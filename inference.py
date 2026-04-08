import os
import json
import re
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is required")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

ENV_URL = os.getenv("ENV_URL", "http://localhost:8000")

# ---------------- LLM CALL ----------------
def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "Return ONLY ONE valid JSON object. No explanations.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


# ---------------- PARSE ----------------
def parse_action(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return {}
    return {}


# ---------------- SANITIZE ----------------
def sanitize_action(action: dict, task_type: str) -> dict:
    if task_type.startswith("classify"):
        return {"label": action.get("label")}
    if task_type.startswith("reply"):
        return {"reply": action.get("reply")}
    if task_type.startswith("triage"):
        return {"priority_order": action.get("priority_order")}
    return {}


# ---------------- EXTRACT REWARD ----------------
def extract_reward(raw_step: dict) -> float:
    """
    Reward may live at different depths depending on create_app() version.
    Walk all candidate locations; return first non-zero value found.
    Fall back to top-level (which may legitimately be 0.0).
    """
    candidates = [
        raw_step.get("reward"),
        (raw_step.get("observation") or {}).get("reward"),
        (raw_step.get("result") or {}).get("reward"),
    ]
    non_zero = [float(c) for c in candidates if c is not None and float(c) != 0.0]
    if non_zero:
        return non_zero[0]
    # All candidates zero or absent — return top-level 0.0
    try:
        return float(raw_step.get("reward", 0.0))
    except (TypeError, ValueError):
        return 0.0


# ---------------- EXTRACT DONE ----------------
def extract_done(raw_step: dict) -> bool:
    for c in [raw_step.get("done"), (raw_step.get("observation") or {}).get("done")]:
        if c is not None:
            return bool(c)
    return False


# ---------------- EXTRACT OBS ----------------
def extract_obs(raw: dict) -> dict:
    if "observation" in raw and isinstance(raw["observation"], dict):
        obs = raw["observation"]
        obs.setdefault("reward", raw.get("reward", 0.0))
        obs.setdefault("done", raw.get("done", False))
        return obs
    return raw


# ---------------- MAIN RUN ----------------
def run_task(task_name: str):
    raw_reset = requests.post(
        f"{ENV_URL}/reset",
        params={"task": task_name}
    ).json()

    obs = extract_obs(raw_reset)

    # Hoist emails for triage if missing after unwrapping
    if task_name.startswith("triage") and not obs.get("emails"):
        emails_from_raw = raw_reset.get("emails") or (raw_reset.get("observation") or {}).get("emails")
        if emails_from_raw:
            obs["emails"] = emails_from_raw

    rewards = []
    print(f"[START] task={task_name} env=email-triage model={MODEL_NAME}")

    for step_num in range(1, 6):
        task_type = obs.get("task", "") or task_name

        if task_type.startswith("classify"):
            prompt = (
                "You are an email classifier.\n"
                "Return ONLY valid JSON.\n"
                "Do NOT include explanations.\n"
                'Format: {"label": "spam"} OR {"label": "urgent"} OR {"label": "normal"}\n'
                f'Email:\nSubject: {obs.get("subject")}\nBody: {obs.get("body")}'
            )

        elif task_type.startswith("reply"):
            prompt = (
                "You are an email assistant.\n"
                "Write a professional reply.\n"
                "Return ONLY JSON.\n"
                "Do NOT return 'label'.\n"
                'Format: {"reply": "<your reply text>"}\n'
                f'Email:\nSubject: {obs.get("subject")}\nBody: {obs.get("body")}'
            )

        elif task_type.startswith("triage"):
            prompt = (
                "You are an email triage system.\n"
                "Sort emails by priority.\n"
                "Return ONLY JSON.\n"
                'Format: {"priority_order": ["A","B","C"]}\n'
                f'Emails:\n{obs.get("emails")}'
            )

        else:
            print(f"[ERROR] Unknown task_type: {task_type}")
            break

        raw = call_llm(prompt)
        parsed = parse_action(raw)
        if task_type.startswith("reply") and "reply" not in parsed:
            parsed = {"reply": "Thanks, noted."}
        if task_type.startswith("triage") and "priority_order" not in parsed:
            parsed = {"priority_order": ["A", "B", "C"]}

        action = sanitize_action(parsed, task_type)
        clean_action = {k: v for k, v in action.items() if v is not None}
        if not clean_action:
            raise ValueError(f"Invalid action generated: {parsed}")

        raw_step = requests.post(
            f"{ENV_URL}/step",
            json={"action": clean_action}
        ).json()

        reward = extract_reward(raw_step)
        done = extract_done(raw_step)

        rewards.append(reward)

        action_str = json.dumps(clean_action, separators=(",", ":"))
        print(
            f"[STEP] step={step_num} action={action_str} "
            f"reward={reward:.2f} done={str(done).lower()} error=null"
        )

        if done:
            break

        obs = extract_obs(raw_step)

    success = any(r > 0 for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={len(rewards)} "
        f"rewards={','.join(f'{r:.2f}' for r in rewards)}"
    )


if __name__ == "__main__":
    for task in ["classify_easy", "reply_medium", "triage_hard"]:
        run_task(task)
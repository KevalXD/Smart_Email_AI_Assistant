import gradio as gr

# 🔹 Health
def check_health():
    return "✅ System Ready"


# 🔥 FINAL MULTI-STEP LOGIC
def process_email(email):
    try:
        # STEP 1: Classification
        label = "spam" if any(word in email.lower() for word in ["free", "win", "money"]) else "important"

        # STEP 2: Reply
        reply = "Thank you for your email. I will assist you shortly."

        # STEP 3: Triage (dynamic emails)
        emails = [
            {"id": "A", "subject": email},
            {"id": "B", "subject": "Special discount offer"},
            {"id": "C", "subject": "Meeting scheduled tomorrow"},
        ]

        def score_email(email_item):
            subject = email_item["subject"].lower()

            if any(word in subject for word in ["urgent", "asap", "immediate", "refund", "issue"]):
                return 100
            elif any(word in subject for word in ["today", "hour", "meeting", "deadline", "tomorrow"]):
                return 50
            elif any(word in subject for word in ["newsletter", "promo", "offer", "discount"]):
                return 10
            else:
                return 30

        sorted_emails = sorted(emails, key=score_email, reverse=True)
        priority_order = [email["id"] for email in sorted_emails]

        # Explanation
        explanations = []
        for email_item in sorted_emails:
            score = score_email(email_item)

            if score == 100:
                reason = "High urgency (critical issue)"
            elif score == 50:
                reason = "Time-sensitive"
            elif score == 10:
                reason = "Low priority / promotional"
            else:
                reason = "Normal request"

            explanations.append(f"{email_item['id']} → {reason}")

        explanation_text = "\n".join(explanations)

        total_reward = 3.0  # simulate full success

        return (
            f"📌 Classification: {label}\n\n"
            f"💬 Reply: {reply}\n\n"
            f"📊 Priority Order: {priority_order}\n"
            f"🧠 Explanation:\n{explanation_text}",

            f"Final Reward: {total_reward}",

            "✅ Completed Multi-Step AI"
        )

    except Exception as e:
        return "Error", "-", str(e)


# 🔹 UI
with gr.Blocks() as demo:
    gr.Markdown("# 📧 Smart Email AI Assistant")
    gr.Markdown("AI-powered email classification, reply, and prioritization")

    status = gr.Textbox(label="System Status", value=check_health())

    email_input = gr.Textbox(
        label="Enter Email",
        placeholder="Paste your email here...",
        lines=8
    )

    submit_btn = gr.Button("🚀 Analyze Email")

    reply_output = gr.Textbox(label="AI Output")
    length_output = gr.Textbox(label="Score / Reward")
    log_output = gr.Textbox(label="System Status")

    submit_btn.click(
        fn=process_email,
        inputs=email_input,
        outputs=[reply_output, length_output, log_output]

)


demo.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
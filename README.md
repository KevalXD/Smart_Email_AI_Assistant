# 🚀 Smart Email AI Assistant

An AI-powered system that intelligently **classifies emails, generates replies, and prioritizes them** based on urgency and context.

---

## 🧠 Overview

Managing emails efficiently is a real-world challenge. This project simulates an **AI-driven email triage system** that:

- 📌 Classifies emails (Important / Normal / Spam)
- 💬 Generates smart replies
- 📊 Prioritizes emails dynamically using keyword-based scoring

---

## ✨ Features

### 🔹 1. Email Classification
- Detects whether an email is:
  - **Important**
  - **Normal**
  - **Spam**

---

### 🔹 2. AI Reply Generation
- Generates context-aware responses
- Keeps replies short and professional

---

### 🔹 3. Dynamic Email Prioritization
Emails are ranked based on:

- 🚨 Urgency keywords (urgent, asap, server down)
- ⏱ Time-sensitive words (meeting, today, deadline)
- 📢 Promotional indicators (newsletter, offer)

---

### 🔹 4. Interactive UI
- Built using **Gradio**
- Simple and clean interface
- Real-time output display

---

## 🛠 Tech Stack

- Python
- Gradio
- Rule-based AI logic (lightweight & efficient)

---

## ⚙️ How It Works

1. User enters an email
2. System:
   - Classifies the email
   - Generates a reply
   - Scores and ranks multiple emails
3. Outputs:
   - Classification
   - AI Reply
   - Priority Order
   - Explanation

---

## 📦 Installation (Local Setup)

```bash
git clone https://github.com/YOUR_USERNAME/Smart_Email_AI_Assistant.git
cd Smart_Email_AI_Assistant
pip install -r requirements.txt
python app.py

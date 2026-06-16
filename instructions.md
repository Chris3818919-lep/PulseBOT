# 🤖 PulseBOT - Installation & Setup Guide

Please read this file carefully before running PulseBOT.

---

# Requirements

Make sure you have the following installed:

- Python 3.10 or newer
- Git (optional)
- A Discord Bot Application
- Internet connection

---

# Required Python Packages

Install the required packages:

```bash
pip install discord.py aiosqlite python-dotenv
```

or

```bash
pip install -r requirements.txt
```

---

# Required Files

Your project folder should contain:

```text
PulseBOT/
│
├── main.py
├── pulse.db
├── .env
├── requirements.txt
├── README.md
├── INSTRUCTIONS.md
└── .gitignore
```

---

# Create a Discord Bot

1. Go to the Discord Developer Portal.
2. Click "New Application".
3. Enter a name.
4. Open the "Bot" tab.
5. Click "Add Bot".

---

# Enable Privileged Intents

In the Bot settings, enable:

✅ Message Content Intent

✅ Server Members Intent

✅ Presence Intent

Save the changes.

---

# Get
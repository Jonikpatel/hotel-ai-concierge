# 🏨 LuxStay AI Concierge

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.20%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Groq AI](https://img.shields.io/badge/Claude_AI-Powered-D97706?style=for-the-badge&logo=anthropic&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**An AI-powered hotel voice concierge system built with Groq AI and Streamlit.**  
Handles check-in, check-out, room service, housekeeping, and guest requests — all via natural voice or text conversation.

[🚀 Quick Start](#-quick-start) • [✨ Features](#-features) • [📁 Structure](#-project-structure) • [🎙️ Voice Guide](#-voice-guide)

</div>

---

## ✨ Features

| Capability | Description |
|---|---|
| 🎙️ **Voice Input** | Speak naturally using Web Speech API — no wake word required |
| 🏨 **Smart Check-In** | AI looks up reservations, assigns rooms, handles early/late requests |
| 🚪 **Express Checkout** | Automated bill summary, payment processing, and key deactivation |
| 🍽️ **Room Service** | Order food, drinks, and amenities via voice with real-time tracking |
| 🛎️ **Concierge** | Local recommendations, restaurant bookings, transport, tours |
| 🧹 **Housekeeping** | Request towels, toiletries, cleaning, turn-down service |
| 🔧 **Maintenance** | Report issues — AC, TV, plumbing — with priority ticketing |
| 💬 **Multilingual** | Claude understands requests in any language |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/hotel-ai-concierge.git
cd hotel-ai-concierge
pip install -r requirements.txt
```

### 2. Set Your Anthropic API Key

```bash
# Option A: Environment variable
export GROQ_API_KEY="gsk_..."

# Option B: Streamlit secrets (recommended for deployment)
echo 'GROQ_API_KEY = "gsk_..."' > .streamlit/secrets.toml
```

> Get your free API key at [console.groq.com](https://console.groq.com)

### 3. Launch

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🎙️ Voice Guide

Click the **🎙️ microphone button** and speak naturally:

| You say... | What happens |
|---|---|
| *"I'd like to check in, reservation under Johnson"* | Finds reservation, assigns room, prints key card info |
| *"Check me out of room 204 please"* | Generates itemised bill, confirms checkout |
| *"Can I get a club sandwich to room 312?"* | Places room service order with ETA |
| *"I need extra pillows and towels"* | Creates housekeeping ticket |
| *"The TV in my room isn't working"* | Logs maintenance request with priority |
| *"What restaurants would you recommend nearby?"* | Curated local recommendations |
| *"Book me a taxi to the airport at 6am"* | Arranges transport with confirmation |

---

## 📁 Project Structure

```
hotel-ai-concierge/
│
├── 📄 app.py                   # Main Streamlit application
│
├── 📂 src/
│   ├── concierge.py            # Groq AI conversation engine
│   ├── hotel_db.py             # Hotel data layer (rooms, guests, orders)
│   ├── services.py             # Service handlers (check-in, checkout, etc.)
│   └── voice_input.py          # Web Speech API Streamlit component
│
├── 📂 data/
│   └── hotel_config.json       # Hotel config, room types, menu, amenities
│
├── 📂 tests/
│   └── test_hotel_db.py        # Unit tests for data layer
│
├── 📂 .streamlit/
│   └── config.toml             # Streamlit theme (luxury dark gold)
│
├── 📂 .github/workflows/
│   └── ci.yml                  # GitHub Actions CI pipeline
│
├── requirements.txt            # App dependencies
└── requirements-dev.txt        # Dev + test dependencies
```

---

## 🏗️ Architecture

```
User (Voice/Text)
       │
       ▼
  Streamlit UI  ──────────────────────────────┐
       │                                      │
       ▼                                      ▼
  Voice Component                    Conversation History
  (Web Speech API)                   (Session State)
       │                                      │
       └──────────────┬───────────────────────┘
                      ▼
              AI Concierge (Claude)
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
     Check-In    Room Service  Concierge
     Check-Out   Housekeeping  Maintenance
          │           │           │
          └───────────┴───────────┘
                      │
                 Hotel Database
              (In-memory / JSON)
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `anthropic` | Groq AI API for natural language understanding |
| Web Speech API | Browser-native voice recognition |
| `pandas` | Guest and reservation data management |
| `pytest` | Unit testing |

---

## 🔐 Deployment

### Streamlit Cloud (Free)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Set **Main file**: `app.py`
4. Add secret: `GROQ_API_KEY = "gsk_..."`
5. Deploy

### Environment Variables
| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Your Anthropic API key |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with 🏨 hospitality and 🤖 intelligence  
</div>

# ⚡ VibePilot: Your AI Agent for Beating Procrastination

![VibePilot Mascot](vibepilot_mascot.png)

## 🎯 Project Overview
VibePilot is an AI-powered productivity agent designed to solve the "procrastination trap." Unlike traditional static to-do lists, VibePilot uses an intelligent agentic architecture to reason about your tasks, understand your personal work style, and dynamically structure your day for optimal flow.

---

## 🚀 Key Features
* **Dynamic Task Scheduling:** The agent doesn't just list tasks; it reorders and prioritizes them based on your goals.
* **AI-Powered Insights:** Uses **Gemini** to analyze your procrastination habits and provide actionable nudges.
* **Streamlined UI:** Built with Streamlit for a fast, focused, and "vibe-centric" user experience.

---

## 🏗️ Architecture
VibePilot follows a modular agentic design:
1. **User Interface:** Streamlit dashboard for task input and interaction.
2. **Reasoning Engine:** Gemini acts as the core agent, processing user input and planning the day.
3. **Task Logic:** Python-based handler that manages the state of tasks and persistence.

```
┌───────────┐      Input      ┌───────────┐
│           │ ──────────────> │           │
│   User    │                 │ Streamlit │
│           │ <────────────── │    UI     │
└───────────┘     Render      └───────────┘
                                    │
                                    │ Request
                                    ▼
                              ┌───────────┐
                              │  Gemini   │
                              │ AI Model  │
                              └───────────┘
```

---

## 🛠️ Concepts Applied (Kaggle AI Agents Course)
* **Agent System Design:** Implemented a multi-step reasoning flow to prioritize tasks.
* **Tool Use:** Effectively utilized Gemini's function-calling capabilities to structure task output.
* **Deployability:** Designed with a Docker-first approach for easy containerization.

---

## ⚡ Quick Start (Local Setup)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/VibePilot.git
cd VibePilot
```

### 2. Set Up a Virtual Environment
Create and activate a virtual environment to keep your packages isolated:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration (Secrets)
Create or edit `.streamlit/secrets.toml` in your project root directory and insert your Google Gemini API key:
```toml
GEMINI_API_KEY = "your-api-key-here"
```

### 5. Run the Project
Launch the Streamlit web server:
```bash
streamlit run app.py
```
Then navigate to `http://localhost:8501` in your browser.

---

## 🐳 Docker Setup

To run inside a container:
```bash
# Build the image
docker build -t vibepilot-focus-protocol .

# Run the container
docker run -p 8080:8080 vibepilot-focus-protocol
```
Open `http://localhost:8080` in your web browser.

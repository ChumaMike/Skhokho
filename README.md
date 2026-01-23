# SKHOKHO.SYS // Life Operating System

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![OpenAI](https://img.shields.io/badge/AI-Powered-412991?style=for-the-badge&logo=openai&logoColor=white)
![Status](https://img.shields.io/badge/System-Operational-green?style=for-the-badge)

**Skhokho** is an enterprise-grade personal management platform (LifeOS) engineered for the South African context. It integrates financial calculations, network relationship management (CRM), strategic goal tracking, and local environmental telemetry into a single, high-performance command center.

The system features **Skhokho AI**, an integrated chatbot companion that assesses user well-being, provides life strategy, and acts as a daily accountability partner.

---

## 📸 System Interface

*(Add screenshots here. For example: `![Dashboard Screenshot](docs/dashboard.png)`)*

---

## ⚡ Core Modules

### 1. 🤖 Skhokho AI Companion (NEW)
A conversational intelligence engine designed to be your daily architect:
* **Well-being Assessment:** Daily check-ins to track mental state and energy levels.
* **Strategic Advisor:** Provides tailored "Life Hacks" and tips based on your current goals and challenges.
* **Conversational Interface:** A chat-based UI for venting, brainstorming, or getting quick advice.

### 2. 🎛️ Command Center (Dashboard)
A centralized HUD providing real-time intelligence:
* **Environmental Telemetry:** Integration with OpenWeatherMap for local forecasts.
* **Grid Status:** Real-time Load Shedding stage updates via EskomSePush API.
* **Priority Queue:** Top 3 active strategic goals sorted by completion status.
* **Network Alerts:** Automated "Red Flags" for contacts neglected for >30 days.

### 3. 🚕 Balaa Financial Engine
A specialized arithmetic engine for the South African taxi industry:
* Calculates fare distribution for groups.
* Tracks expected vs. received totals.
* Computes change variance.
* Maintains a transactional history log.

### 4. 🎯 Strategic Goal Tracker
A project management system for personal ambition:
* Create high-level objectives (e.g., "Career", "Finance").
* Break down objectives into executable milestones.
* Visual progress bars powered by real-time completion logic.

### 5. 🤝 Network Intelligence (CRM)
A "Personal Rolodex" to manage social capital:
* Track professional and personal contacts.
* Log interactions (Calls, Meetings, Emails).
* **Cold Contact Algorithm:** Automatically flags contacts that haven't been engaged in 30 days.

---

## 🏗️ Architecture

The application follows a **Service-Repository Pattern** to ensure scalability and separation of concerns:

```text
app/
├── routes/          # Logic Controllers (Blueprints)
│   ├── auth.py      # Security & Session Management
│   ├── chat.py      # Skhokho AI Logic
│   ├── crm.py       # Network Logic
│   ├── goals.py     # Strategy Engine
│   └── tools.py     # Utilities (Balaa/Diary)
├── services/        # External API Integrations
│   ├── ai_service.py # OpenAI / LLM Integration
│   ├── eskom.py     # Load Shedding Service
│   └── weather.py   # Weather Service
├── models.py        # SQLAlchemy Database Schema
└── templates/       # Jinja2 UI (Tailwind CSS)
🛠️ Installation & Setup
Prerequisites
Python 3.10+

API Keys (OpenWeatherMap, EskomSePush, OpenAI)

1. Clone the Repository
Bash

git clone [https://github.com/yourusername/skhokho.git](https://github.com/yourusername/skhokho.git)
cd skhokho
2. Initialize Environment
Bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
3. Configure Variables
Create a .env file in the root directory:

Ini, TOML

FLASK_APP=run.py
FLASK_DEBUG=1
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///skhokho.db
WEATHER_API_KEY=your_key_here
ESKOM_API_TOKEN=your_token_here
OPENAI_API_KEY=your_openai_key_here
4. Database Migration
Initialize the SQLite database schema:

Bash

flask db upgrade
5. Launch System
Bash

flask run
Access the terminal at http://127.0.0.1:5000

🧪 Testing & Quality Assurance
Skhokho maintains a rigorous testing suite using pytest, covering authentication, math logic, and security edge cases.

To execute the test suite:

Bash

pytest
To generate a coverage report:

Bash

pytest --cov=app
🛡️ License
Distributed under the MIT License. See LICENSE for more information.

Engineer: Chuma Meyiswa Version: 2.1.0 (AI Update)

13
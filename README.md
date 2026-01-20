# SKHOKHO.SYS // Life Operating System

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Status](https://img.shields.io/badge/System-Operational-green?style=for-the-badge)
![Coverage](https://img.shields.io/badge/Test_Coverage-100%25-success?style=for-the-badge)

**Skhokho** is an enterprise-grade personal management platform (LifeOS) engineered for the South African context. It integrates financial calculations, network relationship management (CRM), strategic goal tracking, and local environmental telemetry into a single, high-performance command center.

Designed with a modular **Model-View-Controller (MVC)** architecture and a privacy-first philosophy.

---

## 📸 System Interface

*(Add screenshots here. For example: `![Dashboard Screenshot](docs/dashboard.png)`)*

---

## ⚡ Core Modules

### 1. Command Center (Dashboard)
A centralized HUD providing real-time intelligence:
* **Environmental Telemetry:** Integration with OpenWeatherMap for local forecasts.
* **Grid Status:** Real-time Load Shedding stage updates via EskomSePush API.
* **Priority Queue:** Top 3 active strategic goals sorted by completion status.
* **Network Alerts:** Automated "Red Flags" for contacts neglected for >30 days.

### 2. Balaa Financial Engine
A specialized arithmetic engine for the South African taxi industry:
* Calculates fare distribution for groups.
* Tracks expected vs. received totals.
* Computes change variance.
* Maintains a transactional history log.

### 3. Strategic Goal Tracker
A project management system for personal ambition:
* Create high-level objectives (e.g., "Career", "Finance").
* Break down objectives into executable milestones.
* Visual progress bars powered by real-time completion logic.

### 4. Network Intelligence (CRM)
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
│   ├── crm.py       # Network Logic
│   ├── goals.py     # Strategy Engine
│   └── tools.py     # Utilities (Balaa/Diary)
├── services/        # External API Integrations
│   ├── eskom.py     # Load Shedding Service
│   └── weather.py   # Weather Service
├── models.py        # SQLAlchemy Database Schema
└── templates/       # Jinja2 UI (Tailwind CSS)
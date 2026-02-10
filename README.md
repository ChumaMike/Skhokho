# Skhokho

**Skhokho is not just an app; it is a feedback loop ecosystem.**

A community-focused super app that connects economic activity, civic engagement, and accessibility into one unified platform for South African townships.

## 🌍 The Ecosystem

Skhokho operates on **three interconnected loops**:

### 1. 💰 Economic Loop
Users earn money in **LinkUp** → Track/Budget it in **Skhokho Dashboard** → Spend it on Goals/Services

### 2. 🏛️ Civic Loop  
Users report data in **CivicNerve** → Earn Reputation Points → Get trusted status/discounts in **LinkUp**

### 3. 🦯 Accessibility Layer
**Macalaa** sits on top of everything, ensuring blind/disabled users can participate in both loops equally

📖 **[Read the Complete Ecosystem Overview](ECOSYSTEM_OVERVIEW.md)**

---

## ✨ Core Features

### 🏠 Skhokho Dashboard (Command Center)
- **AI Chatbot with Database Write Access**: Natural language commands that execute real actions
  - "Add a goal to save R5000 for a laptop" → Creates goal in database
  - "I met a great plumber, add him to my network" → Saves contact
  - "Alert me if my budget drops below R200" → Sets budget alert
- **Wallet & Reputation Tracking**: Real-time balance and reputation points
- **Baala Calculator Integration**: Taxi fare splitting via chat
- **Context-Aware**: Knows your goals, contacts, and financial status

### 🤝 LinkUp (The Marketplace)
- **Dual-Role Identity**: Users can be both service providers AND customers
- **Interactive Map**: Real-time geospatial view of services and civic issues
- **Escrow System**: Secure payment holding until job completion
- **Rating & Reviews**: 1-5 star ratings for both providers and customers
- **Verified Badges**: Earned through reputation (50+ points)

### 👁️ CivicNerve (The City Agent)
- **AI Vision Analysis**: Google Gemini analyzes photos of civic issues
- **Auto-Categorization**: AI determines issue type and severity (0-100)
- **Community Voting**: Upvote system prioritizes urgent issues
- **Reputation Rewards**: Earn points for verified reports
- **Status Tracking**: Real-time updates from Reported → Resolved

### 🦯 Macalaa (Visual & Voice Assistant)
- **Voice Navigation**: Full app control via voice commands
  - "Macalaa, hire a plumber" → Opens LinkUp with plumber filter
  - "Check my balance" → Reads wallet and reputation
- **Environment Scanning**: AI describes surroundings from camera
- **Danger Detection**: Auto-detects hazards and warns users urgently
- **Auto-Reporting**: Dangers automatically reported to CivicNerve
- **Location Narration**: Describes nearby services and safety warnings

### 🛠️ Tools
- **Diary**: Personal journal with AI-powered insights
- **Baala Calculator**: Taxi fare splitting and payment tracking
- **Goals**: Mission tracking with progress visualization
- **Network (CRM)**: Professional and personal contact management

## Requirements

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-Migrate
- psycopg2-binary (for PostgreSQL)
- python-dotenv
- requests
- google-generativeai (or google.genai)
- pillow
- geoalchemy2
- flask-limiter
- flask-talisman
- flask-wtf
- email_validator

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ChumaMike/Skhokho.git
   cd Skhokho
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   - Copy `.env.example` to `.env` (if exists)
   - Or create a new `.env` file with the following content:
     ```
     FLASK_APP=run.py
     FLASK_DEBUG=1
     SECRET_KEY=dev-key-change-this-in-prod
     DATABASE_URL=sqlite:///skhokho.db
     WEATHER_API_KEY=your_weather_api_key
     NEWSAPI_KEY=your_news_api_key
     ESKOM_API_TOKEN=your_eskom_token
     GOOGLE_API_KEY=your_google_api_key
     SKHOKHO_CLIENT_SECRET=your_secret_key
     GEMINI_API_KEY=your_gemini_api_key
     ```

5. **Initialize the database**:
   ```bash
   python init_db.py
   python seed_demo.py  # Optional: Adds demo data
   ```

## Running the App

### Development Server

```bash
python run.py --port 5000 --host 0.0.0.0
```

The app will be available at `http://localhost:5000/`

### Docker

```bash
docker-compose up
```

## Usage

### Accessing the App

1. Open your browser and navigate to `http://localhost:5000/`
2. Register a new account or log in with existing credentials
3. Explore the various features:
   - **Goals**: Click on "Goals" in the navigation to set and track your goals
   - **Network**: Manage your contacts under "Network"
   - **Tools**: Access Balaa (fare calculator) and Diary (journal) under "Tools"
   - **LinkUp**: Find local service providers on the map
   - **Macalaa AI**: Chat with the AI assistant
   - **Civic**: Report and view civic issues

### Demo User

If you ran `seed_demo.py`, you can log in with:
- Username: `citizen_one`
- Password: `demo`

## Testing

To run the tests:

```bash
pytest tests/
```

## Architecture

- **Flask** - Web framework
- **SQLite/PostgreSQL** - Database
- **Flask-SQLAlchemy** - ORM
- **Flask-Login** - Authentication
- **Google Generative AI (Gemini)** - AI chat functionality
- **Leaflet** - Map visualization for LinkUp
- **Font Awesome** - Icons

## Project Structure

```
Skhokho/
├── app/
│   ├── __init__.py       # App initialization
│   ├── extensions.py     # Flask extensions (db, login_manager, etc.)
│   ├── models.py         # Database models
│   ├── routes/           # Blueprint routes
│   ├── services/         # Business logic and external API integration
│   ├── static/           # Static files (CSS, JavaScript, images)
│   └── templates/        # HTML templates
├── tests/                # Test files
├── .env                  # Environment variables
├── config.py             # App configuration
├── docker-compose.yml    # Docker configuration
├── Dockerfile            # Dockerfile
├── init_db.py            # Database initialization script
├── requirements.txt      # Python dependencies
├── run.py                # App entry point
└── seed_demo.py          # Demo data seeding script
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes and commit them
4. Push to your fork and create a pull request

## License

MIT License

## Contact

For questions or support, please contact [Chuma Mike](https://github.com/ChumaMike)
# Skhokho — Your Personal Life Helper 🌟

**Skhokho** is a smart, lightweight Flask-based app designed to simplify your daily life. Whether you're splitting a taxi fare, journaling your thoughts, or staying on top of local updates, Skhokho has your back — all while keeping your data private and offline using SQLite.

---

## 🚀 Features

### 🧮 1. Balaa — Taxi Money Calculator 🚕  
- Easily split taxi fares among multiple passengers  
- Enter the fare, group size, and each passenger’s contribution  
- Automatically calculate total expected, received amount, and change  
- View past calculations saved securely under your account  

### 📔 2. Diary — Personal Journal  
- Create entries like Notes, Feelings, To-Dos, Needs, and Wants  
- Timestamped entries organized by date for easy browsing  
- All entries are saved privately per user  

### 🔐 3. User Authentication  
- Secure registration and login system  
- User-separated data ensures full privacy  
- Passwords are safely hashed  

### 📍 4. Weekly Snapshot / Local Update  
- Get updates based on your selected location, including:  
  - Weather forecast 🌤️  
  - Load-shedding schedule 🔌  
  - Local events or tips 🗓️  

### 🤖 5. AI Bot Assistant (Upcoming)  
- Friendly chatbot that helps with tasks and guides app usage  
- Uses local or cloud-based AI (privacy-focused option in development)  
- Always refers to you as *skhokho* for a personalized vibe  

---

## 🛠️ Technology Stack

- **Backend:** Python & Flask  
- **Frontend:** HTML, CSS, Jinja2 Templates  
- **Database:** SQLite (offline-first, local storage)  
- **User Auth:** Flask-Login  
- **APIs:** Weather API, EskomSePush (for load-shedding), OpenAI (optional)

---

## ⚙️ Installation & Setup

1. Clone the repo:
   git clone https://github.com/ChumaMike/skhokho.git
   cd skhokho

2. Create and activate a Python virtual environment         (optional but recommended):

    python3 -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows

3. Install dependencies:

    pip install -r requirements.txt

4. Run the application:

    python app.py

5. Open your browser and go to http://localhost:5000 to use Skhokho.

## 📌 Usage Notes

- All data is stored locally in `skhokho.db` using SQLite. No internet connection is required to use the app.
- Your data is private and separated by user accounts.
- Use the Balaa feature to quickly calculate shared taxi fares.
- Use the Diary to jot down notes, feelings, tasks, and more.

## 🌱 Future Features (Planned)

- To-Do list and task manager
- Expense tracking and budgeting
- Habit tracker
- Data export/import for backup
- Offline AI assistant chatbot
- Daily motivational quotes
- Dark mode and UI customization
- Reminders and local notifications

## 🤝 Contributing & Vibe Coding

I'm vibe coding most parts of Skhokho with ChatGPT’s help.
Contributions and suggestions are always welcome!

To contribute:

Fork the repository

Create a branch (git checkout -b feature/your-feature)

Commit changes and push

Open a pull request 💬

## 📄 License

MIT License

## 📫 Contact

Created with ❤️ by Chuma Mike.
Email: nmeyiswa@gmail.com
Or open an issue here on GitHub.
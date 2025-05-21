# Skhokho — Your Personal Life Helper 🌟

Skhokho is a smart, lightweight Flask-based app designed to simplify your daily life. Whether on your phone or desktop, Skhokho helps you manage everyday tasks, finances, and personal reflections — all while keeping your data private and offline using SQLite.

---

## 🚀 Features

### 1. Balaa — Taxi Money Calculator 🚕  
- Easily split taxi fares among multiple passengers  
- Enter the fare, group size, and each passenger’s contribution  
- Automatically calculate total expected, received amount, and change  
- View your past calculations saved securely under your account  

### 2. Diary — Personal Journal 📔  
- Create diverse diary entries: Notes, Feelings, To-Dos, Needs, Wants, and more  
- Timestamped entries organized by date for easy browsing  
- All entries are saved privately to your user account  

### 3. User Authentication 🔐  
- Secure user registration and login system  
- Data is separated per user to ensure privacy  
- Passwords are safely hashed for security  

---

## 🛠 Technology Stack

- **Python** and **Flask** web framework  
- **SQLite** database for local, offline data storage  
- **Flask-Login** for user session management  
- **Jinja2** templates for rendering responsive views  

---

## ⚙️ Installation & Setup

1. Clone the repo:
   git clone https://github.com/ChumaMike/skhokho.git
   cd skhokho

2. Create and activate a Python virtual environment         (optional but recommended):

    python3 -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows

3. nstall dependencies:

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

I will be vibe coding most parts of Skhokho with ChatGPT’s help. Contributions and suggestions are welcome!

## 📄 License

MIT License

## 📫 Contact

For any questions or suggestions, please open an issue or contact me at nmeyiswa@gmail.com
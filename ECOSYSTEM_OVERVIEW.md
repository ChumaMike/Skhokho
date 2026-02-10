# Skhokho Ecosystem Overview

## 🌍 The Complete Feedback Loop System

Skhokho is not just an app; it is a **feedback loop ecosystem** that connects economic activity, civic engagement, and accessibility into one unified platform.

---

## 🔄 The Three Core Loops

### 1. **Economic Loop** 💰
**Flow:** Users earn money in LinkUp → Track/Budget it in Skhokho Dashboard → Spend it on Goals/Services

- **LinkUp Marketplace**: Gig economy where users can be both service providers AND customers
- **Wallet System**: Real-time balance tracking integrated with all transactions
- **Escrow Protection**: Payments held until job completion
- **Reputation System**: Points earned through good work and civic participation

### 2. **Civic Loop** 🏛️
**Flow:** Users report data in CivicNerve → Earn Reputation Points → Get trusted status/discounts in LinkUp

- **CivicNerve Reporting**: AI-powered civic issue reporting with photo evidence
- **Reputation Rewards**: Users earn points for verified reports
- **Community Voting**: Upvote system prioritizes urgent issues
- **Status Tracking**: Real-time updates on issue resolution

### 3. **Accessibility Layer** 🦯
**Flow:** Macalaa sits on top of everything, ensuring blind/disabled users can participate in both loops equally

- **Voice Navigation**: Full app control via voice commands
- **Environment Scanning**: AI vision describes surroundings
- **Danger Detection**: Auto-reports hazards to CivicNerve
- **Audio Narration**: Speaks location details and warnings

---

## 🏠 1. Skhokho Dashboard (The Command Center)

### Role
The financial and personal HQ where users manage their entire digital life.

### Key Feature: "Skhokho" - The System Chatbot
This isn't just a FAQ bot; it has **"Write Access"** to the database.

#### Chatbot Capabilities (Natural Language Actions)

**Goal Management:**
```
User: "Add a goal to save R5000 for a laptop."
Bot: ✅ Sharp! I've added 'Save R5000 for laptop' to your mission board.
```

**Network Management:**
```
User: "I just met a great plumber, add him to my network."
Bot: ✅ Ayt, I saved [Name] (Plumber) to your network.
```

**Budget Alerts:**
```
User: "Alert me if my budget drops below R200."
Bot: ✅ Alert set! I'll notify you when your balance drops below R200.
```

**Diary Logging:**
```
User: "Log a diary entry: Paid rent today."
Bot: ✅ Diary entry saved. Type: Expense
```

**Baala Calculator:**
```
User: "Calculate taxi fare: R15 for 4 people."
Bot: 🚖 Baala Calc: R15 ÷ 4 people = R3.75 each
```

### Dashboard Components

#### Wallet Card
- Large, clear balance display (Rands)
- Reputation Badge showing points
- Transaction history

#### Quick Links
- Icons for Diary, Baala Calculator, Goals, Network
- One-click access to all tools

#### Chat Interface
- Floating or side-panel chat window
- Always accessible from any page
- Context-aware (knows your goals, contacts, balance)

---

## 🤝 2. LinkUp (The Marketplace)

### Role
The engine of the gig economy - connecting service providers with customers.

### Key Feature: Dual-Role Identity
Users are not "Drivers" OR "Riders". They are **Citizens who can be both**.

### The Map (Leaflet.js)
- Real-time view of verified providers nearby
- Filters: "Show me Plumbers" vs "Show me Tutors"
- Geospatial search with radius control
- Displays both services AND civic issues

### User Profiles
- **Toggle Switch**: "Buying Mode" vs "Selling Mode"
- **Verified Badge**: Only appears if `reputation_points > 50`
- **Rating Display**: Average rating from completed jobs
- **Service Categories**: Plumbing, Electrical, Tutoring, etc.

### Workflow

#### 1. Discovery
- Locate services on map
- View provider profile and ratings
- Check pricing and availability

#### 2. Hiring
- "Hire Now" button triggers escrow hold
- Funds deducted from customer wallet
- Job status: `Pending`

#### 3. Execution
- Provider accepts: Status → `In_Progress`
- Real-time chat between parties
- Location tracking (optional)

#### 4. Completion
- Customer marks complete via QR code scan or button
- Status → `Completed`
- Escrow releases funds to provider
- Status → `Paid`

#### 5. Review
- Both parties can rate each other (1-5 stars)
- Comments optional
- Reputation points updated

### Escrow System
```python
# On Hire:
customer.wallet_balance -= job.agreed_price
# Funds held in escrow

# On Completion:
provider.wallet_balance += job.agreed_price
job.is_paid = True
# Transaction recorded
```

---

## 👁️ 3. CivicNerve (The City Agent)

### Role
The eyes of the city - an "Agentic" system that creates verified data from chaos.

### Key Feature: AI Vision Analysis
Uses Google Gemini Vision API to analyze civic issues from photos.

### The Input
A camera interface specifically for reporting civic issues.

### The AI Agent Process

#### 1. Capture
User takes photo of a burst pipe, pothole, broken light, etc.

#### 2. Analyze
AI scans image and extracts:
- **Category**: "Water Infrastructure", "Road Damage", "Electrical"
- **Severity**: 0-100 score (Critical, High, Medium, Low)
- **Location**: GPS coordinates matched with image
- **Description**: Auto-generated detailed description

#### 3. Report
Auto-generates a structured report:
```json
{
  "title": "Burst Water Pipe on Main Street",
  "description": "AI-detected water infrastructure failure...",
  "category": "Water Infrastructure",
  "severity": 95,
  "latitude": -26.2309,
  "longitude": 27.8596,
  "image_url": "/uploads/scan_123.jpg",
  "guardian_seal": "sha256_hash_for_tamper_proof"
}
```

#### 4. Reward
If the report is verified (by AI confidence score > 70):
- User gets +50 Reputation Points
- Report appears on map for all users
- Nearby users receive proximity warnings

### City Dashboard (Future Prep)
The system generates a "Ticket" ID that allows the city to:
- View all reports on admin dashboard
- Dispatch crews to locations
- Allocate budget for repairs
- Update status: `Reported` → `Under_Review` → `In_Progress` → `Resolved`

### Community Voting
- Users can upvote issues (one vote per user)
- Most-voted issues get priority
- Voting increases reporter's reputation

---

## 🦯 4. Macalaa (The Visual & Voice Assistant)

### Role
The bridge for the disabled - it "sees" and "speaks" the app.

### Key Feature: Environment Scanning & Danger Detection

### Voice Navigation
```
User: "Macalaa, hire a plumber."
Macalaa: "I found 3 plumbers nearby. Opening LinkUp map..."
[Executes navigation to LinkUp with plumber filter]
```

**Supported Commands:**
- "Check my balance" → Reads wallet balance and reputation
- "Show my goals" → Lists active goals
- "Open the map" → Navigates to LinkUp map
- "Report an issue" → Opens CivicNerve reporting
- "Hire a [service]" → Searches for service providers

### Environment Mode (Camera)

#### Normal Scanning
```
User points camera at street.
Macalaa: "You are on Vilakazi Street. There is a cafe to your left. 
          A hardware store is 50 meters ahead."
```

#### Danger Detection Loop

**If Macalaa sees an open manhole/danger:**

**Action 1: Urgent Voice Warning**
```
Macalaa: "⚠️ STOP! DANGER DETECTED! Open manhole 2 meters ahead!"
[Speaks with increased rate and pitch for urgency]
```

**Action 2: Auto-triggers CivicNerve**
- Takes snapshot automatically
- Logs a "Danger" report with severity 95
- Alerts nearby users via push notification (future)
- Marks location on map with red danger icon

### Location Narration
```
User: "Where am I?"
Macalaa: "You are at coordinates -26.2309, 27.8596. 
          Nearby services: Kasi Electrician, Soweto Plumbing. 
          ⚠️ Warning: 1 reported civic issue in this area. 
          High severity: Open manhole on Main Street."
```

### Accessibility Features
- **Screen Reader Compatible**: Proper ARIA labels
- **High Contrast Mode**: Visual accessibility
- **Keyboard Navigation**: Full app usable without mouse
- **Text-to-Speech**: All content can be read aloud
- **Speech-to-Text**: Voice input for all forms

---

## 🔗 Integration Points

### How the Loops Connect

#### Economic → Civic
1. User completes job in LinkUp (+R50 earned)
2. User reports pothole via CivicNerve (+50 reputation)
3. Higher reputation = Verified Badge in LinkUp
4. Verified Badge = More job opportunities
5. More jobs = More income

#### Civic → Economic
1. User has 150 reputation points
2. Gets "Trusted Citizen" badge
3. Receives 10% discount on LinkUp services
4. Can charge premium rates as provider

#### Accessibility → Both
1. Blind user uses Macalaa voice commands
2. "Hire a plumber" → LinkUp transaction
3. Macalaa detects danger → CivicNerve report
4. User earns reputation → Better LinkUp status
5. Full participation in both loops

---

## 🗄️ Database Schema

### Core Models

#### User
```python
- id, username, email, password_hash
- wallet_balance (Integer, default=0)
- reputation_points (Integer, default=0)
- role (citizen, provider, official)
```

#### Service
```python
- id, name, description, category
- latitude, longitude
- provider_id (FK to User)
- price
```

#### Job
```python
- id, service_id, client_id, provider_id
- status (Pending, In_Progress, Completed, Paid, Disputed)
- agreed_price
- is_paid (Boolean)
- started_at, completed_at, paid_at
```

#### CivicIssue
```python
- id, title, description, category
- latitude, longitude
- ai_severity_score (0-100)
- city_status (Reported, Under_Review, In_Progress, Resolved)
- image_url
- reporter_id (FK to User)
- upvote_count
```

#### Goal
```python
- id, user_id, title, description
- is_completed (Boolean)
```

#### NetworkContact
```python
- id, user_id, name, role, phone, email
```

#### DiaryEntry
```python
- id, user_id, entry_type, content
- created_at
```

#### ChatLog
```python
- id, user_id, message, response
- created_at
```

#### MacalaaLog
```python
- id, user_id, query, response, query_type
- created_at
```

---

## 🚀 API Endpoints

### Chat/AI
- `POST /chat/send` - Send message to Skhokho chatbot (with DB write access)

### Macalaa
- `POST /macalaa/api/macalaa/voice` - Voice command execution
- `POST /macalaa/api/macalaa/scan-environment` - Environment scanning with danger detection
- `POST /macalaa/api/macalaa/navigate` - Location narration

### LinkUp
- `GET /linkup/map` - Interactive map view
- `POST /linkup/hire/<service_id>` - Hire a service provider
- `POST /linkup/complete/<job_id>` - Mark job as complete
- `POST /linkup/rate/<job_id>` - Rate completed job

### CivicNerve
- `POST /civic/report` - Report new civic issue
- `GET /civic/dashboard` - View all civic issues
- `POST /civic/issue/<id>/upvote` - Upvote an issue

### Tools
- `GET /tools/diary` - Diary interface
- `POST /tools/diary/entry` - Create diary entry
- `GET /tools/balaa` - Baala calculator

---

## 🎯 User Journeys

### Journey 1: The Gig Worker
1. **Morning**: Opens Skhokho Dashboard, sees R150 balance
2. **Discovery**: Checks LinkUp map for nearby jobs
3. **Work**: Accepts plumbing job, earns R200
4. **Civic**: Reports broken streetlight on way home (+50 reputation)
5. **Evening**: Balance now R350, reputation 150 points
6. **Result**: Unlocks "Trusted Provider" badge

### Journey 2: The Blind User
1. **Voice**: "Macalaa, check my balance"
2. **Response**: "Your balance is R150. Reputation: 100 points."
3. **Navigation**: "Macalaa, hire a plumber"
4. **Action**: Macalaa opens LinkUp, reads available plumbers
5. **Danger**: Walking, Macalaa detects open manhole
6. **Alert**: "STOP! DANGER! Open manhole ahead!"
7. **Auto-Report**: CivicNerve report auto-generated
8. **Result**: User safe, community warned, reputation +50

### Journey 3: The Community Activist
1. **Reporting**: Takes photo of pothole
2. **AI Analysis**: Severity 85, auto-categorized
3. **Community**: Other users upvote (15 votes)
4. **City**: Issue marked "In_Progress"
5. **Resolution**: Fixed within 2 weeks
6. **Reward**: +100 reputation for high-impact report
7. **Benefit**: Verified badge in LinkUp, more job offers

---

## 🔐 Security & Privacy

### Data Protection
- Passwords hashed with Werkzeug
- CSRF protection on all forms
- SQL injection prevention via SQLAlchemy ORM
- File upload validation and sanitization

### Location Privacy
- GPS coordinates only stored with explicit consent
- Users can disable location tracking
- Civic reports can be anonymous

### AI Safety
- Image analysis respects privacy
- No facial recognition
- Guardian seal prevents report tampering

---

## 📊 Success Metrics

### Economic Loop
- Total transactions processed
- Average job completion time
- Provider earnings growth
- Customer satisfaction ratings

### Civic Loop
- Issues reported per month
- Average resolution time
- Community engagement (upvotes)
- Reputation points distributed

### Accessibility
- Voice command usage rate
- Danger detections prevented
- Blind/disabled user retention
- Accessibility feature adoption

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **ORM**: SQLAlchemy
- **Auth**: Flask-Login

### Frontend
- **Templates**: Jinja2
- **Styling**: Tailwind CSS
- **Icons**: Font Awesome
- **Maps**: Leaflet.js

### AI/ML
- **Vision**: Google Gemini Flash (gemini-flash-latest)
- **NLP**: Google Gemini for chatbot
- **Voice**: Web Speech API (browser-native)

### Infrastructure
- **Deployment**: Docker
- **File Storage**: Local filesystem (uploads/)
- **Session**: Flask sessions

---

## 🌟 Future Enhancements

### Phase 2
- [ ] Real-time notifications (WebSockets)
- [ ] Payment gateway integration (Stripe/PayFast)
- [ ] Advanced escrow with dispute resolution
- [ ] City official dashboard
- [ ] Mobile app (React Native)

### Phase 3
- [ ] Machine learning for fraud detection
- [ ] Predictive civic issue mapping
- [ ] Multi-language support (Zulu, Xhosa, Sotho)
- [ ] Blockchain for tamper-proof civic records
- [ ] Integration with municipal systems

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👥 Contributing

We welcome contributions! See CONTRIBUTING.md for guidelines.

---

## 📞 Support

- **Email**: support@skhokho.co.za
- **GitHub**: https://github.com/ChumaMike/Skhokho
- **Docs**: https://docs.skhokho.co.za

---

**Built with ❤️ in Soweto, South Africa**

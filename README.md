# 🌍 Plan-IT — AI-Powered Travel Planner

Plan-IT is a full-stack travel planning application that uses AI agents to generate personalized, day-by-day trip itineraries. Fill a simple form, and get a complete plan with destinations, timings, budget breakdowns, and local tips — all in seconds.

---

## ✨ Features

- **AI-Powered Itineraries** — Multi-agent pipeline (Planner, Budget, Geo, Itinerary, Expert) powered by Groq / Gemini LLMs
- **Smart Trip Form** — Structured inputs for destination, dates, budget, travel style & interests
- **Real-Time Chat** — Conversational interface with session-based memory
- **Authentication** — Email/password signup & login with MongoDB Atlas + bcrypt, plus **Google Sign-In** via Firebase
- **Persistent Sessions** — Stay logged in across page refreshes (localStorage)
- **Modern UI** — Glassmorphism design with Carbon Design System components and micro-animations
- **RAG Pipeline** — Retrieval-Augmented Generation with ChromaDB for enhanced destination knowledge

---

## 🏗️ Tech Stack

| Layer        | Technology                                              |
| ------------ | ------------------------------------------------------- |
| **Frontend** | React 19, Vite, Carbon Design System, Firebase Auth     |
| **Backend**  | Flask, Python 3, Flask-CORS                             |
| **AI/LLM**   | Groq (Llama 3.3 70B), Google Gemini 2.0 Flash           |
| **Database** | MongoDB Atlas (pymongo + bcrypt)                        |
| **RAG**      | ChromaDB, Sentence Transformers                         |

---

## 📁 Project Structure

```
PlanIT/
├── Frontend/                  # React + Vite app
│   ├── src/
│   │   ├── components/        # Login, Signup, Header, TripPlanner, ChatBox, etc.
│   │   ├── services/api.js    # API client (auth, sessions, chat, plan)
│   │   ├── firebase.js        # Firebase config & Google auth provider
│   │   ├── App.jsx            # Main app with routing & auth state
│   │   └── App.css            # Global styles
│   ├── package.json
│   └── vite.config.js         # Dev proxy → backend :8000
│
├── Backend/                   # Flask API + AI agents
│   ├── api/main.py            # Flask routes (auth, chat, plan, sessions)
│   ├── auth.py                # MongoDB auth (signup, login, Google upsert)
│   ├── config.py              # Pydantic settings from .env
│   ├── llm_client.py          # Multi-provider LLM client
│   ├── agents/                # AI agent modules
│   │   ├── planner_agent.py   # Orchestrator agent
│   │   ├── budget_agent.py    # Budget analysis
│   │   ├── geo_agent.py       # Geographic/location data
│   │   ├── itinerary_agent.py # Day-by-day plan generation
│   │   ├── expert_agent.py    # Travel expertise
│   │   ├── preference_agent.py# User preference extraction
│   │   ├── react_agent.py     # ReAct reasoning agent
│   │   └── tools.py           # Agent tool definitions
│   ├── memory/                # Session management
│   ├── rag/                   # RAG pipeline (ChromaDB)
│   ├── requirements.txt
│   └── .env                   # API keys & config (not committed)
│
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.10
- **MongoDB Atlas** account (free tier works)
- **Groq** or **Google Gemini** API key

### 1. Clone the Repository

```bash
git clone https://github.com/Rudranshhhhh/PlanIT.git
cd PlanIT
```

### 2. Backend Setup

```bash
cd Backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file in `Backend/`:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile

GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash

MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/

API_HOST=127.0.0.1
API_PORT=8000
DEBUG=true
```

Start the backend:

```bash
python api/main.py
```

### 3. Frontend Setup

```bash
cd Frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## 🔐 Authentication

| Method              | How it works                                                    |
| ------------------- | --------------------------------------------------------------- |
| **Email/Password**  | Passwords hashed with bcrypt, stored in MongoDB `users` collection |
| **Google Sign-In**  | Firebase Auth popup → user upserted into MongoDB                |
| **Session Persist** | Login state saved to localStorage, survives page refresh        |

---

## 📡 API Endpoints

| Method | Endpoint                      | Description                    |
| ------ | ----------------------------- | ------------------------------ |
| POST   | `/auth/signup`                | Register with name/email/pass  |
| POST   | `/auth/login`                 | Login with email/password      |
| POST   | `/auth/google`                | Upsert Google-authenticated user |
| POST   | `/plan`                       | Generate trip plan from form   |
| POST   | `/session/create`             | Create a new chat session      |
| GET    | `/session/<id>/history`       | Get chat history               |
| POST   | `/session/<id>/chat`          | Send a chat message            |
| GET    | `/health`                     | Health check                   |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is for educational purposes. All rights reserved.

---

<p align="center">
  Built with ❤️ by <strong>Team Plan-IT</strong>
</p>

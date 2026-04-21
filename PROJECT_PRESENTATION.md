# 🌍 Plan-IT — AI-Powered Travel Planner

## Project Overview

**Plan-IT** is a full-stack, AI-powered travel planning web application that generates personalized, day-by-day trip itineraries. Users fill a simple form with their destination, dates, budget, travel style, and interests — and our **multi-agent AI system** crafts a complete itinerary with timings, costs, restaurant suggestions, and local tips in seconds.

---

## 🧠 How It Works — Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React 19)                     │
│  Login/Signup → Trip Form → AI Results (Weather + Map + Plan)  │
└───────────────────────┬────────────────────────────────────────┘
                        │  REST API (Vite Proxy)
┌───────────────────────▼────────────────────────────────────────┐
│                      FLASK BACKEND                             │
│  Auth Routes │ Plan Route │ Weather Route │ Session Routes     │
└──┬──────┬────────┬─────────────┬───────────────────────────────┘
   │      │        │             │
   ▼      ▼        ▼             ▼
MongoDB  Multi-Agent      OpenWeatherMap     Session
Atlas    AI Pipeline       API               Memory
         │
    ┌────┬┴───┬──────┬──────────┐
    ▼    ▼    ▼      ▼          ▼
 Planner  Budget  Geo  Itinerary  Preference
 Agent    Agent   Agent  Agent     Agent
    │
    ▼
 Groq / Gemini LLM
```

---

## 🛠️ Complete Technology Stack

### Frontend
| Technology | Purpose |
|---|---|
| **React 19** | UI framework — component-based SPA |
| **Vite 7** | Build tool & dev server with HMR (Hot Module Replacement) |
| **Carbon Design System** | IBM's enterprise UI component library (buttons, forms, inputs, tags, headers) |
| **Firebase SDK** | Google Sign-In authentication (popup-based OAuth) |
| **Leaflet.js + react-leaflet** | Interactive maps with OpenStreetMap tiles |
| **SASS** | CSS preprocessing for advanced styling |
| **JavaScript (ES2022)** | Core programming language |
| **localStorage** | Client-side session persistence |

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.10+** | Backend programming language |
| **Flask 3.0** | Lightweight web framework for REST API |
| **Flask-CORS** | Cross-Origin Resource Sharing for frontend communication |
| **PyMongo** | MongoDB driver for Python |
| **bcrypt** | Password hashing (secure one-way encryption) |
| **Pydantic Settings** | Configuration management from environment variables |

### AI & LLM
| Technology | Purpose |
|---|---|
| **Groq Cloud (Llama 3.3 70B)** | Primary LLM provider — ultra-fast inference |
| **Google Gemini 2.0 Flash** | Backup LLM provider |
| **Multi-Agent Architecture** | 6 specialized agents working together |
| **ChromaDB** | Vector database for RAG (Retrieval-Augmented Generation) |
| **Sentence Transformers** | Text embedding model for semantic search |

### Database & External APIs
| Technology | Purpose |
|---|---|
| **MongoDB Atlas** | Cloud NoSQL database — stores users, sessions |
| **OpenWeatherMap API** | Real-time weather + 5-day forecast for destinations |
| **OpenStreetMap (Nominatim)** | Free geocoding fallback for map coordinates |
| **Leaflet Tile Server** | Map tiles rendering |

---

## 🤖 Multi-Agent AI System (Core Innovation)

Our backend uses a **multi-agent pipeline** where specialized AI agents collaborate:

| Agent | Role |
|---|---|
| **Planner Agent** | Orchestrator — coordinates all agents, synthesizes final plan |
| **Preference Agent** | Extracts user preferences from input (interests, pace, style) |
| **Budget Agent** | Analyzes costs, estimates daily per-person spending |
| **Geo Agent** | Provides geographic/location data for the destination |
| **Itinerary Agent** | Generates structured day-by-day plans with timings |
| **Expert Agent** | Adds travel expertise, local tips, and recommendations |

The **Planner Agent** sends the user's request through each specialist, then the **Itinerary Agent** generates the final structured plan using the Groq LLM with all context combined.

---

## ✨ Key Features

### 🔐 Authentication System
- **Email/Password** registration and login (bcrypt hashed, MongoDB stored)
- **Google Sign-In** via Firebase Auth (OAuth 2.0 popup)
- **Persistent sessions** — stay logged in across browser refreshes (localStorage)
- **Profile dropdown** with logout functionality

### 📝 Smart Trip Planning Form
- Structured inputs: destination, duration, start date, budget, travelers
- Travel style picker (Budget / Moderate / Luxury)
- Interest tags (Food, Adventure, Culture, Nature, History, etc.)
- Real-time progress indicator
- Per-person-per-day budget calculator

### 🗺️ Interactive Destination Map
- **Leaflet.js** with OpenStreetMap tiles — fully interactive (zoom, pan, click)
- Marker pin on the destination with popup info
- Dual geocoding: OpenWeatherMap coordinates → Nominatim fallback

### 🌤️ Live Weather Integration
- Current temperature, feels-like, humidity, wind speed
- 5-day weather forecast with daily cards
- Weather icons from OpenWeatherMap CDN

### 📋 Enhanced Itinerary Display
- **Timeline layout** with day cards and marker dots
- **Color-coded time badges** — Morning (amber), Afternoon (blue), Evening (purple), Night (indigo)
- **Contextual activity icons** — auto-detected from keywords (🛕 temple, 🏖️ beach, 🍽️ restaurant, etc.)
- **Cost tags** — ₹ amounts highlighted as green badges
- **Tip callouts** — amber-bordered boxes for local tips
- **Budget breakdown** — grid cards showing daily cost by category

### 💬 AI Chat Interface
- Session-based conversational chat with LLM
- Real-time message streaming
- Session management and history

---

## 🔒 Security Measures

- Passwords hashed with **bcrypt** (never stored in plain text)
- MongoDB Atlas cluster with **TLS/SSL encryption**
- API keys stored in server-side `.env` (not exposed to frontend)
- Frontend-to-backend communication via **Vite proxy** (no CORS leaks)
- Firebase Auth with Google's **OAuth 2.0** security

---

## 📁 Project Structure

```
PlanIT/
├── Frontend/                    # React + Vite SPA
│   ├── src/
│   │   ├── App.jsx              # Main app with routing and auth
│   │   ├── firebase.js          # Firebase config for Google Auth
│   │   ├── components/
│   │   │   ├── Login.jsx        # Email/password login
│   │   │   ├── Signup.jsx       # User registration
│   │   │   ├── Header.jsx       # Nav bar with profile dropdown
│   │   │   ├── TripPlanner.jsx  # Trip planning form
│   │   │   ├── TripResults.jsx  # AI results with weather + map
│   │   │   ├── WeatherWidget.jsx # Weather display
│   │   │   ├── TripMap.jsx      # Leaflet interactive map
│   │   │   └── ChatBox.jsx      # AI chat interface
│   │   └── services/api.js      # API client for all endpoints
│   └── vite.config.js           # Dev proxy config
│
├── Backend/                     # Flask API + AI Agents
│   ├── api/main.py              # All API routes
│   ├── auth.py                  # MongoDB auth helpers
│   ├── config.py                # Environment settings
│   ├── llm_client.py            # Multi-provider LLM client
│   ├── agents/
│   │   ├── planner_agent.py     # Orchestrator
│   │   ├── budget_agent.py      # Cost analysis
│   │   ├── geo_agent.py         # Location data
│   │   ├── itinerary_agent.py   # Plan generation
│   │   ├── preference_agent.py  # User preferences
│   │   └── expert_agent.py      # Travel expertise
│   ├── memory/                  # Session storage
│   └── rag/                     # RAG with ChromaDB
│
└── README.md
```

---

## 🚀 What Makes Plan-IT Unique

1. **Multi-Agent AI** — Not a simple LLM wrapper; 6 specialized agents collaborate like a real travel planning team
2. **Full-Stack Integration** — React + Flask + MongoDB + LLM + Weather API + Maps — all connected
3. **Dual Auth** — Both traditional email/password and modern Google Sign-In
4. **Real Data** — Live weather forecasts and interactive maps for actual destinations
5. **Structured Output** — Smart parsing turns raw AI text into beautifully formatted cards with icons, costs, and tips

---

*Built with ❤️ by Team Plan-IT*

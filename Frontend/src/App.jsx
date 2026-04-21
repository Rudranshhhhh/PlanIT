import { useState } from 'react';
import { Button } from '@carbon/react';
import ChatBox from './components/ChatBox';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './components/HomePage';
import Login from './components/Login';
import Signup from './components/Signup';
import TripPlanner from './components/TripPlanner';
import TripResults from './components/TripResults';
import FlightSelection from './components/FlightSelection';
import './App.css';

function App() {
  // Read login state from localStorage immediately (not in useEffect)
  const savedUser = (() => {
    try {
      const s = localStorage.getItem('planit_user');
      return s ? JSON.parse(s) : null;
    } catch { return null; }
  })();

  const [currentView, setCurrentView] = useState('home');
  const [isLoggedIn, setIsLoggedIn] = useState(!!savedUser);
  const [userName, setUserName] = useState(savedUser?.name || '');
  const [tripData, setTripData] = useState(null);
  const [tripResults, setTripResults] = useState(null);
  const [flightsList, setFlightsList] = useState([]);
  const [pendingPayload, setPendingPayload] = useState(null);

  // Theme state — persisted in localStorage
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem('planit_theme') || 'dark';
    } catch { return 'dark'; }
  });

  const toggleTheme = () => {
    setTheme((prev) => {
      const next = prev === 'dark' ? 'light' : 'dark';
      localStorage.setItem('planit_theme', next);
      return next;
    });
  };

  const navigate = (view) => {
    setCurrentView(view);
    window.scrollTo(0, 0);
  };

  const handleLogin = (user) => {
    setIsLoggedIn(true);
    setUserName(user?.name || '');
    localStorage.setItem('planit_user', JSON.stringify(user));
    navigate('planner');
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserName('');
    localStorage.removeItem('planit_user');
    navigate('home');
  };

  const handleOptionSkipFlights = async (payload) => {
    navigate('generating');
    try {
        const response = await fetch('/api/plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!response.ok) throw new Error('Failed to generate plan');
        const result = await response.json();
        setTripData(payload);
        setTripResults(result);
        navigate('results');
    } catch (e) {
        alert(e.message);
        navigate('planner');
    }
  };

  const handleFlightsFound = (flights, payload) => {
    setFlightsList(flights);
    setPendingPayload(payload);
    if (flights && flights.length > 0) {
        navigate('flights');
    } else {
        // Fallback directly to itinerary if no flights match Groq/Travelpayout criteria
        handleOptionSkipFlights(payload);
    }
  };

  const isHomePage = currentView === 'home';

  const renderView = () => {
    switch (currentView) {
      case 'login':
        return <Login onNavigate={navigate} onLogin={handleLogin} />;
      case 'signup':
        return <Signup onNavigate={navigate} onLogin={handleLogin} />;
      case 'planner':
        return <TripPlanner onFlightsFound={handleFlightsFound} />;
      case 'flights':
        return <FlightSelection flights={flightsList} onContinue={() => handleOptionSkipFlights(pendingPayload)} />;
      case 'generating':
        return (
            <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', justifyContent: 'center', alignItems: 'center', background: '#0f172a' }}>
                 <div className="loading-spinner" style={{ width: '60px', height: '60px', borderTopColor: '#38bdf8', marginBottom: '20px' }}></div>
                 <h2 style={{ color: '#fff' }}>Generating Itinerary...</h2>
                 <p style={{ color: '#94a3b8' }}>Our AI is crafting the perfect plan for you</p>
            </div>
        );
      case 'results':
        return tripData && tripResults ? (
          <TripResults
            tripData={tripData}
            tripResults={tripResults}
            onPlanAnother={() => navigate('planner')}
          />
        ) : (
          <TripPlanner onFlightsFound={handleFlightsFound} />
        );
      case 'chat':
        return (
          <div className="workspace">
            <div className="workspace-card">
              <main className="main-area">
                <ChatBox />
              </main>
            </div>
          </div>
        );
      case 'home':
      default:
        return <HomePage onNavigate={navigate} isLoggedIn={isLoggedIn} theme={theme} />;
    }
  };

  return (
    <div className={`app ${isHomePage ? `app--${theme}` : ''}`}>
      <Header onNavigate={navigate} isLoggedIn={isLoggedIn} userName={userName} onLogout={handleLogout} isHomePage={isHomePage} theme={theme} onToggleTheme={toggleTheme} />
      <div className="app-container">
        {renderView()}
        {isHomePage && <Footer />}
      </div>
    </div>
  );
}

export default App;

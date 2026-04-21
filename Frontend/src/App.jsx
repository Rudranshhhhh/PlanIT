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

  const handlePlanGenerated = (results, formData) => {
    setTripData(formData);
    setTripResults(results);
    navigate('results');
  };

  const isHomePage = currentView === 'home';

  const renderView = () => {
    switch (currentView) {
      case 'login':
        return <Login onNavigate={navigate} onLogin={handleLogin} />;
      case 'signup':
        return <Signup onNavigate={navigate} onLogin={handleLogin} />;
      case 'planner':
        return <TripPlanner onPlanGenerated={handlePlanGenerated} />;
      case 'results':
        return tripData && tripResults ? (
          <TripResults
            tripData={tripData}
            tripResults={tripResults}
            onPlanAnother={() => navigate('planner')}
          />
        ) : (
          <TripPlanner onPlanGenerated={handlePlanGenerated} />
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

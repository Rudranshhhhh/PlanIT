import { useState } from 'react';
import { Button } from '@carbon/react';
import { ArrowRight } from '@carbon/icons-react';
import ChatBox from './components/ChatBox';
import Header from './components/Header';
import Footer from './components/Footer';
import Login from './components/Login';
import Signup from './components/Signup';
import TripPlanner from './components/TripPlanner';
import TripResults from './components/TripResults';
import SplitText from './SplitText';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [tripData, setTripData] = useState(null);
  const [tripResults, setTripResults] = useState(null);

  const navigate = (view) => {
    setCurrentView(view);
    window.scrollTo(0, 0);
  };

  const handleLogin = () => {
    setIsLoggedIn(true);
    navigate('planner');
  };

  const handlePlanGenerated = (results, formData) => {
    setTripData(formData);
    setTripResults(results);
    navigate('results');
  };

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
        return (
          <header className="hero">
            <div className="hero-glow"></div>
            <div className="hero-inner">
              <div className="hero-content">
                <h1 className="hero-title">
                  <SplitText
                    text="Plan-IT"
                    delay={50}
                    duration={1.25}
                    ease="ease-out"
                    splitType="chars"
                    from={{ opacity: 0, y: 40 }}
                    to={{ opacity: 1, y: 0 }}
                    threshold={0.1}
                    rootMargin="-100px"
                    textAlign="left"
                    showCallback={false}
                  />
                  <span className="hero-highlight">Intelligent Planning</span>
                </h1>
                <p className="hero-sub">
                  Experience the future of travel planning.
                  Fill a form, get a complete AI-powered itinerary in seconds.
                </p>
                <div className="hero-buttons">
                  <Button
                    size="lg"
                    renderIcon={ArrowRight}
                    onClick={() => navigate(isLoggedIn ? 'planner' : 'signup')}
                    className="hero-cta"
                  >
                    Get Started Free
                  </Button>
                  <button className="btn-secondary" onClick={() => navigate('login')}>
                    Existing User?
                  </button>
                </div>
              </div>

              <aside className="hero-aside" aria-label="Key features">
                <div className="cards-grid">
                  <div className="feature-card card-1">
                    <span className="feature-icon">✨</span>
                    <div className="feature-text">
                      <h3>AI Powered</h3>
                      <p>Smart itinerary generation with LLMs</p>
                    </div>
                  </div>
                  <div className="feature-card card-2">
                    <span className="feature-icon">🗺️</span>
                    <div className="feature-text">
                      <h3>Smart Forms</h3>
                      <p>Plan trips with simple structured inputs</p>
                    </div>
                  </div>
                  <div className="feature-card card-3">
                    <span className="feature-icon">🌍</span>
                    <div className="feature-text">
                      <h3>Global Search</h3>
                      <p>Real-time info for any destination</p>
                    </div>
                  </div>
                </div>
              </aside>
            </div>
          </header>
        );
    }
  };

  return (
    <div className="app">
      <Header onNavigate={navigate} isLoggedIn={isLoggedIn} />
      <div className="app-container">
        {renderView()}
        {currentView === 'home' && <Footer />}
      </div>
    </div>
  );
}

export default App;

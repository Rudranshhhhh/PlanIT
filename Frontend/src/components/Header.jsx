import { useState, useRef, useEffect } from 'react';
import { UserAvatar, Logout } from '@carbon/icons-react';
import './Header.css';

const Header = ({ onNavigate, isLoggedIn, userName, onLogout, isHomePage, theme, onToggleTheme }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const isDark = theme === 'dark';

  return (
    <nav className={`hf-nav ${!isDark ? 'hf-nav--light' : ''}`}>
      <div className="hf-nav__pill">
        {/* Brand */}
        <div className="hf-nav__brand" onClick={() => onNavigate('home')}>
          Plan-IT
        </div>

        {/* Center Links */}
        <div className="hf-nav__links">
          <a
            href="#"
            className="hf-nav__link hf-nav__link--active"
            onClick={(e) => { e.preventDefault(); onNavigate('home'); }}
          >
            Explore
          </a>
          <a href="#features" className="hf-nav__link">Features</a>
          <a href="#agents" className="hf-nav__link">AI Agents</a>
          <a href="#" className="hf-nav__link">Pricing</a>
        </div>

        {/* Right Side */}
        <div className="hf-nav__actions">
          {/* Theme Toggle — only on homepage */}
          {isHomePage && (
            <button
              className="hf-nav__theme-toggle"
              onClick={onToggleTheme}
              aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
              title={isDark ? 'Light mode' : 'Dark mode'}
            >
              <span className="material-symbols-outlined">
                {isDark ? 'light_mode' : 'dark_mode'}
              </span>
            </button>
          )}

          {!isLoggedIn ? (
            <>
              <button
                className="hf-nav__login-btn"
                onClick={() => onNavigate('login')}
              >
                Login
              </button>
              <button
                className="hf-nav__signup-btn"
                onClick={() => onNavigate('signup')}
              >
                Sign Up
              </button>
            </>
          ) : (
            <div className="hf-nav__profile" ref={menuRef}>
              <button
                className="hf-nav__avatar-btn"
                onClick={() => setMenuOpen((prev) => !prev)}
                aria-label="Profile menu"
              >
                <UserAvatar size={22} />
                <span className="hf-nav__user-name">{userName || 'User'}</span>
              </button>

              {menuOpen && (
                <div className="hf-nav__dropdown">
                  <div className="hf-nav__dropdown-header">
                    <UserAvatar size={24} />
                    <span className="hf-nav__dropdown-name">{userName || 'User'}</span>
                  </div>
                  <div className="hf-nav__dropdown-divider" />
                  <button
                    className="hf-nav__dropdown-item"
                    onClick={() => { setMenuOpen(false); onNavigate('planner'); }}
                  >
                    🗺️ Trip Planner
                  </button>
                  <button
                    className="hf-nav__dropdown-item"
                    onClick={() => { setMenuOpen(false); onNavigate('chat'); }}
                  >
                    💬 AI Chat
                  </button>
                  <button
                    className="hf-nav__dropdown-item hf-nav__dropdown-logout"
                    onClick={() => { setMenuOpen(false); onLogout(); }}
                  >
                    <Logout size={16} />
                    Log Out
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Header;

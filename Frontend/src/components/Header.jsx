import { useState, useRef, useEffect } from 'react';
import {
  Header as CarbonHeader,
  HeaderName,
  HeaderNavigation,
  HeaderMenuItem,
  HeaderGlobalBar,
  HeaderGlobalAction,
} from '@carbon/react';
import { UserAvatar, Login as LoginIcon, Logout } from '@carbon/icons-react';
import './Header.css';

const Header = ({ onNavigate, isLoggedIn, userName, onLogout }) => {
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

  return (
    <CarbonHeader aria-label="PlanIT" className="planit-header">
      <HeaderName
        href="#"
        prefix=""
        onClick={(e) => { e.preventDefault(); onNavigate('home'); }}
        className="planit-brand"
      >
        Plan-IT
      </HeaderName>

      <HeaderNavigation aria-label="Main navigation">
        <HeaderMenuItem
          href="#"
          onClick={(e) => { e.preventDefault(); onNavigate('home'); }}
        >
          Home
        </HeaderMenuItem>
        <HeaderMenuItem href="#features">Features</HeaderMenuItem>
        <HeaderMenuItem href="#about">About</HeaderMenuItem>
      </HeaderNavigation>

      <HeaderGlobalBar>
        {!isLoggedIn ? (
          <HeaderGlobalAction
            aria-label="Log in"
            onClick={() => onNavigate('login')}
            tooltipAlignment="end"
          >
            <LoginIcon size={20} />
          </HeaderGlobalAction>
        ) : (
          <div className="profile-menu-wrapper" ref={menuRef}>
            <HeaderGlobalAction
              aria-label="Profile"
              onClick={() => setMenuOpen((prev) => !prev)}
              tooltipAlignment="end"
            >
              <UserAvatar size={20} />
            </HeaderGlobalAction>

            {menuOpen && (
              <div className="profile-dropdown">
                <div className="profile-dropdown-header">
                  <UserAvatar size={24} />
                  <span className="profile-dropdown-name">{userName || 'User'}</span>
                </div>
                <div className="profile-dropdown-divider" />
                <button
                  className="profile-dropdown-item"
                  onClick={() => { setMenuOpen(false); onNavigate('planner'); }}
                >
                  🗺️ Trip Planner
                </button>
                <button
                  className="profile-dropdown-item profile-dropdown-logout"
                  onClick={() => { setMenuOpen(false); onLogout(); }}
                >
                  <Logout size={16} />
                  Log Out
                </button>
              </div>
            )}
          </div>
        )}
      </HeaderGlobalBar>
    </CarbonHeader>
  );
};

export default Header;

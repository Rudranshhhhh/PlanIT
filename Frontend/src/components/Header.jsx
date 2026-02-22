import {
  Header as CarbonHeader,
  HeaderName,
  HeaderNavigation,
  HeaderMenuItem,
  HeaderGlobalBar,
  HeaderGlobalAction,
} from '@carbon/react';
import { UserAvatar, Login as LoginIcon } from '@carbon/icons-react';
import './Header.css';

const Header = ({ onNavigate, isLoggedIn }) => {
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
          <>
            <HeaderGlobalAction
              aria-label="Log in"
              onClick={() => onNavigate('login')}
              tooltipAlignment="end"
            >
              <LoginIcon size={20} />
            </HeaderGlobalAction>
          </>
        ) : (
          <HeaderGlobalAction
            aria-label="Profile"
            onClick={() => onNavigate('planner')}
            tooltipAlignment="end"
          >
            <UserAvatar size={20} />
          </HeaderGlobalAction>
        )}
      </HeaderGlobalBar>
    </CarbonHeader>
  );
};

export default Header;

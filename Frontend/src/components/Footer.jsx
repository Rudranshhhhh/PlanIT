import { Link } from '@carbon/react';
import './Footer.css';

const Footer = () => {
    return (
        <footer className="footer">
            <div className="footer-content">
                <div className="footer-brand">
                    <h3 className="footer-logo">Plan-IT</h3>
                    <p className="footer-tagline">Your intelligent travel companion.</p>
                    <div className="social-links">
                        <a href="#" className="social-link">𝕏</a>
                        <a href="#" className="social-link">📸</a>
                        <a href="#" className="social-link">📘</a>
                    </div>
                </div>

                <div className="footer-links">
                    <div className="link-column">
                        <h4>Product</h4>
                        <a href="#">Features</a>
                        <a href="#">Pricing</a>
                        <a href="#">Showcase</a>
                    </div>
                    <div className="link-column">
                        <h4>Company</h4>
                        <a href="#">About</a>
                        <a href="#">Careers</a>
                        <a href="#">Blog</a>
                    </div>
                    <div className="link-column">
                        <h4>Resources</h4>
                        <a href="#">Community</a>
                        <a href="#">Help Center</a>
                        <a href="#">Terms</a>
                    </div>
                </div>
            </div>
            <div className="footer-bottom">
                <p>&copy; {new Date().getFullYear()} Plan-IT Technologies. All rights reserved.</p>
            </div>
        </footer>
    );
};

export default Footer;

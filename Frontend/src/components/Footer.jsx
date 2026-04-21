import './Footer.css';

const Footer = () => {
  return (
    <footer className="hf-footer">
      <div className="hf-footer__grid">
        {/* Brand */}
        <div>
          <div className="hf-footer__brand-name">Plan-IT</div>
          <p className="hf-footer__brand-copy">
            © {new Date().getFullYear()} Plan-IT. Hyper-Fluid Discovery for the Next Gen.
          </p>
        </div>

        {/* Platform */}
        <div>
          <h4 className="hf-footer__col-title">Platform</h4>
          <div className="hf-footer__links">
            <a href="#" className="hf-footer__link">Features</a>
            <a href="#" className="hf-footer__link">Pricing</a>
            <a href="#" className="hf-footer__link">AI Agents</a>
          </div>
        </div>

        {/* Legal */}
        <div>
          <h4 className="hf-footer__col-title">Legal</h4>
          <div className="hf-footer__links">
            <a href="#" className="hf-footer__link">Terms</a>
            <a href="#" className="hf-footer__link">Privacy</a>
          </div>
        </div>

        {/* Connect */}
        <div>
          <h4 className="hf-footer__col-title">Connect</h4>
          <div className="hf-footer__links">
            <a href="#" className="hf-footer__link">Contact</a>
            <a href="#" className="hf-footer__link">Instagram</a>
            <a href="#" className="hf-footer__link">Discord</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

import './HomePage.css';

const HomePage = ({ onNavigate, isLoggedIn }) => {
  return (
    <>
      {/* Ambient Background Glow */}
      <div className="hf-ambient">
        <div className="hf-ambient-blob hf-ambient-blob--primary" />
        <div className="hf-ambient-blob hf-ambient-blob--secondary" />
        <div className="hf-ambient-blob hf-ambient-blob--tertiary" />
      </div>

      {/* Hero Section */}
      <section className="hf-hero">
        <div className="hf-hero__content hf-animate-in">
          <div className="hf-hero__badge">
            <span className="hf-hero__badge-text">Plan-IT: Intelligent Planning</span>
          </div>

          <h1 className="hf-hero__title">
            Discover The World
            <br />
            <span className="hf-hero__title-gradient">Hyper-Fluid</span>
          </h1>

          <p className="hf-hero__sub">
            A multi-agent AI architecture orchestrating your perfect itinerary. From deep
            preference analysis to dynamic budget allocation, experience travel planning in motion.
          </p>

          <div className="hf-hero__buttons">
            <button
              className="hf-btn-primary"
              onClick={() => onNavigate(isLoggedIn ? 'planner' : 'signup')}
            >
              Get Started Free
              <span className="material-symbols-outlined">arrow_forward</span>
            </button>
            {!isLoggedIn && (
              <button
                className="hf-btn-secondary"
                onClick={() => onNavigate('login')}
              >
                Existing User?
                <span className="material-symbols-outlined">login</span>
              </button>
            )}
          </div>
        </div>

        {/* Floating Hero Visual */}
        <div className="hf-hero__visual">
          <div
            className="hf-hero__visual-card"
            style={{
              backgroundImage: `url('https://lh3.googleusercontent.com/aida-public/AB6AXuDDdjbxDe4St_DhQh_1YSAwel3kkr0A5fHou_PCOgVzf7pPiuDA8N2lJdTKyVQXTv0CuxZMNQ6OwIZbh71wFNbtGq6RsQnUa8drEtU4Hq2f46B3XhH0JIPMTWGZkINc7HXpG-fm3zxrWJC_f2fh4NvGNJxfCOhY2YIEbIGst9g0GsqK_aBttjkeJspXyTJzyZIvVskbJJaZYohxpg6o2mplVkbM_y6iMX1u2HY-q8GIJXNc5XBb_ipjPL0TrjeMKpaq190mWkStjQi9')`,
            }}
          >
            <div className="hf-hero__visual-overlay" />
          </div>
        </div>
      </section>

      {/* Tech Stack Badge Strip */}
      <section className="hf-techstack">
        <div className="hf-techstack__inner">
          <span className="hf-techstack__label">Powered By</span>
          <div className="hf-techstack__item hf-techstack__item--secondary">
            <span className="material-symbols-outlined">code</span> React 19
          </div>
          <div className="hf-techstack__item hf-techstack__item--primary">
            <span className="material-symbols-outlined">view_quilt</span> IBM Carbon
          </div>
          <div className="hf-techstack__item hf-techstack__item--tertiary">
            <span className="material-symbols-outlined">bolt</span> Vite
          </div>
        </div>
      </section>

      {/* Features Section (Bento Grid) */}
      <section className="hf-features">
        <div className="hf-features__header">
          <h2 className="hf-features__title hf-animate-in">Intelligent Core</h2>
          <p className="hf-features__subtitle hf-animate-in hf-animate-delay-1">
            The foundation of your hyper-fluid discovery experience.
          </p>
        </div>

        <div className="hf-features__grid">
          {/* Card 1 — AI Powered */}
          <div className="hf-feature-card hf-animate-in hf-animate-delay-1">
            <div className="hf-feature-card__glow hf-feature-card__glow--primary" />
            <div className="hf-feature-card__icon hf-feature-card__icon--primary">
              <span className="material-symbols-outlined">psychology</span>
            </div>
            <h3 className="hf-feature-card__title">AI Powered</h3>
            <p className="hf-feature-card__desc">
              Continuous learning algorithms adapt to your micro-preferences in real-time,
              sculpting itineraries that breathe.
            </p>
          </div>

          {/* Card 2 — Smart Forms */}
          <div className="hf-feature-card hf-animate-in hf-animate-delay-2">
            <div className="hf-feature-card__glow hf-feature-card__glow--secondary" />
            <div className="hf-feature-card__icon hf-feature-card__icon--secondary">
              <span className="material-symbols-outlined">dynamic_form</span>
            </div>
            <h3 className="hf-feature-card__title">Smart Forms</h3>
            <p className="hf-feature-card__desc">
              Ditch static inputs. Our contextual UI morphs based on intent, capturing nuanced
              travel desires without friction.
            </p>
          </div>

          {/* Card 3 — Global Search */}
          <div className="hf-feature-card hf-animate-in hf-animate-delay-3">
            <div className="hf-feature-card__glow hf-feature-card__glow--tertiary" />
            <div className="hf-feature-card__icon hf-feature-card__icon--tertiary">
              <span className="material-symbols-outlined">travel_explore</span>
            </div>
            <h3 className="hf-feature-card__title">Global Search</h3>
            <p className="hf-feature-card__desc">
              Semantic discovery across fragmented global datasets, unifying flights, stays,
              and experiences into a single stream.
            </p>
          </div>
        </div>
      </section>

      {/* AI Agents Section (Orbital Visualization) */}
      <section className="hf-agents">
        <div className="hf-agents__bg-glow" />
        <div className="hf-agents__inner">
          <div className="hf-agents__text hf-animate-in">
            <h2 className="hf-agents__title">
              Multi-Agent <br />
              <span className="hf-agents__title-accent">Symphony</span>
            </h2>
            <p className="hf-agents__desc">
              Behind the glass, specialized AI agents converse, negotiate, and optimize every
              facet of your journey simultaneously.
            </p>
            <button className="hf-btn-outline">
              View Architecture
              <span className="material-symbols-outlined">open_in_new</span>
            </button>
          </div>

          <div className="hf-agents__visual">
            {/* Central Hub Node */}
            <div className="hf-node-hub">
              <span className="material-symbols-outlined">hub</span>
            </div>

            {/* Orbital Nodes */}
            <div className="hf-node hf-node--planner">
              <span className="material-symbols-outlined">event_note</span>
              <div className="hf-node__label">Planner</div>
            </div>

            {/* Connection Lines */}
            <div className="hf-connection hf-connection--planner" />

            <div className="hf-node hf-node--preference">
              <span className="material-symbols-outlined">tune</span>
              <div className="hf-node__label">Preference</div>
            </div>
            <div className="hf-connection hf-connection--preference" />

            <div className="hf-node hf-node--budget">
              <span className="material-symbols-outlined">account_balance_wallet</span>
              <div className="hf-node__label">Budget</div>
            </div>
            <div className="hf-connection hf-connection--budget" />

            <div className="hf-node hf-node--discovery">
              <span className="material-symbols-outlined">explore</span>
              <div className="hf-node__label">Discovery</div>
            </div>
            <div className="hf-connection hf-connection--discovery" />

            {/* Pulse on Discovery */}
            <div className="hf-node-pulse" />
          </div>
        </div>
      </section>
    </>
  );
};

export default HomePage;

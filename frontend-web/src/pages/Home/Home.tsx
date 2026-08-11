import "./Home.css";
import useLanguage from "../../hooks/useLanguage";

function Home() {
  const t = useLanguage();

  return (
    <div className="home">
      {/* Hero */}
      <section className="hero">
        <div className="hero-content">
          <span className="hero-badge">{t.home.badge}</span>

          <h1>
            {t.home.title}
            <span>{t.home.highlight}</span>
          </h1>

          <p>{t.home.description}</p>

          <div className="hero-buttons">
            <button className="primary-btn">{t.home.start}</button>

            <button className="secondary-btn">{t.home.learn}</button>
          </div>
        </div>
      </section>

      {/* Statistics */}

      <section className="stats">
        <div className="stat-card">
          <h2>52K+</h2>
          <p>{t.home.stats.transactions}</p>
        </div>

        <div className="stat-card">
          <h2>98.6%</h2>
          <p>{t.home.stats.accuracy}</p>
        </div>

        <div className="stat-card">
          <h2>97.9%</h2>
          <p>{t.home.stats.precision}</p>
        </div>

        <div className="stat-card">
          <h2>96.4%</h2>
          <p>{t.home.stats.recall}</p>
        </div>
      </section>

      {/* Workflow */}

      <section className="workflow">
        <h2>{t.home.workflow.title}</h2>

        <div className="workflow-grid">
          <div className="workflow-card">
            <span>1</span>
            <h3>{t.home.workflow.step1}</h3>

            <p>{t.home.workflow.step1Desc}</p>
          </div>

          <div className="workflow-card">
            <span>2</span>
            <h3>{t.home.workflow.step2}</h3>
            <p>{t.home.workflow.step2Desc}</p>
          </div>

          <div className="workflow-card">
            <span>3</span>
            <h3>{t.home.workflow.step3}</h3>
            <p>{t.home.workflow.step3Desc}</p>
          </div>

          <div className="workflow-card">
            <span>4</span>
            <h3>{t.home.workflow.step4}</h3>
            <p>{t.home.workflow.step4Desc}</p>
          </div>
        </div>
      </section>

      {/* Technology */}

      <section className="technology">
        <h2>{t.home.technology.title}</h2>

        <div className="tech-box">
          <div>
            <h3>XGBoost</h3>
            <p>{t.home.technology.xgb}</p>
          </div>

          <div className="plus">+</div>

          <div>
            <h3>LSTM</h3>
            <p>{t.home.technology.lstm}</p>
          </div>
        </div>
      </section>

      {/* CTA */}

      <section className="cta">
        <h2>{t.home.cta.title}</h2>

        <p>{t.home.cta.description}</p>

        <button className="primary-btn">{t.home.cta.button}</button>
      </section>
    </div>
  );
}

export default Home;

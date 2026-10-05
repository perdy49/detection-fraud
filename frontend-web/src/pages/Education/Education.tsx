import "./Education.css";
import useLanguage from "../../hooks/useLanguage";

function Education() {
  const t = useLanguage();

  return (
    <div className="education">
      {/* Header */}

      <section className="education-header">
        <h1>{t.education.title}</h1>

        <p>{t.education.description}</p>
      </section>

      {/* What is Fraud */}

      <section className="education-section">
        <h2>{t.education.unauthorized.title}</h2>

        <div className="info-card">
          <p>{t.education.unauthorized.content}</p>
        </div>
      </section>

      {/* Types */}

      <section className="education-section">
        <h2>{t.education.types.title}</h2>

        <div className="type-grid">
          <div className="type-card">
            <h3>💳 {t.education.types.card}</h3>
            <p>{t.education.types.cardDesc}</p>
          </div>

          <div className="type-card">
            <h3>🪪 {t.education.types.identity}</h3>
            <p>{t.education.types.identityDesc}</p>
          </div>

          <div className="type-card">
            <h3>🔓 {t.education.types.account}</h3>
            <p>{t.education.types.accountDesc}</p>
          </div>

          <div className="type-card">
            <h3>🎣 {t.education.types.phishing}</h3>
            <p>{t.education.types.phishingDesc}</p>
          </div>
        </div>
      </section>

      {/* Workflow */}

      <section className="education-section">
        <h2>{t.education.workflow.title}</h2>

        <div className="workflow-ai">
          <div className="step">Transaction</div>
          <span>→</span>

          <div className="step">Preprocessing</div>
          <span>→</span>

          <div className="step">Feature Engineering</div>
          <span>→</span>

          <div className="step">XGBoost</div>
          <span>+</span>

          <div className="step">LSTM</div>
          <span>→</span>

          <div className="step">Prediction</div>
        </div>
      </section>

      {/* Advantages */}

      <section className="education-section">
        <h2>{t.education.advantages.title}</h2>

        <div className="advantage-grid">
          <div className="advantage-card">
            <h3>{t.education.advantages.accuracy}</h3>
            <p>{t.education.advantages.accuracyDesc}</p>
          </div>

          <div className="advantage-card">
            <h3>{t.education.advantages.realtime}</h3>
            <p>{t.education.advantages.realtimeDesc}</p>
          </div>

          <div className="advantage-card">
            <h3>{t.education.advantages.pattern}</h3>
            <p>{t.education.advantages.patternDesc}</p>
          </div>
        </div>
      </section>

      {/* FAQ */}

      <section className="education-section">
        <h2>{t.education.faq.title}</h2>

        <div className="faq-card">
          <h3>{t.education.faq.q1}</h3>
          <p>{t.education.faq.a1}</p>
        </div>

        <div className="faq-card">
          <h3>{t.education.faq.q2}</h3>
          <p>{t.education.faq.a2}</p>
        </div>
      </section>
    </div>
  );
}

export default Education;

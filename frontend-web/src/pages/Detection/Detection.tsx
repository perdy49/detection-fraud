import "./Detection.css";
import useLanguage from "../../hooks/useLanguage";

function Detection() {
  const t = useLanguage();

  return (
    <div className="detection">
      <section className="detection-header">
        <h1>{t.detection.title}</h1>

        <p>{t.detection.description}</p>
      </section>

      <section className="detection-container">
        {/* Form */}

        <div className="detection-form">
          <h2>{t.detection.form.title}</h2>

          <div className="form-group">
            <label>{t.detection.form.amount}</label>

            <input
              type="number"
              placeholder={t.detection.form.amountPlaceholder}
            />
          </div>

          <div className="form-group">
            <label>{t.detection.form.product}</label>

            <select defaultValue="">
              <option value="" disabled>
                {t.detection.form.productPlaceholder}
              </option>

              <option>W</option>
              <option>H</option>
              <option>C</option>
              <option>S</option>
              <option>R</option>
            </select>
          </div>

          <div className="form-group">
            <label>{t.detection.form.card}</label>

            <select defaultValue="">
              <option value="" disabled>
                {t.detection.form.cardPlaceholder}
              </option>

              <option>Visa</option>
              <option>Mastercard</option>
              <option>Discover</option>
              <option>American Express</option>
            </select>
          </div>

          <div className="form-group">
            <label>{t.detection.form.email}</label>

            <input
              type="text"
              placeholder={t.detection.form.emailPlaceholder}
            />
          </div>

          <div className="form-group">
            <label>{t.detection.form.time}</label>

            <input type="datetime-local" />
          </div>

          <button className="primary-btn">{t.detection.form.button}</button>
        </div>

        {/* Result */}

        <div className="prediction-panel">
          <h2>{t.detection.result.title}</h2>

          <div className="result-card">
            <h3>{t.detection.result.status}</h3>

            <span className="safe-status">{t.detection.result.legitimate}</span>
          </div>

          <div className="result-card">
            <h3>{t.detection.result.probability}</h3>

            <div className="progress">
              <div className="progress-fill" style={{ width: "12%" }}></div>
            </div>

            <p>12%</p>
          </div>

          <div className="result-card">
            <h3>{t.detection.result.recommendation}</h3>

            <p>{t.detection.result.safeMessage}</p>
          </div>

          {/* Result Actions */}

          <div className="result-actions">
            <button className="delete-result-btn">{t.detection.result.ClearResults}</button>

            <button className="save-result-btn">{t.detection.result.SaveToHistory}</button>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Detection;

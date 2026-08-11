import "./History.css";
import useLanguage from "../../hooks/useLanguage";

function History() {
  const t = useLanguage();

  return (
    <div className="history">
      <section className="history-header">
        <h1>{t.history.title}</h1>

        <p>{t.history.description}</p>
      </section>

      <section className="history-search">
        <input type="text" placeholder={t.history.search} />

        <select>
          <option>{t.history.filter.all}</option>
          <option>{t.history.filter.legitimate}</option>
          <option>{t.history.filter.unauthorized}</option>
        </select>
      </section>

      <section className="history-list">
        <div className="history-card">
          <div className="history-top">
            <h3>#TRX-2026001</h3>

            <span className="safe">{t.history.filter.legitimate}</span>
          </div>

          <div className="history-body">
            <div>
              <label>{t.history.amount}</label>
              <p>Rp 350.000</p>
            </div>

            <div>
              <label>{t.history.probability}</label>
              <p>12%</p>
            </div>

            <div>
              <label>{t.history.date}</label>
              <p>01 Jul 2026</p>
            </div>
          </div>
        </div>

        <div className="history-card">
          <div className="history-top">
            <h3>#TRX-2026002</h3>

            <span className="fraud">{t.history.filter.unauthorized}</span>
          </div>

          <div className="history-body">
            <div>
              <label>{t.history.amount}</label>
              <p>Rp 7.250.000</p>
            </div>

            <div>
              <label>{t.history.probability}</label>
              <p>98%</p>
            </div>

            <div>
              <label>{t.history.date}</label>
              <p>30 Jun 2026</p>
            </div>
          </div>
        </div>

        <div className="history-card">
          <div className="history-top">
            <h3>#TRX-2026003</h3>

            <span className="safe">{t.history.filter.legitimate}</span>
          </div>

          <div className="history-body">
            <div>
              <label>{t.history.amount}</label>
              <p>Rp 1.200.000</p>
            </div>

            <div>
              <label>{t.history.probability}</label>
              <p>5%</p>
            </div>

            <div>
              <label>{t.history.date}</label>
              <p>28 Jun 2026</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default History;

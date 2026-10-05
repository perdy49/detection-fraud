import { translations } from "../utils/language";
import type { Language } from "../utils/language";

interface FooterProps {
  language: Language;
}

function Footer({ language }: FooterProps) {
  const t = translations[language];

  return (
    <footer className="footer">
      <div className="footer-container">
        <h3>FraudDetect</h3>

        <p>{t.footer.description}</p>

        <small>{t.footer.copyright}</small>
      </div>
    </footer>
  );
}

export default Footer;

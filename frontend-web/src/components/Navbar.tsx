import { NavLink } from "react-router-dom";
import { useState } from "react";

import { translations } from "../utils/language";
import type { Language } from "../utils/language";

type Theme = "light" | "dark";

interface NavbarProps {
  language: Language;
  setLanguage: React.Dispatch<React.SetStateAction<Language>>;

  theme: Theme;
  setTheme: React.Dispatch<React.SetStateAction<Theme>>;
}

function Navbar({ language, setLanguage, theme, setTheme }: NavbarProps) {
  const t = translations[language];

  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="navbar">
      <div className="navbar-container">
        <NavLink to="/" className="navbar-logo">
          Fraud<span>Detect</span>
        </NavLink>

        <button className="menu-toggle" onClick={() => setMenuOpen(!menuOpen)}>
          ☰
        </button>

        <nav className={`navbar-menu ${menuOpen ? "open" : ""}`}>
          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
            onClick={() => setMenuOpen(false)}
          >
            {t.navbar.home}
          </NavLink>

          <NavLink
            to="/detection"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
            onClick={() => setMenuOpen(false)}
          >
            {t.navbar.detection}
          </NavLink>

          <NavLink
            to="/history"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
            onClick={() => setMenuOpen(false)}
          >
            {t.navbar.history}
          </NavLink>

          <NavLink
            to="/education"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
            onClick={() => setMenuOpen(false)}
          >
            {t.navbar.education}
          </NavLink>

          {/* Language */}
          <select
            className="language-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value as Language)}
          >
            <option value="en">🇺🇸 English</option>
            <option value="id">🇮🇩 Indonesia</option>
          </select>

          {/* Theme */}
          <select
            className="theme-select"
            value={theme}
            onChange={(e) => setTheme(e.target.value as Theme)}
          >
            <option value="light">☀️ Light</option>
            <option value="dark">🌙 Dark</option>
          </select>
        </nav>
      </div>
    </header>
  );
}

export default Navbar;

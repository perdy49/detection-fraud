import { Outlet } from "react-router-dom";
import { useEffect, useState } from "react";

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

import type { Language } from "../utils/language";

type Theme = "light" | "dark";

function MainLayout() {
  const [language, setLanguage] = useState<Language>("en");
  const [theme, setTheme] = useState<Theme>("light");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  return (
    <>
      <Navbar
        language={language}
        setLanguage={setLanguage}
        theme={theme}
        setTheme={setTheme}
      />

      <main>
        <Outlet
          context={{
            language
          }}
        />
      </main>

      <Footer language={language} />
    </>
  );
}

export default MainLayout;

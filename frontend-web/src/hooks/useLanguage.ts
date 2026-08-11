import { useOutletContext } from "react-router-dom";

import { translations } from "../utils/language";
import type { Language } from "../utils/language";

export default function useLanguage() {
  const { language } = useOutletContext<{
    language: Language;
  }>();

  return translations[language];
}

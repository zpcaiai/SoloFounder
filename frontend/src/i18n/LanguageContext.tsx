import { useState, type ReactNode } from "react";
import { I18nContext } from "./context";
import { translations, type Lang, type TranslationKey } from "./translations";

const STORAGE_KEY = "rp_lang";

function getInitialLang(): Lang {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "en" || stored === "zh") return stored;
  return navigator.language.startsWith("zh") ? "zh" : "en";
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(getInitialLang);

  const setLang = (l: Lang) => {
    localStorage.setItem(STORAGE_KEY, l);
    setLangState(l);
  };

  const t = (key: TranslationKey) => translations[lang][key];

  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

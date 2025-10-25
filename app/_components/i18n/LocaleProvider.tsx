"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import en from '../../locales/en.json';
import zh from '../../locales/zh.json';

type Translations = Record<string, unknown>;

const translationsMap: Record<string, Translations> = {
  en,
  zh
};

type LocaleContextType = {
  locale: string;
  setLocale: (l: string) => void;
  t: (key: string, fallback?: string) => string | string[];
  allLocales: string[];
};

const LocaleContext = createContext<LocaleContextType>({
  locale: 'zh',
  setLocale: () => {},
  t: (k: string) => k,
  allLocales: ['zh', 'en']
});

function lookup(obj: unknown, key: string): unknown {
  const parts = key.split('.');
  let cur: unknown = obj;
  for (const p of parts) {
    if (cur == null) return undefined;
    if (typeof cur === 'object') {
      const record = cur as Record<string, unknown>;
      cur = record[p];
    } else {
      return undefined;
    }
  }
  return cur;
}

export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<string>('zh');

  useEffect(() => {
    try {
      const saved = localStorage.getItem('locale');
      if (saved) {
        setLocaleState(saved);
        return;
      }
      const nav = (navigator && navigator.language) || 'zh';
      if (nav.startsWith('en')) setLocaleState('en');
      else setLocaleState('zh');
    } catch (e) {
      setLocaleState('zh');
    }
  }, []);

  const setLocale = (l: string) => {
    setLocaleState(l);
    try {
      localStorage.setItem('locale', l);
    } catch {}
  };

  const t = (key: string, fallback?: string): string | string[] => {
    const dict = translationsMap[locale] || translationsMap['zh'];
    const val = lookup(dict, key);
    if (val === undefined || val === null) return (fallback ?? key) as string;
  if (typeof val === 'string' || Array.isArray(val)) return val as string | string[];
    // Fallback to string
    return String(val);
  };

  const value = { locale, setLocale, t, allLocales: Object.keys(translationsMap) };

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useTranslation() {
  return useContext(LocaleContext);
}

export default LocaleProvider;

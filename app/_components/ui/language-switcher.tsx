"use client";

import React from 'react';
import { useTranslation } from '@/components/i18n/LocaleProvider';

export default function LanguageSwitcher() {
  const { locale, setLocale } = useTranslation();

  return (
    <div className="fixed bottom-30 right-4 z-50">
      <div className="inline-flex flex-col items-end gap-2">
        <button
          className={`px-3 py-2 rounded-md border bg-card text-muted-foreground text-sm ${locale === 'zh' ? 'ring-2 ring-primary' : ''}`}
          onClick={() => setLocale('zh')}
          aria-label="中文"
        >
          中文
        </button>
        <button
          className={`px-3 py-2 rounded-md border bg-card text-muted-foreground text-sm ${locale === 'en' ? 'ring-2 ring-primary' : ''}`}
          onClick={() => setLocale('en')}
          aria-label="English"
        >
          EN
        </button>
      </div>
    </div>
  );
}

"use client";
import React, { useEffect, useState } from "react";

const THEME_KEY = "theme";

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState<boolean>(false);

  useEffect(() => {
    // Initialize from localStorage or prefers-color-scheme
    try {
      const raw = localStorage.getItem(THEME_KEY);
      if (raw === "dark") {
        document.documentElement.classList.add("dark");
        setIsDark(true);
      } else if (raw === "light") {
        document.documentElement.classList.remove("dark");
        setIsDark(false);
      } else {
        const mq = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)");
        const prefersDark = mq ? mq.matches : false;
        if (prefersDark) {
          document.documentElement.classList.add("dark");
          setIsDark(true);
        } else {
          document.documentElement.classList.remove("dark");
          setIsDark(false);
        }

        // If user hasn't explicitly selected theme, listen to system changes
        if (mq) {
          const onChange = (e: MediaQueryListEvent) => {
            try {
              const rawInner = localStorage.getItem(THEME_KEY);
              if (rawInner) return; // user has chosen, don't override
              if (e.matches) {
                document.documentElement.classList.add('dark');
                setIsDark(true);
              } else {
                document.documentElement.classList.remove('dark');
                setIsDark(false);
              }
            } catch (err) {
              console.warn('prefers-color-scheme handler failed', err);
            }
          };
          // For modern browsers
          if (typeof mq.addEventListener === 'function') {
            mq.addEventListener('change', onChange);
          } else {
            // Legacy Safari fallback
            type LegacyMQ = { addListener?: (cb: (e: MediaQueryListEvent) => void) => void };
            const legacy = mq as unknown as LegacyMQ;
            legacy.addListener?.(onChange);
          }

          // cleanup
          return () => {
            if (typeof mq.removeEventListener === 'function') {
              mq.removeEventListener('change', onChange);
            } else {
              type LegacyMQRem = { removeListener?: (cb: (e: MediaQueryListEvent) => void) => void };
              const legacyRem = mq as unknown as LegacyMQRem;
              legacyRem.removeListener?.(onChange);
            }
          };
        }
      }
    } catch (e) {
      console.warn("Theme init failed", e);
    }
  }, []);

  const toggle = () => {
    try {
      if (isDark) {
        document.documentElement.classList.remove("dark");
        localStorage.setItem(THEME_KEY, "light");
        setIsDark(false);
      } else {
        document.documentElement.classList.add("dark");
        localStorage.setItem(THEME_KEY, "dark");
        setIsDark(true);
      }
    } catch (e) {
      console.warn("Theme toggle failed", e);
    }
  };

  return (
    <button
      onClick={toggle}
      aria-pressed={isDark}
      className="inline-flex items-center justify-center w-10 h-10 rounded-md border border-border bg-card text-card-foreground hover:shadow-sm"
      title={isDark ? "切换为浅色模式" : "切换为黑暗模式"}
    >
      {isDark ? (
        // sun icon
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
          <path d="M6.76 4.84l-1.8-1.79L3.17 4.84l1.79 1.79 1.8-1.79zM1 13h3v-2H1v2zm10 8h2v-3h-2v3zm8.83-16.95l-1.79-1.79-1.8 1.79 1.8 1.79 1.79-1.79zM17.24 19.16l1.79 1.79 1.8-1.79-1.8-1.79-1.79 1.79zM20 11v2h3v-2h-3zM11 1h2v3h-2V1zM4.22 19.78l1.79-1.79-1.79-1.79-1.79 1.79 1.79 1.79zM12 6a6 6 0 100 12A6 6 0 0012 6z" />
        </svg>
      ) : (
        // moon icon
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
          <path d="M21.64 13.06A9 9 0 1110.94 2.36 7 7 0 0021.64 13.06z" />
        </svg>
      )}
    </button>
  );
}


'use client';

import Link from 'next/link';

export default function NotFound() {
  return (
  <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-24 -left-24 h-96 w-96 rounded-full blur-3xl opacity-30" style={{ background: 'radial-gradient(closest-side, #082A7B, transparent)' }} />
        <div className="absolute -bottom-24 -right-24 h-[28rem] w-[28rem] rounded-full blur-3xl opacity-30" style={{ background: 'radial-gradient(closest-side, #6AA7FF, transparent)' }} />
      </div>

      <div className="relative z-10 mx-auto max-w-2xl px-6 text-center">
        <div className="text-[10rem] leading-none font-extrabold tracking-tight select-none bg-clip-text text-transparent" style={{ backgroundImage: 'linear-gradient(to bottom, rgba(8,42,123,0.9) 30%, rgba(8,42,123,0.1) 76%)' }}>
          404
        </div>
  <h1 className="mt-2 text-3xl font-bold text-foreground">Oops! This page can’t be found</h1>
  <p className="mt-3 text-base text-muted-foreground">The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.</p>

        <div className="mt-8 flex items-center justify-center gap-4">
          <Link href="/" className="inline-flex items-center justify-center rounded-full bg-primary px-6 py-3 text-white text-sm font-medium shadow-md hover:shadow-lg transition">
            Back to Home
          </Link>
          <Link href="/contact" className="inline-flex items-center justify-center rounded-full border px-6 py-3 text-sm font-medium text-foreground hover:bg-gray-50 transition">
            Contact Us
          </Link>
        </div>
      </div>

      <div aria-hidden className="pointer-events-none absolute inset-x-0 bottom-16 flex justify-center gap-6 text-3xl opacity-70">
        <span>🍪</span>
        <span>🍪</span>
        <span>🍪</span>
      </div>
    </div>
  );
}



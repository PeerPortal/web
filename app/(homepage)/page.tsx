"use client";

import Image from 'next/image';
import SearchField from '@/components/search-field';
import ThemeToggle from '@/components/ui/theme-toggle';
import { CheckCircle, Shield, Clock, ChevronRight } from 'lucide-react';
import React from 'react';
import { useTranslation } from '@/components/i18n/LocaleProvider';

type CarouselItem = { title: string; sub: string; image: string };

function Carousel3D({
  items,
  cardWidth,
  cardHeight
}: {
  items: CarouselItem[];
  cardWidth: number;
  cardHeight: number;
}) {
  const [idx, setIdx] = React.useState(0);
  const len = items.length;

  const cls = React.useCallback(
    (i: number) => {
      const o = (i - idx + len) % len;
      if (o === 0) return 'pp-center';
      if (o === 1) return 'pp-right-1';
      if (o === 2) return 'pp-right-2';
      if (o === len - 1) return 'pp-left-1';
      if (o === len - 2) return 'pp-left-2';
      return 'pp-hidden';
    },
    [idx, len]
  );

  React.useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') setIdx(v => (v - 1 + len) % len);
      if (e.key === 'ArrowRight') setIdx(v => (v + 1) % len);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [len]);

  return (
    <div className="pp-carousel">
      <button className="pp-nav pp-left" onClick={() => setIdx(v => (v - 1 + len) % len)}>{'<'}</button>
      <div className="pp-track">
        {items.map((it, i) => (
          <div key={i} className={`pp-card ${cls(i)}`} onClick={() => setIdx(i)}>
            <Image src={it.image} alt={it.title} width={cardWidth} height={cardHeight} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </div>
        ))}
      </div>
      <button className="pp-nav pp-right" onClick={() => setIdx(v => (v + 1) % len)}>{'>'}</button>

      <div className="pp-info">
        <div className="pp-name">{items[idx]?.title}</div>
        <div className="pp-sub">{items[idx]?.sub}</div>
        <div className="pp-dots">
          {items.map((_, i) => (
            <div key={i} className={`pp-dot ${i === idx ? 'pp-active' : ''}`} onClick={() => setIdx(i)} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default function Homepage() {
  const { t } = useTranslation();
  const destinations = [
    {
      name: '北美洲',
      properties: '122 位导师',
      image: '/regions/north-america.jpg'
    },
    {
      name: '欧洲',
      properties: '98 位导师',
      image: '/regions/europe.jpg'
    },
    {
      name: '日本',
      properties: '66 位导师',
      image: '/regions/jp.jpg'
    },
    {
      name: '英国',
      properties: '221 位导师',
      image: '/regions/uk.jpg'
    },
    {
      name: '澳洲',
      properties: '111 位导师',
      image: '/regions/australia.jpg'
    },
    {
      name: '香港',
      properties: '45 位导师',
      image: '/regions/hongkong.jpg'
    }
  ];

  const popularSchools = [
    {
      name: '哈佛大学',
      location: '美国',
      tutors: '32 位导师',
      image: '/schools/harvard.jpg'
    },
    {
      name: '斯坦福大学',
      location: '美国',
      tutors: '28 位导师',
      image: '/schools/stanford.jpg'
    },
    {
      name: '麻省理工学院',
      location: '美国',
      tutors: '35 位导师',
      image: '/schools/mit.jpg'
    },
    {
      name: '牛津大学',
      location: '英国',
      tutors: '24 位导师',
      image: '/schools/oxford.jpg'
    },
    {
      name: '剑桥大学',
      location: '英国',
      tutors: '22 位导师',
      image: '/schools/cambridge.jpg'
    },
    {
      name: '东京大学',
      location: '日本',
      tutors: '18 位导师',
      image: '/schools/tokyo.jpg'
    },
    {
      name: '新加坡国立大学',
      location: '新加坡',
      tutors: '16 位导师',
      image: '/schools/nus.jpg'
    },
    {
      name: '香港大学',
      location: '香港',
      tutors: '15 位导师',
      image: '/schools/hku.jpeg'
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-[600px] flex items-center justify-center">
        {/* Theme toggle (top-right) */}
        <div className="absolute right-6 top-6 z-20">
          <ThemeToggle />
        </div>
        {/* Background Image */}
        <div className="absolute inset-0 z-0">
          <Image
            src="/bg.jpg"
            alt="学生留学申请场景"
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-black/20" />
        </div>

        {/* Content */}
        <div className="relative z-10 text-center px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6">
            {t('homepage.titleLine1')}
            <br />
            {t('homepage.titleLine2')}
          </h1>
          <p className="text-lg sm:text-xl text-white/90 mb-8 max-w-3xl mx-auto font-medium">
            {t('homepage.subtitle')}
          </p>

          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto mb-8">
            <SearchField />
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-wrap justify-center items-center gap-6 sm:gap-8 text-white/90">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-primary" />
              <span className="text-sm sm:text-base font-medium">认证导师</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-primary" />
              <span className="text-sm sm:text-base font-medium">价格保障</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-primary" />
              <span className="text-sm sm:text-base font-medium">
                24小时协助
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* AI Assistant Feature Section */}
      <section className="py-16 bg-gradient-to-br from-primary/5 via-background to-primary/10">
        <div className="w-full max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="relative">
                <svg
                  className="h-8 w-8 text-primary"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
                </svg>
                <div className="absolute -top-1 -right-1 h-3 w-3 bg-yellow-400 rounded-full animate-pulse"></div>
              </div>
              <h2 className="text-3xl font-bold text-foreground">
                {t('homepage.cta.aiTitle')}
              </h2>
            </div>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
              {t('homepage.cta.aiSubtitle')}
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 items-center">
            {/* Features */}
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <svg
                    className="h-5 w-5 text-primary"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-2">
                    智能学校推荐
                  </h3>
                  <p className="text-muted-foreground text-sm">
                    基于您的背景和偏好，AI为您推荐最匹配的学校和专业
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <svg
                    className="h-5 w-5 text-primary"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-2">
                    引路人匹配
                  </h3>
                  <p className="text-muted-foreground text-sm">
                    AI帮您找到最合适的学长学姐导师，获得一对一指导
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <svg
                    className="h-5 w-5 text-primary"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-2">
                    申请时间规划
                  </h3>
                  <p className="text-muted-foreground text-sm">
                    制定详细的申请时间表，确保不错过任何重要截止日期
                  </p>
                </div>
              </div>
            </div>

            {/* CTA */}
            <div className="bg-card rounded-2xl p-8 shadow-lg border">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-primary to-primary/70 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg
                    className="h-8 w-8 text-white"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M8.5 3h7c.28 0 .5.22.5.5v8c0 .28-.22.5-.5.5h-7c-.28 0-.5-.22-.5-.5v-8c0-.28.22-.5.5-.5z" />
                    <path d="M15 13.5v5c0 .28-.22.5-.5.5h-6c-.28 0-.5-.22-.5-.5v-5" />
                    <circle cx="9" cy="16" r="1" />
                    <circle cx="15" cy="16" r="1" />
                    <path d="M9 20v1m6-1v1" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-foreground mb-3">
                  {t('homepage.cta.ctaTitle')}
                </h3>
                <p className="text-muted-foreground mb-6">
                  {t('homepage.cta.ctaDesc')}
                </p>
                <a
                  href="/ai-advisor"
                  className="inline-flex items-center gap-2 bg-gradient-to-r from-primary to-primary/80 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-200 transform hover:scale-105"
                >
                  {t('homepage.cta.ctaButton')}
                  <ChevronRight className="h-4 w-4" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Popular Areas Section */}
      <section className="py-16 bg-gray-50 ">
        <div className="w-full max-w-7xl mx-auto px-4">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-foreground mb-2">
              {t('homepage.popularAreasTitle')}
            </h2>
            <p className="text-muted-foreground text-base">
              {t('homepage.popularAreasSub')}
            </p>
          </div>

          <Carousel3D
            items={destinations.map((d) => ({
              title: d.name,
              sub: d.properties,
              image: d.image
            }))}
            cardWidth={256}
            cardHeight={192}
          />
        </div>
      </section>

      {/* Popular Schools Section */}
      <section className="py-16">
        <div className="w-full max-w-7xl mx-auto px-4">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-foreground mb-2">{t('homepage.popularSchoolsTitle')}</h2>
            <p className="text-muted-foreground text-base">{t('homepage.popularSchoolsSub')}</p>
          </div>

          <Carousel3D
            items={popularSchools.map((s) => ({
              title: s.name,
              sub: `${s.location} · ${s.tutors}`,
              image: s.image
            }))}
            cardWidth={192}
            cardHeight={128}
          />
        </div>
      </section>
    </div>
  );
}

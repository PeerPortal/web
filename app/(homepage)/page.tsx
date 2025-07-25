'use client';

import Image from 'next/image';
import SearchField from '@/components/search-field';
import { CheckCircle, Shield, Clock, ChevronRight } from 'lucide-react';

export default function Homepage() {
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
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative min-h-[600px] flex items-center justify-center">
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
            全球学子的留学导师之家
          </h1>
          <p className="text-lg sm:text-xl text-white/90 mb-8 max-w-3xl mx-auto font-medium">
            寻找最适合你的留学申请导师，助力世界顶尖大学申请之路
          </p>

          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto mb-8">
            <SearchField />
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-wrap justify-center items-center gap-6 sm:gap-8 text-white/90">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-red-400" />
              <span className="text-sm sm:text-base font-medium">认证导师</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-red-400" />
              <span className="text-sm sm:text-base font-medium">价格保障</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-red-400" />
              <span className="text-sm sm:text-base font-medium">
                24小时协助
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* AI Assistant Feature Section */}
      <section className="py-16 bg-gradient-to-br from-primary/5 via-background to-primary/10">
        <div className="w-full max-w-6xl mx-auto px-4">
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-4">
              <div className="relative">
                <svg className="h-8 w-8 text-primary" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
                <div className="absolute -top-1 -right-1 h-3 w-3 bg-yellow-400 rounded-full animate-pulse"></div>
              </div>
              <h2 className="text-3xl font-bold text-gray-900">启航AI留学规划师</h2>
            </div>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-8">
              体验最先进的AI驱动留学咨询服务，获得个性化的申请指导和专业建议
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 items-center">
            {/* Features */}
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <svg className="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">智能学校推荐</h3>
                  <p className="text-gray-600 text-sm">基于您的背景和偏好，AI为您推荐最匹配的学校和专业</p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <svg className="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">引路人匹配</h3>
                  <p className="text-gray-600 text-sm">AI帮您找到最合适的学长学姐导师，获得一对一指导</p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <svg className="h-5 w-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">申请时间规划</h3>
                  <p className="text-gray-600 text-sm">制定详细的申请时间表，确保不错过任何重要截止日期</p>
                </div>
              </div>
            </div>

            {/* CTA */}
            <div className="bg-white rounded-2xl p-8 shadow-lg border">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-primary to-primary/70 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="h-8 w-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8.5 3h7c.28 0 .5.22.5.5v8c0 .28-.22.5-.5.5h-7c-.28 0-.5-.22-.5-.5v-8c0-.28.22-.5.5-.5z"/>
                    <path d="M15 13.5v5c0 .28-.22.5-.5.5h-6c-.28 0-.5-.22-.5-.5v-5"/>
                    <circle cx="9" cy="16" r="1"/>
                    <circle cx="15" cy="16" r="1"/>
                    <path d="M9 20v1m6-1v1"/>
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">立即体验AI咨询</h3>
                <p className="text-gray-600 mb-6">
                  免费与AI留学规划师对话，获得专业的申请建议
                </p>
                <a 
                  href="/ai-advisor"
                  className="inline-flex items-center gap-2 bg-gradient-to-r from-primary to-primary/80 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-200 transform hover:scale-105"
                >
                  开始对话
                  <ChevronRight className="h-4 w-4" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Popular Areas Section */}
      <section className="py-16 bg-gray-50 ">
        <div className="w-full max-w-6xl mx-auto px-4">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              热门留学区域
            </h2>
            <p className="text-gray-600 text-base">
              探索全球最受欢迎的留学目的地
            </p>
          </div>

          <div className="relative">
            <div className="flex gap-4 overflow-x-auto scrollbar-hide pb-4">
              {destinations.map((destination, index) => (
                <div
                  key={index}
                  className="flex-shrink-0 w-64 cursor-pointer group"
                >
                  <div className="relative overflow-hidden rounded-lg mb-3">
                    <Image
                      src={destination.image}
                      alt={destination.name}
                      width={256}
                      height={192}
                      className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 text-lg mb-1">
                      {destination.name}
                    </h3>
                    <p className="text-gray-600 text-sm">
                      {destination.properties}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <button className="absolute right-0 top-1/2 -translate-y-1/2 bg-white rounded-full p-2 shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <ChevronRight className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>
      </section>

      {/* Popular Schools Section */}
      <section className="py-16 bg-white">
        <div className="w-full max-w-6xl mx-auto px-4">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">热门学校</h2>
            <p className="text-gray-600 text-base">世界顶尖院校申请专业指导</p>
          </div>

          <div className="relative">
            <div className="flex gap-4 overflow-x-auto scrollbar-hide pb-4">
              {popularSchools.map((school, index) => (
                <div
                  key={index}
                  className="flex-shrink-0 w-48 cursor-pointer group"
                >
                  <div className="relative overflow-hidden rounded-lg mb-3">
                    <Image
                      src={school.image}
                      alt={school.name}
                      width={192}
                      height={128}
                      className="w-full h-32 object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 text-base mb-1">
                      {school.name}
                    </h3>
                    <p className="text-gray-500 text-sm mb-1">
                      {school.location}
                    </p>
                    <p className="text-gray-600 text-sm">{school.tutors}</p>
                  </div>
                </div>
              ))}
            </div>

            <button className="absolute right-0 top-1/2 -translate-y-1/2 bg-white rounded-full p-2 shadow-lg border border-gray-200 hover:shadow-xl transition-shadow">
              <ChevronRight className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

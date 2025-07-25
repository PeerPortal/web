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

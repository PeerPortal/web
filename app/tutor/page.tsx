'use client';

import { useMemo, Suspense, useState, useEffect } from 'react';
import { useQueryState } from 'nuqs';
import Link from 'next/link';
import {
  Search,
  Star,
  MapPin,
  DollarSign,
  Languages,
  Award,
  Loader2
} from 'lucide-react';
import SearchField from '@/components/search-field';
import TutorFilterSidebar from '@/components/tutor-filter-sidebar';
import { searchMentors, type MentorPublic } from '@/lib/api';

interface Tutor {
  id: number;
  name: string;
  avatar: string;
  university: string;
  degree: string;
  major: string;
  specializations: string[];
  experience: number;
  rating: number;
  reviews: number;
  price: number;
  location: string;
  bio: string;
  languages: string[];
  achievements: string[];
  available: boolean;
}

// 解析导师标题，提取大学和专业信息
function parseMentorTitle(title: string): {
  university: string;
  major: string;
  degree: string;
} {
  // 标题格式："北京大学 计算机科学 导师" 或 "斯坦福 计算机科学 导师" 或 "雅思口语专家"
  const parts = title.split(' ').filter(part => part.trim() !== '');

  let university = 'Unknown University';
  let major = 'Unknown Major';
  let degree = 'Unknown Degree';

  if (parts.length >= 3 && parts[2] === '导师') {
    // 格式: "大学 专业 导师"
    university = parts[0];
    major = parts[1];
  } else if (parts.length >= 2) {
    // 其他格式，尝试推断
    if (
      parts[0].includes('大学') ||
      parts[0].includes('Stanford') ||
      parts[0].includes('斯坦福')
    ) {
      university = parts[0];
      if (parts[1] !== '导师') {
        major = parts[1];
      }
    } else {
      // 可能是专业名称，如"雅思口语专家"
      major = parts.join(' ');
    }
  } else if (parts.length === 1) {
    // 单个词，当作专业处理
    major = parts[0];
  }

  // 简单的学位推断
  if (university.includes('大学')) {
    degree = 'Bachelor';
  } else if (
    university.toLowerCase().includes('stanford') ||
    university.includes('斯坦福')
  ) {
    degree = 'Master';
  } else if (major.includes('专家')) {
    degree = 'Expert';
  }

  return { university, major, degree };
}

function TutorSearchContent() {
  const [searchTerm, setSearchTerm] = useQueryState('q', {
    defaultValue: ''
  });
  const [selectedMajors, setSelectedMajors] = useQueryState('majors', {
    defaultValue: [] as string[],
    serialize: value => (value.length > 0 ? value.join(',') : ''),
    parse: value => (value ? value.split(',').filter(Boolean) : [])
  });
  const [selectedUniversities, setSelectedUniversities] = useQueryState(
    'universities',
    {
      defaultValue: [] as string[],
      serialize: value => (value.length > 0 ? value.join(',') : ''),
      parse: value => (value ? value.split(',').filter(Boolean) : [])
    }
  );
  const [selectedLanguages, setSelectedLanguages] = useQueryState('languages', {
    defaultValue: [] as string[],
    serialize: value => (value.length > 0 ? value.join(',') : ''),
    parse: value => (value ? value.split(',').filter(Boolean) : [])
  });
  const [priceRange, setPriceRange] = useQueryState('price', {
    defaultValue: [0, 300] as [number, number],
    serialize: value => `${value[0]}-${value[1]}`,
    parse: value => {
      if (!value) return [0, 300] as [number, number];
      const [min, max] = value.split('-').map(Number);
      return [min || 0, max || 300] as [number, number];
    }
  });

  const [mentors, setMentors] = useState<MentorPublic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch mentors from backend
  useEffect(() => {
    const fetchMentors = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await searchMentors({
          search_query: searchTerm || undefined,
          limit: 50,
          offset: 0
        });
        setMentors(data);
      } catch (err) {
        setError('Failed to load mentors. Please try again later.');
        console.error('Error fetching mentors:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMentors();
  }, [searchTerm]);

  // Transform backend data to match frontend Tutor interface
  const tutors: Tutor[] = useMemo(() => {
    return mentors.map((mentor): Tutor => {
      const { university, major, degree } = parseMentorTitle(mentor.title);

      return {
        id: mentor.mentor_id || mentor.id,
        name: mentor.title || `Mentor ${mentor.mentor_id || mentor.id}`,
        avatar: '',
        university,
        degree,
        major,
        specializations: mentor.description ? [mentor.description] : [],
        experience: Math.floor((mentor.sessions_completed || 0) / 10),
        rating: mentor.rating || 4.5,
        reviews: mentor.sessions_completed || 0,
        price: mentor.hourly_rate || 100,
        location: 'Online',
        bio:
          mentor.description ||
          'Experienced mentor ready to help you achieve your goals.',
        languages: ['English', 'Chinese'],
        achievements: [`${mentor.sessions_completed || 0} sessions completed`],
        available: true
      };
    });
  }, [mentors]);

  // Get unique values for filters
  const allMajors = Array.from(
    new Set(tutors.flatMap(tutor => tutor.specializations))
  );
  const allUniversities = Array.from(
    new Set(tutors.map(tutor => tutor.university))
  );
  const allLanguages = Array.from(
    new Set(tutors.flatMap(tutor => tutor.languages))
  );

  // Filter tutors based on search criteria
  const filteredTutors = useMemo(() => {
    return tutors.filter(tutor => {
      const matchesSearch =
        searchTerm === '' ||
        tutor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tutor.specializations.some(spec =>
          spec.toLowerCase().includes(searchTerm.toLowerCase())
        ) ||
        tutor.university.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tutor.major.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesMajors =
        selectedMajors.length === 0 ||
        selectedMajors.some(
          major =>
            tutor.major.toLowerCase().includes(major.toLowerCase()) ||
            tutor.specializations.some(spec =>
              spec.toLowerCase().includes(major.toLowerCase())
            )
        );

      const matchesUniversities =
        selectedUniversities.length === 0 ||
        selectedUniversities.some(university =>
          tutor.university.toLowerCase().includes(university.toLowerCase())
        );

      const matchesLanguages =
        selectedLanguages.length === 0 ||
        selectedLanguages.some(lang => tutor.languages.includes(lang));

      const matchesPrice =
        tutor.price >= priceRange[0] && tutor.price <= priceRange[1];

      return (
        matchesSearch &&
        matchesMajors &&
        matchesUniversities &&
        matchesLanguages &&
        matchesPrice
      );
    });
  }, [
    tutors,
    searchTerm,
    selectedMajors,
    selectedUniversities,
    selectedLanguages,
    priceRange
  ]);

  const handleMajorsChange = (majors: string[]) => {
    setSelectedMajors(majors);
  };

  const handleUniversitiesChange = (universities: string[]) => {
    setSelectedUniversities(universities);
  };

  const handleLanguagesChange = (languages: string[]) => {
    setSelectedLanguages(languages);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">加载导师列表中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Bar */}
        <div className="w-full mb-6">
          <SearchField
            initialValue={searchTerm}
            onSearch={setSearchTerm}
            showSuggestions={false}
          />
        </div>

        {/* Main Content with Sidebar */}
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Filter Sidebar */}
          <TutorFilterSidebar
            allMajors={allMajors}
            allUniversities={allUniversities}
            allLanguages={allLanguages}
            selectedMajors={selectedMajors}
            selectedUniversities={selectedUniversities}
            selectedLanguages={selectedLanguages}
            priceRange={priceRange}
            onMajorsChange={handleMajorsChange}
            onUniversitiesChange={handleUniversitiesChange}
            onLanguagesChange={handleLanguagesChange}
            onPriceChange={setPriceRange}
            tutors={tutors}
            filteredTutorCount={filteredTutors.length}
          />

          {/* Content Area */}
          <div className="flex-1">
            {/* Results Count */}
            <div className="mb-4">
              <p className="text-gray-600">
                找到 {filteredTutors.length} 位导师
              </p>
            </div>

            {/* Tutors Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2  gap-6">
              {filteredTutors.map(tutor => (
                <Link
                  key={tutor.id}
                  href={`/tutor/${tutor.id}`}
                  className="block border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 hover:border-blue-300"
                >
                  {/* Tutor Header */}
                  <div className="flex items-start gap-4 mb-4">
                    <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                      {tutor.name.charAt(0)}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 text-lg">
                        {tutor.name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {tutor.university}
                      </p>
                      <p className="text-sm text-gray-500">{tutor.degree}</p>
                    </div>
                    <div
                      className={`px-2 py-1 rounded-full text-xs font-medium ${tutor.available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}
                    >
                      {tutor.available ? '可预约' : '忙碌中'}
                    </div>
                  </div>

                  {/* Rating and Reviews */}
                  <div className="flex items-center gap-2 mb-3">
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                      <span className="font-semibold">{tutor.rating}</span>
                    </div>
                    <span className="text-gray-500 text-sm">
                      ({tutor.reviews} 评价)
                    </span>
                    <span className="text-gray-300">•</span>
                    <span className="text-gray-600 text-sm">
                      {tutor.experience}年经验
                    </span>
                  </div>

                  {/* Specializations */}
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-1">
                      {tutor.specializations.slice(0, 3).map(spec => (
                        <span
                          key={spec}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                        >
                          {spec}
                        </span>
                      ))}
                      {tutor.specializations.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          +{tutor.specializations.length - 3}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Bio */}
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                    {tutor.bio}
                  </p>

                  {/* Details */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <MapPin className="w-4 h-4" />
                      {tutor.location}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Languages className="w-4 h-4" />
                      {tutor.languages.join(', ')}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Award className="w-4 h-4" />
                      {tutor.achievements[0]}
                    </div>
                  </div>

                  {/* Price and Action */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <div className="flex items-center gap-1">
                      <DollarSign className="w-4 h-4 text-green-600" />
                      <span className="font-bold text-green-600">
                        ${tutor.price}/小时
                      </span>
                    </div>
                    <button
                      className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                        tutor.available
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      }`}
                      disabled={!tutor.available}
                      onClick={e => {
                        e.preventDefault();
                        e.stopPropagation();
                        // TODO: Implement booking functionality
                      }}
                    >
                      {tutor.available ? '立即预约' : '暂不可约'}
                    </button>
                  </div>
                </Link>
              ))}
            </div>

            {/* No Results */}
            {filteredTutors.length === 0 && (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-2">
                  <Search className="w-12 h-12 mx-auto" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  未找到匹配的导师
                </h3>
                <p className="text-gray-600">请尝试调整搜索条件或筛选器</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function TutorSearch() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-white flex items-center justify-center">
          加载中...
        </div>
      }
    >
      <TutorSearchContent />
    </Suspense>
  );
}

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
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert } from '@/components/ui/alert';
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
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">加载导师列表中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Alert className="mb-4 max-w-md">
            <p className="text-destructive">{error}</p>
          </Alert>
          <Button onClick={() => window.location.reload()}>重试</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
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
              <p className="text-muted-foreground">
                找到 {filteredTutors.length} 位导师
              </p>
            </div>

            {/* Tutors Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredTutors.map(tutor => (
                <Link key={tutor.id} href={`/tutor/${tutor.id}`}>
                  <div className="border border-border rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 cursor-pointer h-full">
                    {/* Tutor Header */}
                    <div className="flex items-start gap-4 mb-4">
                      <div className="w-16 h-16 flex-shrink-0 bg-gradient-to-r from-pink-500 to-red-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                        {tutor.name.charAt(0)}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-foreground text-lg truncate">
                          {tutor.name}
                        </h3>
                        <p className="text-sm text-muted-foreground truncate">
                          {tutor.university}
                        </p>
                        <p className="text-sm text-muted-foreground truncate">
                          {tutor.degree}
                        </p>
                      </div>
                      <Badge
                        variant={tutor.available ? 'default' : 'secondary'}
                        className={
                          tutor.available
                            ? 'bg-green-100 text-green-800 hover:bg-green-200'
                            : ''
                        }
                      >
                        {tutor.available ? '可预约' : '忙碌中'}
                      </Badge>
                    </div>
                    {/* Rating and Reviews */}
                    <div className="flex items-center gap-2 mb-3">
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                        <span className="font-semibold">{tutor.rating}</span>
                      </div>
                      <span className="text-muted-foreground text-sm">
                        ({tutor.reviews} 评价)
                      </span>
                      <span className="text-muted-foreground">•</span>
                      <span className="text-muted-foreground text-sm">
                        {tutor.experience}年经验
                      </span>
                    </div>

                    {/* Specializations */}
                    <div className="mb-4">
                      <div className="flex flex-wrap gap-1">
                        {tutor.specializations.slice(0, 3).map(spec => (
                          <Badge
                            key={spec}
                            variant="secondary"
                            className="text-xs"
                          >
                            {spec}
                          </Badge>
                        ))}
                        {tutor.specializations.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{tutor.specializations.length - 3}
                          </Badge>
                        )}
                      </div>
                    </div>

                    {/* Bio */}
                    <p className="text-muted-foreground text-sm mb-4 line-clamp-2">
                      {tutor.bio}
                    </p>

                    {/* Details */}
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <MapPin className="w-4 h-4" />
                        {tutor.location}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Languages className="w-4 h-4" />
                        {tutor.languages.join(', ')}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Award className="w-4 h-4" />
                        {tutor.achievements[0]}
                      </div>
                    </div>

                    {/* Price and Action */}
                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center gap-1">
                        <span className="font-bold text-green-600">
                          ${tutor.price}/小时
                        </span>
                      </div>
                      <Button
                        size="sm"
                        disabled={!tutor.available}
                        onClick={e => {
                          e.preventDefault();
                          e.stopPropagation();
                          // TODO: Implement booking functionality
                        }}
                      >
                        {tutor.available ? '立即预约' : '暂不可约'}
                      </Button>
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* No Results */}
            {filteredTutors.length === 0 && (
              <div className="border border-border rounded-lg text-center py-12">
                <div className="text-muted-foreground mb-2">
                  <Search className="w-12 h-12 mx-auto" />
                </div>
                <h3 className="text-lg font-medium text-foreground mb-2">
                  未找到匹配的导师
                </h3>
                <p className="text-muted-foreground">
                  请尝试调整搜索条件或筛选器
                </p>
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
        <div className="min-h-screen bg-background flex items-center justify-center">
          <p className="text-muted-foreground">加载中...</p>
        </div>
      }
    >
      <TutorSearchContent />
    </Suspense>
  );
}

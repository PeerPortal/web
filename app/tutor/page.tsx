'use client';

import { useMemo, Suspense } from 'react';
import { useQueryState } from 'nuqs';
import Link from 'next/link';
import {
  Search,
  Star,
  MapPin,
  DollarSign,
  Languages,
  Award
} from 'lucide-react';
import tutorsData from '@/data/tutors.json';
import SearchField from '@/components/search-field';
import TutorFilterSidebar from '@/components/tutor-filter-sidebar';

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

  const tutors: Tutor[] = tutorsData;

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
        tutor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tutor.specializations.some(spec =>
          spec.toLowerCase().includes(searchTerm.toLowerCase())
        ) ||
        tutor.university.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesMajors =
        selectedMajors.length === 0 ||
        selectedMajors.some(major => tutor.specializations.includes(major));

      const matchesUniversities =
        selectedUniversities.length === 0 ||
        selectedUniversities.includes(tutor.university);

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

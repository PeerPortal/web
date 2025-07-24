'use client';

import { useState, useMemo } from 'react';
import {
  Search,
  Filter,
  Star,
  MapPin,
  DollarSign,
  Languages,
  Award
} from 'lucide-react';
import tutorsData from '@/data/tutors.json';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

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

export default function TutorSearch() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMajors, setSelectedMajors] = useState<string[]>([]);
  const [selectedUniversities, setSelectedUniversities] = useState<string[]>(
    []
  );
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>([]);
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 300]);
  const [showFilters, setShowFilters] = useState(false);

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

  const handleMajorToggle = (major: string) => {
    setSelectedMajors(prev =>
      prev.includes(major) ? prev.filter(m => m !== major) : [...prev, major]
    );
  };

  const handleUniversityToggle = (university: string) => {
    setSelectedUniversities(prev =>
      prev.includes(university)
        ? prev.filter(u => u !== university)
        : [...prev, university]
    );
  };

  const handleLanguageToggle = (language: string) => {
    setSelectedLanguages(prev =>
      prev.includes(language)
        ? prev.filter(l => l !== language)
        : [...prev, language]
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            留学导师搜索
          </h1>
          <p className="text-gray-600 text-lg">寻找最适合的美国本科申请导师</p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Bar */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <div className="flex gap-4">
            <div className="*:not-first:mt-2">
              <Input type="search" placeholder="搜索导师姓名、专业或大学..." />
            </div>
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="搜索导师姓名、专业或大学..."
                className="w-full pl-12 pr-4 py-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base"
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-8 py-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium"
            >
              <Filter className="w-5 h-5" />
              筛选
            </button>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="bg-white rounded-xl shadow-sm p-8 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {/* Major Filter */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-4 text-base">
                  专业领域
                </h3>
                <div className="space-y-3 max-h-48 overflow-y-auto">
                  {allMajors.map(major => (
                    <label
                      key={major}
                      className="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded"
                    >
                      <input
                        type="checkbox"
                        checked={selectedMajors.includes(major)}
                        onChange={() => handleMajorToggle(major)}
                        className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-2"
                      />
                      <span className="ml-3 text-sm text-gray-700">
                        {major}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* University Filter */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-4 text-base">
                  毕业院校
                </h3>
                <div className="space-y-3 max-h-48 overflow-y-auto">
                  {allUniversities.map(university => (
                    <label
                      key={university}
                      className="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded"
                    >
                      <input
                        type="checkbox"
                        checked={selectedUniversities.includes(university)}
                        onChange={() => handleUniversityToggle(university)}
                        className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-2"
                      />
                      <span className="ml-3 text-sm text-gray-700">
                        {university}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Language Filter */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-4 text-base">
                  授课语言
                </h3>
                <div className="space-y-3 max-h-48 overflow-y-auto">
                  {allLanguages.map(language => (
                    <label
                      key={language}
                      className="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded"
                    >
                      <input
                        type="checkbox"
                        checked={selectedLanguages.includes(language)}
                        onChange={() => handleLanguageToggle(language)}
                        className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-2"
                      />
                      <span className="ml-3 text-sm text-gray-700">
                        {language}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Price Filter */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-4 text-base">
                  价格范围 ($/小时)
                </h3>
                <div className="space-y-4">
                  <div className="relative">
                    <input
                      type="range"
                      min="0"
                      max="300"
                      value={priceRange[1]}
                      onChange={e =>
                        setPriceRange([priceRange[0], parseInt(e.target.value)])
                      }
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                      style={{
                        background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(priceRange[1] / 300) * 100}%, #e5e7eb ${(priceRange[1] / 300) * 100}%, #e5e7eb 100%)`
                      }}
                    />
                  </div>
                  <div className="flex justify-between text-sm text-gray-600 font-medium">
                    <span>$0</span>
                    <span>${priceRange[1]}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results Count */}
        <div className="mb-4">
          <p className="text-gray-600">找到 {filteredTutors.length} 位导师</p>
        </div>

        {/* Tutors Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTutors.map(tutor => (
            <div
              key={tutor.id}
              className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6"
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
                  <p className="text-sm text-gray-600">{tutor.university}</p>
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
                >
                  {tutor.available ? '立即预约' : '暂不可约'}
                </button>
              </div>
            </div>
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
  );
}

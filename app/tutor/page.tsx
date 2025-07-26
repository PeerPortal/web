'use client';

import { useMemo, Suspense, useState, useEffect } from 'react';
import { useQueryState } from 'nuqs';
import Link from 'next/link';
import { Search, Star, MapPin, Briefcase, Award, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import SearchField from '@/components/search-field';
import TutorFilterSidebar from '@/components/tutor-filter-sidebar';
import tutorsData from '@/data/tutors.json';

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
  serviceTypes: string[];
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
  const [selectedServiceTypes, setSelectedServiceTypes] = useQueryState(
    'services',
    {
      defaultValue: [] as string[],
      serialize: value => (value.length > 0 ? value.join(',') : ''),
      parse: value => (value ? value.split(',').filter(Boolean) : [])
    }
  );
  const [priceRange, setPriceRange] = useQueryState('price', {
    defaultValue: [0, 300] as [number, number],
    serialize: value => `${value[0]}-${value[1]}`,
    parse: value => {
      if (!value) return [0, 300] as [number, number];
      const [min, max] = value.split('-').map(Number);
      return [min || 0, max || 300] as [number, number];
    }
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Use mock data
  const tutors: Tutor[] = tutorsData as Tutor[];

  // Get unique values for filters
  const allMajors = Array.from(
    new Set(tutors.flatMap(tutor => tutor.specializations))
  );
  const allUniversities = Array.from(
    new Set(tutors.map(tutor => tutor.university))
  );
  const allServiceTypes = Array.from(
    new Set(tutors.flatMap(tutor => tutor.serviceTypes))
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

      const matchesServiceTypes =
        selectedServiceTypes.length === 0 ||
        selectedServiceTypes.some(service =>
          tutor.serviceTypes.includes(service)
        );

      const matchesPrice =
        tutor.price >= priceRange[0] && tutor.price <= priceRange[1];

      return (
        matchesSearch &&
        matchesMajors &&
        matchesUniversities &&
        matchesServiceTypes &&
        matchesPrice
      );
    });
  }, [
    tutors,
    searchTerm,
    selectedMajors,
    selectedUniversities,
    selectedServiceTypes,
    priceRange
  ]);

  const handleMajorsChange = (majors: string[]) => {
    setSelectedMajors(majors);
  };

  const handleUniversitiesChange = (universities: string[]) => {
    setSelectedUniversities(universities);
  };

  const handleServiceTypesChange = (serviceTypes: string[]) => {
    setSelectedServiceTypes(serviceTypes);
  };

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
            allServiceTypes={allServiceTypes}
            selectedMajors={selectedMajors}
            selectedUniversities={selectedUniversities}
            selectedServiceTypes={selectedServiceTypes}
            priceRange={priceRange}
            onMajorsChange={handleMajorsChange}
            onUniversitiesChange={handleUniversitiesChange}
            onServiceTypesChange={handleServiceTypesChange}
            onPriceChange={setPriceRange}
            tutors={tutors}
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
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
                  <p className="text-muted-foreground">加载导师列表中...</p>
                </div>
              </div>
            ) : (
              <>
                {filteredTutors.length > 0 ? (
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
                              variant={
                                tutor.available ? 'default' : 'secondary'
                              }
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
                              <span className="font-semibold">
                                {tutor.rating}
                              </span>
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
                              <Briefcase className="w-4 h-4" />
                              {tutor.serviceTypes.join(' · ')}
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
                ) : (
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
              </>
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

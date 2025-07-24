'use client';

import MultipleSelector, { Option } from '@/components/ui/multiselect';

interface TutorFilterSidebarProps {
  allMajors: string[];
  allUniversities: string[];
  allLanguages: string[];
  selectedMajors: string[];
  selectedUniversities: string[];
  selectedLanguages: string[];
  priceRange: [number, number];
  onMajorsChange: (majors: string[]) => void;
  onUniversitiesChange: (universities: string[]) => void;
  onLanguagesChange: (languages: string[]) => void;
  onPriceChange: (price: [number, number]) => void;
}

export default function TutorFilterSidebar({
  allMajors,
  allUniversities,
  allLanguages,
  selectedMajors,
  selectedUniversities,
  selectedLanguages,
  priceRange,
  onMajorsChange,
  onUniversitiesChange,
  onLanguagesChange,
  onPriceChange
}: TutorFilterSidebarProps) {
  return (
    <div className="w-full lg:w-64 flex-shrink-0">
      <div className="bg-gray-50 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">筛选</h2>

        {/* Major Filter */}
        <div className="mb-6">
          <h3 className="font-medium text-gray-900 mb-3">专业领域</h3>
          <MultipleSelector
            defaultOptions={allMajors.map(major => ({
              value: major,
              label: major
            }))}
            value={selectedMajors.map(major => ({
              value: major,
              label: major
            }))}
            placeholder="选择专业领域"
            hidePlaceholderWhenSelected
            onChange={(options: Option[]) =>
              onMajorsChange(options.map((opt: Option) => opt.value))
            }
            emptyIndicator={<p className="text-center text-sm">未找到结果</p>}
          />
        </div>

        {/* University Filter */}
        <div className="mb-6">
          <h3 className="font-medium text-gray-900 mb-3">毕业院校</h3>
          <MultipleSelector
            defaultOptions={allUniversities.map(university => ({
              value: university,
              label: university
            }))}
            value={selectedUniversities.map(university => ({
              value: university,
              label: university
            }))}
            placeholder="选择毕业院校"
            hidePlaceholderWhenSelected
            onChange={(options: Option[]) =>
              onUniversitiesChange(options.map((opt: Option) => opt.value))
            }
            emptyIndicator={<p className="text-center text-sm">未找到结果</p>}
          />
        </div>

        {/* Language Filter */}
        <div className="mb-6">
          <h3 className="font-medium text-gray-900 mb-3">授课语言</h3>
          <MultipleSelector
            defaultOptions={allLanguages.map(language => ({
              value: language,
              label: language
            }))}
            value={selectedLanguages.map(language => ({
              value: language,
              label: language
            }))}
            placeholder="选择授课语言"
            hidePlaceholderWhenSelected
            onChange={(options: Option[]) =>
              onLanguagesChange(options.map((opt: Option) => opt.value))
            }
            emptyIndicator={<p className="text-center text-sm">未找到结果</p>}
          />
        </div>

        {/* Price Filter */}
        <div>
          <h3 className="font-medium text-gray-900 mb-3">价格范围 ($/小时)</h3>
          <div className="space-y-4">
            <div className="relative">
              <input
                type="range"
                min="0"
                max="300"
                value={priceRange[1]}
                onChange={e =>
                  onPriceChange([priceRange[0], parseInt(e.target.value)])
                }
                className="w-full h-2 rounded-lg appearance-none cursor-pointer slider"
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
  );
}

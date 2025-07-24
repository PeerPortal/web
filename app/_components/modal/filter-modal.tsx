'use client';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog';
import FilterButton from '@/components/filter-button';

interface FilterModalProps {
  showFilters: boolean;
  setShowFilters: (show: boolean) => void;
  allMajors: string[];
  allUniversities: string[];
  allLanguages: string[];
  selectedMajors: string[];
  selectedUniversities: string[];
  selectedLanguages: string[];
  priceRange: [number, number];
  onMajorToggle: (major: string) => void;
  onUniversityToggle: (university: string) => void;
  onLanguageToggle: (language: string) => void;
  onPriceRangeChange: (range: [number, number]) => void;
}

export default function FilterModal({
  showFilters,
  setShowFilters,
  allMajors,
  allUniversities,
  allLanguages,
  selectedMajors,
  selectedUniversities,
  selectedLanguages,
  priceRange,
  onMajorToggle,
  onUniversityToggle,
  onLanguageToggle,
  onPriceRangeChange
}: FilterModalProps) {
  return (
    <Dialog open={showFilters} onOpenChange={setShowFilters}>
      <DialogTrigger asChild>
        <FilterButton
          showFilters={showFilters}
          setShowFilters={setShowFilters}
        />
      </DialogTrigger>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>筛选选项</DialogTitle>
        </DialogHeader>
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
                    onChange={() => onMajorToggle(major)}
                    className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-2"
                  />
                  <span className="ml-3 text-sm text-gray-700">{major}</span>
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
                    onChange={() => onUniversityToggle(university)}
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
                    onChange={() => onLanguageToggle(language)}
                    className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-2"
                  />
                  <span className="ml-3 text-sm text-gray-700">{language}</span>
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
                    onPriceRangeChange([
                      priceRange[0],
                      parseInt(e.target.value)
                    ])
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
      </DialogContent>
    </Dialog>
  );
}

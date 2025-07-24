'use client';

import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog';
import FilterButton from '@/components/filter-button';
import MultipleSelector, { Option } from '@/components/ui/multiselect';
import { Button } from '@/components/ui/button';

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
  onMajorsChange: (majors: string[]) => void;
  onUniversitiesChange: (universities: string[]) => void;
  onLanguagesChange: (languages: string[]) => void;
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
  onMajorsChange,
  onUniversitiesChange,
  onLanguagesChange,
  onPriceRangeChange
}: FilterModalProps) {
  const majorOptions: Option[] = allMajors.map(major => ({
    value: major,
    label: major
  }));

  const universityOptions: Option[] = allUniversities.map(university => ({
    value: university,
    label: university
  }));

  const languageOptions: Option[] = allLanguages.map(language => ({
    value: language,
    label: language
  }));

  const selectedMajorOptions: Option[] = selectedMajors.map(major => ({
    value: major,
    label: major
  }));

  const selectedUniversityOptions: Option[] = selectedUniversities.map(
    university => ({
      value: university,
      label: university
    })
  );

  const selectedLanguageOptions: Option[] = selectedLanguages.map(language => ({
    value: language,
    label: language
  }));
  return (
    <Dialog open={showFilters} onOpenChange={setShowFilters}>
      <DialogTrigger asChild>
        <FilterButton
          showFilters={showFilters}
          setShowFilters={setShowFilters}
        />
      </DialogTrigger>
      <DialogContent className="flex flex-col gap-0 p-0 sm:max-h-[min(640px,80vh)] sm:max-w-lg [&>button:last-child]:hidden">
        <DialogHeader>
          <DialogTitle className="px-6 py-6 border-b">筛选选项</DialogTitle>
        </DialogHeader>
        <div className="overflow-y-auto">
          <DialogDescription asChild>
            <div className="px-6 py-6">
              <div className="flex flex-col gap-6">
                {/* Major Filter */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-4 text-base">
                    专业领域
                  </h3>
                  <MultipleSelector
                    defaultOptions={majorOptions}
                    value={selectedMajorOptions}
                    placeholder="选择专业领域"
                    hidePlaceholderWhenSelected
                    onChange={(options: Option[]) =>
                      onMajorsChange(options.map((opt: Option) => opt.value))
                    }
                    emptyIndicator={
                      <p className="text-center text-sm">未找到结果</p>
                    }
                  />
                </div>

                {/* University Filter */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-4 text-base">
                    毕业院校
                  </h3>
                  <MultipleSelector
                    defaultOptions={universityOptions}
                    value={selectedUniversityOptions}
                    placeholder="选择毕业院校"
                    hidePlaceholderWhenSelected
                    onChange={(options: Option[]) =>
                      onUniversitiesChange(
                        options.map((opt: Option) => opt.value)
                      )
                    }
                    emptyIndicator={
                      <p className="text-center text-sm">未找到结果</p>
                    }
                  />
                </div>

                {/* Language Filter */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-4 text-base">
                    授课语言
                  </h3>
                  <MultipleSelector
                    defaultOptions={languageOptions}
                    value={selectedLanguageOptions}
                    placeholder="选择授课语言"
                    hidePlaceholderWhenSelected
                    onChange={(options: Option[]) =>
                      onLanguagesChange(options.map((opt: Option) => opt.value))
                    }
                    emptyIndicator={
                      <p className="text-center text-sm">未找到结果</p>
                    }
                  />
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
            </div>
          </DialogDescription>
        </div>
        <DialogFooter className="border-t px-6 py-4">
          <DialogClose asChild>
            <Button type="button" variant="outline">
              Cancel
            </Button>
          </DialogClose>
          <DialogClose asChild>
            <Button type="button">Show Results</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

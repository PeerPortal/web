'use client';

import { useId } from 'react';
import MultipleSelector, { Option } from '@/components/ui/multiselect';
import { useSliderWithInput } from '@/hooks/use-slider-with-input';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';

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
  tutors: Tutor[];
  filteredTutorCount: number;
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
  onPriceChange,
  tutors,
  filteredTutorCount
}: TutorFilterSidebarProps) {
  const id = useId();

  // Find the min and max prices across all tutors
  const minValue = 0;
  const maxValue = 300;

  const {
    sliderValue,
    inputValues,
    validateAndUpdateValue,
    handleInputChange,
    handleSliderChange
  } = useSliderWithInput({
    minValue,
    maxValue,
    initialValue: priceRange,
    defaultValue: [minValue, maxValue]
  });

  // Update parent component when slider values change
  const handleSliderValueChange = (values: number[]) => {
    handleSliderChange(values);
    onPriceChange(values as [number, number]);
  };

  // Function to count tutors in the current price range
  const countTutorsInRange = (min: number, max: number) => {
    return tutors.filter(tutor => tutor.price >= min && tutor.price <= max)
      .length;
  };
  return (
    <div className="w-full lg:w-64 flex-shrink-0">
      <div className="border border-gray-200 rounded-lg p-6">
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
            <Slider
              value={sliderValue}
              onValueChange={handleSliderValueChange}
              min={minValue}
              max={maxValue}
              className="w-full"
              aria-label="价格范围"
            />

            {/* Min and Max Inputs */}
            <div className="flex items-center justify-between gap-3">
              <div className="flex-1">
                <Label htmlFor={`${id}-min`} className="text-xs text-gray-600">
                  最低价格
                </Label>
                <div className="relative">
                  <Input
                    id={`${id}-min`}
                    className="peer w-full pl-6 pr-2 py-1 text-sm"
                    type="text"
                    inputMode="decimal"
                    value={inputValues[0]}
                    onChange={e => handleInputChange(e, 0)}
                    onBlur={() => {
                      validateAndUpdateValue(inputValues[0], 0);
                      onPriceChange([
                        parseInt(inputValues[0]) || minValue,
                        sliderValue[1]
                      ] as [number, number]);
                    }}
                    onKeyDown={e => {
                      if (e.key === 'Enter') {
                        validateAndUpdateValue(inputValues[0], 0);
                        onPriceChange([
                          parseInt(inputValues[0]) || minValue,
                          sliderValue[1]
                        ] as [number, number]);
                      }
                    }}
                    aria-label="输入最低价格"
                  />
                  <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center justify-center pl-2 text-sm text-gray-500 peer-disabled:opacity-50">
                    $
                  </span>
                </div>
              </div>
              <div className="flex-1">
                <Label htmlFor={`${id}-max`} className="text-xs text-gray-600">
                  最高价格
                </Label>
                <div className="relative">
                  <Input
                    id={`${id}-max`}
                    className="peer w-full pl-6 pr-2 py-1 text-sm"
                    type="text"
                    inputMode="decimal"
                    value={inputValues[1]}
                    onChange={e => handleInputChange(e, 1)}
                    onBlur={() => {
                      validateAndUpdateValue(inputValues[1], 1);
                      onPriceChange([
                        sliderValue[0],
                        parseInt(inputValues[1]) || maxValue
                      ] as [number, number]);
                    }}
                    onKeyDown={e => {
                      if (e.key === 'Enter') {
                        validateAndUpdateValue(inputValues[1], 1);
                        onPriceChange([
                          sliderValue[0],
                          parseInt(inputValues[1]) || maxValue
                        ] as [number, number]);
                      }
                    }}
                    aria-label="输入最高价格"
                  />
                  <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center justify-center pl-2 text-sm text-gray-500 peer-disabled:opacity-50">
                    $
                  </span>
                </div>
              </div>
            </div>

            {/* Tutor count display */}
            <div className="text-center text-sm text-gray-600">
              在此价格范围内有{' '}
              <span className="font-medium text-gray-900">
                {countTutorsInRange(sliderValue[0], sliderValue[1])}
              </span>{' '}
              位导师
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

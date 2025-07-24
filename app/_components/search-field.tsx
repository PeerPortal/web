'use client';

import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Command,
  CommandGroup,
  CommandItem,
  CommandList
} from '@/components/ui/command';
import { cn } from '@/lib/utils';

interface SearchFieldProps {
  initialValue?: string;
  onSearch?: (value: string) => void;
  showSuggestions?: boolean;
}

interface Suggestion {
  value: string;
  label: string;
  type: 'university' | 'major';
}

export default function SearchField({
  initialValue = '',
  onSearch,
  showSuggestions = true
}: SearchFieldProps) {
  const [searchTerm, setSearchTerm] = useState(initialValue);
  
  // Update internal state when initialValue changes
  useEffect(() => {
    setSearchTerm(initialValue);
  }, [initialValue]);
  const [open, setOpen] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState<Suggestion[]>(
    []
  );
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Mock suggestions data
  const mockSuggestions: Suggestion[] = [
    { value: 'harvard', label: '哈佛大学', type: 'university' },
    { value: 'mit', label: '麻省理工学院', type: 'university' },
    { value: 'stanford', label: '斯坦福大学', type: 'university' },
    { value: 'computer-science', label: '计算机科学', type: 'major' },
    { value: 'business-admin', label: '工商管理', type: 'major' },
    { value: 'engineering', label: '工程学', type: 'major' },
    { value: 'medicine', label: '医学', type: 'major' },
    { value: 'economics', label: '经济学', type: 'major' }
  ];

  // Recommended schools to always display
  const recommendedSchools: Suggestion[] = [
    { value: 'harvard', label: '哈佛大学', type: 'university' },
    { value: 'mit', label: '麻省理工学院', type: 'university' },
    { value: 'stanford', label: '斯坦福大学', type: 'university' },
    { value: 'yale', label: '耶鲁大学', type: 'university' },
    { value: 'princeton', label: '普林斯顿大学', type: 'university' }
  ];

  useEffect(() => {
    // Filter suggestions based on search term
    if (searchTerm.length > 0) {
      const filtered = mockSuggestions.filter(item =>
        item.label.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredSuggestions(filtered);
    } else {
      setFilteredSuggestions([]);
    }
  }, [searchTerm]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    };

    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [open]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchTerm.trim()) {
      setOpen(false);
      if (onSearch) {
        onSearch(searchTerm);
      } else {
        router.push(`/tutor?q=${encodeURIComponent(searchTerm.trim())}`);
      }
    } else if (e.key === 'Escape') {
      setOpen(false);
      inputRef.current?.blur();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    if (showSuggestions) {
      setOpen(true);
    }
    // Immediately update query parameter when typing
    if (onSearch) {
      onSearch(value);
    }
  };

  const handleSelectSuggestion = (suggestion: Suggestion) => {
    setSearchTerm(suggestion.label);
    setOpen(false);
    if (onSearch) {
      onSearch(suggestion.label);
    } else {
      router.push(`/tutor?q=${encodeURIComponent(suggestion.label)}`);
    }
  };

  return (
    <div className="max-w-2xl align-start w-full">
      <div className="relative">
        <Input
          ref={inputRef}
          type="search"
          placeholder="搜索专业或大学..."
          className="w-full py-6 px-4 text-base"
          value={searchTerm}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onFocus={() => showSuggestions && setOpen(true)}
        />
        <div className="text-muted-foreground/80 pointer-events-none absolute inset-y-0 end-0 flex items-center justify-center pe-3 peer-disabled:opacity-50">
          <Search size={20} aria-hidden="true" />
        </div>

        {/* Popover with suggestions */}
        {showSuggestions && (
          <div
            ref={dropdownRef}
            className={cn(
              'absolute top-full left-0 right-0 mt-2 z-50 w-full overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md',
              'data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
              !open && 'hidden'
            )}
            data-state={open ? 'open' : 'closed'}
          >
            <Command className="w-full">
              <CommandList className="max-h-[300px] overflow-auto">
                {/* Always show recommended schools */}
                <CommandGroup>
                  {recommendedSchools.map(school => (
                    <CommandItem
                      key={school.value}
                      value={school.value}
                      onSelect={() => handleSelectSuggestion(school)}
                      className="cursor-pointer"
                    >
                      {school.label}
                    </CommandItem>
                  ))}
                </CommandGroup>

                {/* Show search results if there's a search term */}
                {searchTerm.length > 0 && (
                  <>
                    {filteredSuggestions.length > 0 ? (
                      <>
                        {/* Universities group */}
                        {filteredSuggestions.filter(
                          s => s.type === 'university'
                        ).length > 0 && (
                          <CommandGroup heading="搜索结果 - 大学">
                            {filteredSuggestions
                              .filter(s => s.type === 'university')
                              .map(suggestion => (
                                <CommandItem
                                  key={suggestion.value}
                                  value={suggestion.value}
                                  onSelect={() =>
                                    handleSelectSuggestion(suggestion)
                                  }
                                  className="cursor-pointer"
                                >
                                  {suggestion.label}
                                </CommandItem>
                              ))}
                          </CommandGroup>
                        )}

                        {/* Majors group */}
                        {filteredSuggestions.filter(s => s.type === 'major')
                          .length > 0 && (
                          <CommandGroup heading="搜索结果 - 专业">
                            {filteredSuggestions
                              .filter(s => s.type === 'major')
                              .map(suggestion => (
                                <CommandItem
                                  key={suggestion.value}
                                  value={suggestion.value}
                                  onSelect={() =>
                                    handleSelectSuggestion(suggestion)
                                  }
                                  className="cursor-pointer"
                                >
                                  {suggestion.label}
                                </CommandItem>
                              ))}
                          </CommandGroup>
                        )}
                      </>
                    ) : (
                      <div className="px-3 py-2 text-sm text-muted-foreground">
                        没有找到相关搜索结果
                      </div>
                    )}
                  </>
                )}
              </CommandList>
            </Command>
          </div>
        )}
      </div>
    </div>
  );
}

'use client';

import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface SearchFieldProps {
  initialValue?: string;
  onSearch?: (value: string) => void;
}

export default function SearchField({
  initialValue = '',
  onSearch
}: SearchFieldProps) {
  const [searchTerm, setSearchTerm] = useState(initialValue);
  const router = useRouter();

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchTerm.trim()) {
      if (onSearch) {
        onSearch(searchTerm);
      } else {
        router.push(`/tutor?q=${encodeURIComponent(searchTerm.trim())}`);
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  return (
    <div className="max-w-2xl align-start w-full">
      <div className="relative">
        <Input
          type="search"
          placeholder="搜索导师姓名、专业或大学..."
          className="w-full py-6 px-4 text-base"
          value={searchTerm}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
        />
        <div className="text-muted-foreground/80 pointer-events-none absolute inset-y-0 end-0 flex items-center justify-center pe-3 peer-disabled:opacity-50">
          <Search size={20} aria-hidden="true" />
        </div>
      </div>
    </div>
  );
}

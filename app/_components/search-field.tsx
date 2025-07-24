import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useState } from 'react';

export default function SearchField() {
  const [searchTerm, setSearchTerm] = useState('');
  return (
    <div className="mx-auto max-w-2xl">
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
      <div className="relative">
        <div
          className="text-muted-foreground pointer-events-none absolute inset-y-0 start-0 flex items-start justify-center ps-4 pt-2.5"
          aria-label="Search component"
        >
          <Search size={24} aria-hidden="true" />
        </div>
      </div>
    </div>
  );
}

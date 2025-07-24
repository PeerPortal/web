import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useState } from 'react';

export default function SearchField() {
  const [searchTerm, setSearchTerm] = useState('');
  return (
    <div className="max-w-2xl align-start w-full">
      <div className="relative">
        <Input
          type="search"
          placeholder="搜索导师姓名、专业或大学..."
          className="w-full py-6 px-4 text-base"
        />
        <div className="text-muted-foreground/80 pointer-events-none absolute inset-y-0 end-0 flex items-center justify-center pe-3 peer-disabled:opacity-50">
          <Search size={20} aria-hidden="true" />
        </div>
      </div>
    </div>
  );
}

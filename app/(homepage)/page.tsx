'use client';

import SearchField from '@/components/search-field';

export default function Homepage() {
  return (
    <div className="bg-white flex items-center justify-center">
      <div className="max-w-7xl w-full px-4 sm:px-6 lg:px-8">
        <div className="bg-white">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-14 py-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              留学导师搜索
            </h1>
            <p className="text-gray-600 text-lg">寻找最适合的留学申请导师</p>
            <div className="w-full py-8">
              <SearchField />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

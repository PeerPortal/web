
"use client";
import React, { useEffect, useState } from "react";
import Image from "next/image";

interface CollegeImage {
  id: number;
  image_url: string;
  caption: string;
  sort_order: number;
}

interface College {
  id: number;
  name: string;
  location: string;
  type: string;
  description: string;
  images: CollegeImage[];
}

const fetchColleges = async (): Promise<College[]> => {
  const res = await fetch("/api/colleges", {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
    },
    cache: "no-store",
  });
  if (!res.ok) throw new Error("获取院校列表失败");
  return res.json();
};


export default function CollegePage() {
  const [colleges, setColleges] = useState<College[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchColleges()
      .then(setColleges)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = search.trim()
    ? colleges.filter(c => c.name.includes(search.trim()))
    : colleges;

  if (loading) return <div className="p-8 text-center">加载中...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">院校列表</h1>
      <div className="mb-6 flex items-center gap-2">
        <input
          type="text"
          placeholder="按名称搜索院校..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="border rounded px-3 py-2 w-full max-w-xs focus:outline-none focus:ring"
        />
        <span className="text-gray-400 text-sm">共 {filtered.length} 所</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {filtered.map((college) => (
          <div key={college.id} className="border rounded-lg p-4 shadow-sm bg-white flex flex-col">
            {college.images && college.images.length > 0 && (
              <Image
                src={college.images[0].image_url}
                alt={college.images[0].caption || college.name}
                width={320}
                height={180}
                className="rounded object-cover w-full h-40 mb-2"
              />
            )}
            <h2 className="text-lg font-semibold mb-1 line-clamp-1">{college.name}</h2>
            <div className="text-gray-600 text-sm mb-1">{college.location} · {college.type}</div>
            <div className="text-gray-700 text-sm line-clamp-2 mb-2">{college.description}</div>
          </div>
        ))}
      </div>
      {filtered.length === 0 && (
        <div className="text-center text-gray-400 py-12">未找到相关院校</div>
      )}
    </div>
  );
}

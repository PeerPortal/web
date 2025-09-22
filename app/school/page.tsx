
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

export default function SchoolPage() {
  const [colleges, setColleges] = useState<College[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchColleges()
      .then(setColleges)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-center">加载中...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">院校列表</h1>
      <div className="space-y-8">
        {colleges.map((college) => (
          <div key={college.id} className="border rounded-lg p-4 shadow-sm">
            <h2 className="text-xl font-semibold mb-2">{college.name}</h2>
            <div className="text-gray-600 mb-1">{college.location} · {college.type}</div>
            <div className="mb-2 text-gray-700">{college.description}</div>
            {college.images && college.images.length > 0 && (
              <div className="flex flex-wrap gap-4 mt-2">
                {college.images.sort((a, b) => a.sort_order - b.sort_order).map((img) => (
                  <div key={img.id} className="w-48">
                    <Image
                      src={img.image_url}
                      alt={img.caption || college.name}
                      width={192}
                      height={128}
                      className="rounded object-cover"
                    />
                    {img.caption && <div className="text-xs text-gray-500 mt-1">{img.caption}</div>}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

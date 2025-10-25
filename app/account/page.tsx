"use client";
import React from "react";
import Link from "next/link";
import { useEffect, useState } from "react";
import type { UserProfileResponse } from "../_lib/api";
import { getUserProfile } from "../_lib/api";

export default function AccountPage() {
  const [profile, setProfile] = useState<UserProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    getUserProfile()
      .then((data) => {
        if (mounted) setProfile(data);
      })
      .catch((e) => {
        if (mounted) setError(String(e));
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <main className="max-w-5xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6">个人中心</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
  <aside className="col-span-1 border rounded p-4 bg-card">
          <nav className="space-y-2">
            <Link href="/account" className="block font-medium">概览</Link>
            <Link href="/account/orders" className="block">订单管理</Link>
            <Link href="/account/bookings" className="block">预约管理</Link>
            <Link href="/account/mentors" className="block">我的导师</Link>
            <Link href="/account/profile" className="block">个人资料</Link>
            <Link href="/account/settings" className="block">设置</Link>
          </nav>
        </aside>

        <section className="col-span-3">
          {loading && <div className="p-6 bg-card rounded">加载中...</div>}
          {error && <div className="p-6 bg-red-50 rounded text-red-600">{error}</div>}

          {!loading && !error && (
            <div className="p-6 bg-card rounded">
              <h2 className="text-xl font-semibold mb-2">欢迎{profile?.userId || profile?.id || '用户'}</h2>
              <p className="text-sm text-muted-foreground mb-4">这是你的个人工作台，从左侧菜单管理订单、预约、导师和个人资料。</p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="border rounded p-4">
                  <div className="text-sm text-muted-foreground">订单</div>
                  <div className="text-xl font-bold">—</div>
                </div>
                <div className="border rounded p-4">
                  <div className="text-sm text-muted-foreground">预约</div>
                  <div className="text-xl font-bold">—</div>
                </div>
                <div className="border rounded p-4">
                  <div className="text-sm text-muted-foreground">导师</div>
                  <div className="text-xl font-bold">—</div>
                </div>
                <div className="border rounded p-4">
                  <div className="text-sm text-muted-foreground">个人资料</div>
                  <div className="text-xl font-bold">{profile?.userId || profile?.id || '未填写'}</div>
                </div>
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

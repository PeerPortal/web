'use client';

import { GraduationCap, BookOpen } from 'lucide-react';

export type UserType = 'studying' | 'planning';

interface UserTypeSelectionProps {
  onSelect: (type: UserType) => void;
}

export function UserTypeSelection({ onSelect }: UserTypeSelectionProps) {
  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-2">欢迎来到 AdMIT!</h2>
        <p className="text-muted-foreground">让我们先了解一下您的情况</p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {/* 已经留学的学生 */}
        <div
          onClick={() => onSelect('studying')}
          className="flex w-full items-center gap-3 rounded-md border-2 border-input p-4 outline-none hover:border-primary/50 transition-colors cursor-pointer min-h-[100px]"
        >
          <div className="w-12 h-12 bg-muted rounded-full flex items-center justify-center flex-shrink-0">
            <GraduationCap className="w-6 h-6 text-muted-foreground" />
          </div>
          <div className="flex flex-col gap-1">
            <h3 className="text-base font-medium">已经留学的学生</h3>
            <p className="text-muted-foreground text-sm">
              我已经在国外学习，想要分享经验或寻找同伴
            </p>
          </div>
        </div>

        {/* 准备留学的学生 */}
        <div
          onClick={() => onSelect('planning')}
          className="flex w-full items-center gap-3 rounded-md border-2 border-input p-4 outline-none hover:border-primary/50 transition-colors cursor-pointer min-h-[100px]"
        >
          <div className="w-12 h-12 bg-muted rounded-full flex items-center justify-center flex-shrink-0">
            <BookOpen className="w-6 h-6 text-muted-foreground" />
          </div>
          <div className="flex flex-col gap-1">
            <h3 className="text-base font-medium">准备留学的学生</h3>
            <p className="text-muted-foreground text-sm">
              我正在准备留学，想要了解更多信息和经验
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

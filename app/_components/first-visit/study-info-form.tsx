'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import { ArrowLeft } from 'lucide-react';
import type { UserType, StudyInfo } from '@/hooks/use-first-visit';

interface StudyInfoFormProps {
  userType: UserType;
  onSubmit: (info: StudyInfo) => void;
  onBack: () => void;
}

export function StudyInfoForm({
  userType,
  onSubmit,
  onBack
}: StudyInfoFormProps) {
  const [region, setRegion] = useState('');
  const [school, setSchool] = useState('');
  const [major, setMajor] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (region.trim() && school.trim() && major.trim()) {
      onSubmit({
        userType,
        region: region.trim(),
        school: school.trim(),
        major: major.trim()
      });
    }
  };

  const title = userType === 'studying' ? '您的留学信息' : '您的意向留学信息';
  const description =
    userType === 'studying'
      ? '请填写您当前的留学信息，以便我们为您提供更好的服务'
      : '请填写您的意向留学信息，以便我们为您匹配相关资源';

  return (
    <div className="w-full max-w-xl mx-auto p-6">
      <Button variant="ghost" onClick={onBack} className="mb-4 -ml-2">
        <ArrowLeft className="w-4 h-4 mr-2" />
        返回
      </Button>

      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="region">
                {userType === 'studying' ? '留学地区' : '意向留学地区'}
              </Label>
              <Input
                id="region"
                type="text"
                placeholder="例如：美国、英国、加拿大等"
                value={region}
                onChange={e => setRegion(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="school">
                {userType === 'studying' ? '就读学校' : '意向学校'}
              </Label>
              <Input
                id="school"
                type="text"
                placeholder="例如：哈佛大学、剑桥大学等"
                value={school}
                onChange={e => setSchool(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="major">
                {userType === 'studying' ? '就读专业' : '意向专业'}
              </Label>
              <Input
                id="major"
                type="text"
                placeholder="例如：计算机科学、商业管理等"
                value={major}
                onChange={e => setMajor(e.target.value)}
                required
              />
            </div>

            <Button type="submit" className="w-full" size="lg">
              开始使用 AdMIT
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

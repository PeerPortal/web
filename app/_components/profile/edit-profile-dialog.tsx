'use client';

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Skeleton } from '@/components/ui/skeleton';
import { Edit, Loader2 } from 'lucide-react';
import { User } from '@/lib/api';

interface ProfileUpdateData {
  full_name?: string;
  avatar_url?: string;
  bio?: string;
}

interface EditProfileDialogProps {
  user: User;
  onSave: (updatedData: ProfileUpdateData) => Promise<void>;
  trigger?: React.ReactNode;
}

export type { ProfileUpdateData };

export function EditProfileDialog({
  user,
  onSave,
  trigger
}: EditProfileDialogProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [dataLoading, setDataLoading] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    avatar_url: '',
    bio: ''
  });

  // Load user data when dialog opens
  useEffect(() => {
    if (open && user) {
      setDataLoading(true);
      // Fetch fresh profile data when dialog opens
      import('@/lib/api').then(({ getUserProfile }) => {
        getUserProfile()
          .then(profile => {
            setFormData({
              full_name: profile.full_name || user.full_name || '',
              avatar_url: profile.avatar_url || user.avatar_url || '',
              bio: profile.bio || user.bio || ''
            });
          })
          .catch(err => {
            console.error('Failed to load profile data:', err);
            // Fallback to user data
            setFormData({
              full_name: user.full_name || '',
              avatar_url: user.avatar_url || '',
              bio: user.bio || ''
            });
          })
          .finally(() => {
            setDataLoading(false);
          });
      });
    }
  }, [open, user]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await onSave(formData);
      setOpen(false);
    } catch (error) {
      console.error('Failed to save profile:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Edit className="mr-2 h-4 w-4" />
            编辑个人资料
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>编辑个人资料</DialogTitle>
          <DialogDescription>更新您的个人信息和偏好设置</DialogDescription>
        </DialogHeader>
        <div className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="full_name">真实姓名</Label>
            {dataLoading ? (
              <Skeleton className="h-10 w-full" />
            ) : (
              <Input
                id="full_name"
                value={formData.full_name}
                onChange={e => handleInputChange('full_name', e.target.value)}
                placeholder="输入您的真实姓名"
              />
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="avatar_url">头像URL</Label>
            {dataLoading ? (
              <Skeleton className="h-10 w-full" />
            ) : (
              <Input
                id="avatar_url"
                type="url"
                value={formData.avatar_url}
                onChange={e => handleInputChange('avatar_url', e.target.value)}
                placeholder="输入头像图片链接"
              />
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="bio">个人简介</Label>
            {dataLoading ? (
              <Skeleton className="h-24 w-full" />
            ) : (
              <Textarea
                id="bio"
                value={formData.bio}
                onChange={e => handleInputChange('bio', e.target.value)}
                placeholder="介绍一下您自己..."
                rows={4}
              />
            )}
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSave} disabled={loading || dataLoading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  保存中...
                </>
              ) : (
                '保存'
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

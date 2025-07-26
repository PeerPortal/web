'use client';

import { useState, useEffect, useRef } from 'react';
import Image from 'next/image';
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
import { Edit, Loader2, Camera, Upload } from 'lucide-react';
import { User } from '@/lib/api';
import { uploadUserAvatar } from '@/lib/api';

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
  const [avatarUploading, setAvatarUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
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

  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      alert('请上传 JPG, PNG, GIF 或 WEBP 格式的图片');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('图片文件大小不能超过 5MB');
      return;
    }

    setAvatarUploading(true);
    try {
      const result = await uploadUserAvatar(file);
      setFormData(prev => ({
        ...prev,
        avatar_url: result.avatar_url
      }));
    } catch (error) {
      console.error('Avatar upload failed:', error);
      alert('头像上传失败，请重试');
    } finally {
      setAvatarUploading(false);
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
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
            <Label>头像</Label>
            {dataLoading ? (
              <Skeleton className="h-32 w-full" />
            ) : (
              <div className="space-y-4">
                {/* Current Avatar Preview */}
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <div className="w-20 h-20 rounded-full overflow-hidden bg-gray-100 border-2 border-gray-200">
                      {formData.avatar_url ? (
                        <Image
                          src={formData.avatar_url.startsWith('/static') 
                            ? `https://web-4w0h.onrender.com${formData.avatar_url}` 
                            : formData.avatar_url
                          }
                          alt="Avatar"
                          width={80}
                          height={80}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.src = '/api/placeholder/80/80';
                          }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                          <Camera className="w-8 h-8" />
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex-1">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleUploadClick}
                      disabled={avatarUploading}
                      className="w-full"
                    >
                      {avatarUploading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          上传中...
                        </>
                      ) : (
                        <>
                          <Upload className="w-4 h-4 mr-2" />
                          上传新头像
                        </>
                      )}
                    </Button>
                    <p className="text-xs text-gray-500 mt-1">
                      支持 JPG, PNG, GIF, WEBP 格式，文件大小不超过 5MB
                    </p>
                  </div>
                </div>
                
                {/* Hidden File Input */}
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleAvatarUpload}
                  accept="image/jpeg,image/png,image/gif,image/webp"
                  className="hidden"
                />
                
                {/* Manual URL Input (Alternative) */}
                <div className="border-t pt-4">
                  <Label htmlFor="avatar_url" className="text-sm text-gray-600">
                    或输入图片链接
                  </Label>
                  <Input
                    id="avatar_url"
                    type="url"
                    value={formData.avatar_url}
                    onChange={e => handleInputChange('avatar_url', e.target.value)}
                    placeholder="https://example.com/avatar.jpg"
                    className="mt-1"
                  />
                </div>
              </div>
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
                  <Loader2 className="h-4 w-4 animate-spin" />
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

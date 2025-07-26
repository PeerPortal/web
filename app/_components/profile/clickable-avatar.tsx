'use client';

import { useState, useRef } from 'react';
import { Camera, Loader2 } from 'lucide-react';
import { uploadUserAvatar } from '@/lib/api';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';

interface ClickableAvatarProps {
  src?: string;
  alt?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  fallback?: string;
  onAvatarUpdate?: (newAvatarUrl: string) => void;
  className?: string;
  showUploadOverlay?: boolean;
}

const sizeClasses = {
  sm: 'size-8',
  md: 'size-12',
  lg: 'size-16',
  xl: 'size-20'
};

export function ClickableAvatar({
  src,
  alt = 'Avatar',
  size = 'lg',
  fallback = '?',
  onAvatarUpdate,
  className,
  showUploadOverlay = true
}: ClickableAvatarProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [currentSrc, setCurrentSrc] = useState(src);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAvatarClick = () => {
    if (showUploadOverlay && onAvatarUpdate) {
      fileInputRef.current?.click();
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
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

    setIsUploading(true);
    try {
      const result = await uploadUserAvatar(file);
      const newAvatarUrl = result.avatar_url.startsWith('/static') 
        ? `https://web-4w0h.onrender.com${result.avatar_url}` 
        : result.avatar_url;
      
      setCurrentSrc(newAvatarUrl);
      onAvatarUpdate?.(result.avatar_url);
    } catch (error) {
      console.error('Avatar upload failed:', error);
      alert('头像上传失败，请重试');
    } finally {
      setIsUploading(false);
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const avatarSrc = currentSrc?.startsWith('/static') 
    ? `https://web-4w0h.onrender.com${currentSrc}` 
    : currentSrc;

  return (
    <div className="relative">
      <Avatar 
        className={cn(
          sizeClasses[size],
          showUploadOverlay && onAvatarUpdate && 'cursor-pointer hover:opacity-80 transition-opacity',
          className
        )}
        onClick={handleAvatarClick}
      >
        <AvatarImage src={avatarSrc} alt={alt} />
        <AvatarFallback>{fallback}</AvatarFallback>
      </Avatar>

      {/* Upload overlay */}
      {showUploadOverlay && onAvatarUpdate && (
        <div 
          className={cn(
            'absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 hover:bg-opacity-50 transition-all rounded-full cursor-pointer',
            isUploading && 'bg-opacity-50'
          )}
          onClick={handleAvatarClick}
        >
          {isUploading ? (
            <Loader2 className="w-4 h-4 text-white animate-spin" />
          ) : (
            <Camera className="w-4 h-4 text-white opacity-0 hover:opacity-100 transition-opacity" />
          )}
        </div>
      )}

      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept="image/jpeg,image/png,image/gif,image/webp"
        className="hidden"
        disabled={isUploading}
      />
    </div>
  );
}

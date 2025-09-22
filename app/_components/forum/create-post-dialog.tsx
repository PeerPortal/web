'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog';
import { Plus, X, Hash, Eye, EyeOff, FileText, Send } from 'lucide-react';
import { forumAPI, CreatePostData, ForumCategory } from '@/lib/forum-api';

interface CreatePostDialogProps {
  children?: React.ReactNode;
  onPostCreated?: () => void;
}

export default function CreatePostDialog({
  children,
  onPostCreated
}: CreatePostDialogProps) {
  const [open, setOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [categories, setCategories] = useState<ForumCategory[]>([]);

  // 表单数据
  const [formData, setFormData] = useState<CreatePostData>({
    title: '',
    content: '',
    category: '',
    tags: [],
    is_anonymous: false
  });

  const [currentTag, setCurrentTag] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  // 预设标签建议
  const suggestedTags = [
    '美国留学',
    'CS申请',
    '奖学金',
    '签证',
    'GRE',
    'TOEFL',
    '文书',
    '面试',
    '实习',
    '求职',
    '生活经验',
    '选校'
  ];

  useEffect(() => {
    if (open) {
      loadCategories();
    }
  }, [open]);

  const loadCategories = async () => {
    try {
      const categoriesData = await forumAPI.getCategories();
      setCategories(categoriesData);
      if (categoriesData.length > 0 && !formData.category) {
        setFormData(prev => ({ ...prev, category: categoriesData[0].id }));
      }
    } catch (error) {
      console.error('加载分类失败:', error);
    }
  };

  const handleInputChange = (
    field: keyof CreatePostData,
    value: string | string[] | boolean
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // 清除对应字段的错误
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const addTag = (tag: string) => {
    const trimmedTag = tag.trim();
    if (
      trimmedTag &&
      !formData.tags.includes(trimmedTag) &&
      formData.tags.length < 5
    ) {
      handleInputChange('tags', [...formData.tags, trimmedTag]);
    }
  };

  const removeTag = (tagToRemove: string) => {
    handleInputChange(
      'tags',
      formData.tags.filter(tag => tag !== tagToRemove)
    );
  };

  const handleAddTag = () => {
    if (currentTag.trim()) {
      addTag(currentTag);
      setCurrentTag('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = '请输入帖子标题';
    } else if (formData.title.length < 5) {
      newErrors.title = '标题至少需要5个字符';
    } else if (formData.title.length > 100) {
      newErrors.title = '标题不能超过100个字符';
    }

    if (!formData.content.trim()) {
      newErrors.content = '请输入帖子内容';
    } else if (formData.content.length < 10) {
      newErrors.content = '内容至少需要10个字符';
    } else if (formData.content.length > 5000) {
      newErrors.content = '内容不能超过5000个字符';
    }

    if (!formData.category) {
      newErrors.category = '请选择帖子分类';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      await forumAPI.createPost(formData);

      // 重置表单
      setFormData({
        title: '',
        content: '',
        category: categories[0]?.id || '',
        tags: [],
        is_anonymous: false
      });
      setCurrentTag('');
      setErrors({});
      setOpen(false);

      // 通知父组件刷新
      onPostCreated?.();
    } catch (error) {
      console.error('发布帖子失败:', error);
      setErrors({ submit: '发布失败，请稍后再试' });
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      content: '',
      category: categories[0]?.id || '',
      tags: [],
      is_anonymous: false
    });
    setCurrentTag('');
    setErrors({});
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button className="w-full" size="lg">
            <Plus className="w-4 h-4 mr-2" />
            发布帖子
          </Button>
        )}
      </DialogTrigger>

      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            发布新帖子
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* 标题 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">帖子标题 *</label>
            <Input
              placeholder="请输入帖子标题..."
              value={formData.title}
              onChange={e => handleInputChange('title', e.target.value)}
              className={errors.title ? 'border-red-500' : ''}
            />
            {errors.title && (
              <p className="text-sm text-red-500">{errors.title}</p>
            )}
            <p className="text-xs text-gray-500">
              {formData.title.length}/100 字符
            </p>
          </div>

          {/* 分类选择 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">帖子分类 *</label>
            <select
              value={formData.category}
              onChange={e => handleInputChange('category', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md bg-white ${
                errors.category ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">请选择分类</option>
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.icon} {category.name}
                </option>
              ))}
            </select>
            {errors.category && (
              <p className="text-sm text-red-500">{errors.category}</p>
            )}
          </div>

          {/* 标签 */}
          <div className="space-y-3">
            <label className="text-sm font-medium">标签</label>

            {/* 当前标签 */}
            {formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.tags.map(tag => (
                  <Badge key={tag} variant="secondary" className="text-sm">
                    <Hash className="w-3 h-3 mr-1" />
                    {tag}
                    <button
                      onClick={() => removeTag(tag)}
                      className="ml-1 hover:text-red-500"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}

            {/* 添加标签 */}
            <div className="flex gap-2">
              <Input
                placeholder="添加标签..."
                value={currentTag}
                onChange={e => setCurrentTag(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={formData.tags.length >= 5}
              />
              <Button
                variant="outline"
                onClick={handleAddTag}
                disabled={!currentTag.trim() || formData.tags.length >= 5}
              >
                添加
              </Button>
            </div>

            {/* 建议标签 */}
            <div className="space-y-2">
              <p className="text-xs text-gray-500">建议标签（点击添加）:</p>
              <div className="flex flex-wrap gap-2">
                {suggestedTags
                  .filter(tag => !formData.tags.includes(tag))
                  .slice(0, 8)
                  .map(tag => (
                    <Badge
                      key={tag}
                      variant="outline"
                      className="cursor-pointer hover:bg-blue-50 text-xs"
                      onClick={() => addTag(tag)}
                    >
                      {tag}
                    </Badge>
                  ))}
              </div>
            </div>

            <p className="text-xs text-gray-500">
              最多可添加5个标签 ({formData.tags.length}/5)
            </p>
          </div>

          {/* 内容 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">帖子内容 *</label>
            <Textarea
              placeholder="请详细描述你的问题或想要分享的内容..."
              value={formData.content}
              onChange={e => handleInputChange('content', e.target.value)}
              rows={8}
              className={`resize-none ${errors.content ? 'border-red-500' : ''}`}
            />
            {errors.content && (
              <p className="text-sm text-red-500">{errors.content}</p>
            )}
            <div className="flex justify-between items-center">
              <p className="text-xs text-gray-500">支持 Markdown 格式</p>
              <p className="text-xs text-gray-500">
                {formData.content.length}/5000 字符
              </p>
            </div>
          </div>

          {/* 选项 */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="anonymous"
                checked={formData.is_anonymous}
                onCheckedChange={checked =>
                  handleInputChange('is_anonymous', checked === true)
                }
              />
              <label
                htmlFor="anonymous"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 flex items-center gap-2"
              >
                {formData.is_anonymous ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
                匿名发布
              </label>
            </div>
            <p className="text-xs text-gray-500 ml-6">
              匿名发布后，其他用户将无法看到你的用户名和个人信息
            </p>
          </div>

          {/* 错误信息 */}
          {errors.submit && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{errors.submit}</p>
            </div>
          )}

          {/* 操作按钮 */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="outline" onClick={resetForm}>
              重置
            </Button>
            <Button variant="outline" onClick={() => setOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSubmit} disabled={isLoading}>
              {isLoading ? (
                <>处理中...</>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  发布帖子
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

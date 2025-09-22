'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import {
  MessageCircle,
  ThumbsUp,
  Eye,
  Share,
  Flag,
  Heart,
  ChevronLeft,
  Reply,
  MoreVertical
} from 'lucide-react';

interface ForumPost {
  id: number;
  title: string;
  content: string;
  author: {
    id: number;
    username: string;
    role: 'student' | 'mentor';
    university?: string;
    major?: string;
    avatar_url?: string;
    reputation: number;
  };
  category: string;
  tags: string[];
  replies: number;
  likes: number;
  views: number;
  isLiked: boolean;
  created_at: string;
  updated_at: string;
}

interface Reply {
  id: number;
  content: string;
  author: {
    id: number;
    username: string;
    role: 'student' | 'mentor';
    university?: string;
    major?: string;
    avatar_url?: string;
    reputation: number;
  };
  likes: number;
  isLiked: boolean;
  created_at: string;
  replies?: Reply[];
}

const mockPost: ForumPost = {
  id: 1,
  title: '如何准备MIT计算机科学申请？求指导！',
  content: `大家好，我是大三学生，目前在国内一所985院校学习计算机科学，GPA 3.8/4.0。

我一直梦想能够申请到MIT的计算机科学研究生项目，但是对于申请流程和要求还不是特别了解。希望有经验的学长学姐能够给一些指导！

**我的背景：**
- GPA: 3.8/4.0
- 专业：计算机科学与技术
- 年级：大三
- 英语：托福还没考，但六级600+
- 研究经历：跟导师做过一个机器学习的项目
- 实习：在一家互联网公司实习过3个月

**我的问题：**
1. MIT CS的录取要求具体是什么？
2. 需要什么样的研究经历？
3. 推荐信应该找谁写？
4. 个人陈述应该怎么写？
5. 申请时间线是怎样的？

非常感谢大家的帮助！🙏`,
  author: {
    id: 1,
    username: '小明同学',
    role: 'student',
    university: '清华大学',
    major: '计算机科学与技术',
    reputation: 150
  },
  category: 'application',
  tags: ['MIT', '计算机科学', '研究生申请', '求助'],
  replies: 15,
  likes: 23,
  views: 156,
  isLiked: false,
  created_at: '2024-01-20T10:30:00Z',
  updated_at: '2024-01-20T10:30:00Z'
};

const mockReplies: Reply[] = [
  {
    id: 1,
    content: `我是MIT CS 23年入学的，可以分享一些经验：

1. **GPA要求**：虽然没有明确的最低要求，但一般建议3.7+
2. **研究经历**：这个非常重要！建议至少要有1-2个高质量的研究项目，最好能发表论文
3. **推荐信**：建议找研究导师、实习mentor、课程老师各写一封
4. **个人陈述**：要突出你的研究兴趣和未来目标，展现passion

具体的申请时间线我可以私信发给你~`,
    author: {
      id: 2,
      username: 'MIT学长',
      role: 'mentor',
      university: 'MIT',
      major: 'Computer Science',
      reputation: 890
    },
    likes: 12,
    isLiked: false,
    created_at: '2024-01-20T11:15:00Z'
  },
  {
    id: 2,
    content: `补充一下托福要求：MIT要求托福最低90分，但建议考到100+会更有竞争力。

另外，如果有时间的话，建议考一下GRE，虽然MIT说optional，但有个好成绩总是加分的。`,
    author: {
      id: 3,
      username: 'Harvard学姐',
      role: 'mentor',
      university: 'Harvard University',
      major: 'Computer Science',
      reputation: 650
    },
    likes: 8,
    isLiked: true,
    created_at: '2024-01-20T12:30:00Z'
  }
];

export default function ForumPostPage() {
  const params = useParams();
  const [post, setPost] = useState<ForumPost>(mockPost);
  const [replies, setReplies] = useState<Reply[]>(mockReplies);
  const [newReply, setNewReply] = useState('');
  const [isLiked, setIsLiked] = useState(post.isLiked);
  const [likesCount, setLikesCount] = useState(post.likes);

  const handleLike = () => {
    setIsLiked(!isLiked);
    setLikesCount(prev => (isLiked ? prev - 1 : prev + 1));
  };

  const handleReplyLike = (replyId: number) => {
    setReplies(prev =>
      prev.map(reply =>
        reply.id === replyId
          ? {
              ...reply,
              isLiked: !reply.isLiked,
              likes: reply.isLiked ? reply.likes - 1 : reply.likes + 1
            }
          : reply
      )
    );
  };

  const handleSubmitReply = () => {
    if (newReply.trim()) {
      const reply: Reply = {
        id: replies.length + 1,
        content: newReply,
        author: {
          id: 999,
          username: '当前用户',
          role: 'student',
          university: '北京大学',
          major: '计算机科学',
          reputation: 50
        },
        likes: 0,
        isLiked: false,
        created_at: new Date().toISOString()
      };
      setReplies(prev => [...prev, reply]);
      setNewReply('');
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    );

    if (diffInHours < 1) return '刚刚';
    if (diffInHours < 24) return `${diffInHours}小时前`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}天前`;
    return date.toLocaleDateString('zh-CN');
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* 返回按钮 */}
      <Button
        variant="ghost"
        className="mb-6"
        onClick={() => window.history.back()}
      >
        <ChevronLeft className="w-4 h-4 mr-2" />
        返回论坛
      </Button>

      {/* 主帖内容 */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <Badge variant="outline">
                  {post.category === 'application' ? '申请经验' : post.category}
                </Badge>
                {post.tags.map(tag => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    #{tag}
                  </Badge>
                ))}
              </div>
              <h1 className="text-2xl font-bold mb-4">{post.title}</h1>
            </div>
            <Button variant="ghost" size="icon">
              <MoreVertical className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>

        <CardContent>
          {/* 帖子内容 */}
          <div className="prose max-w-none mb-6">
            <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
              {post.content}
            </div>
          </div>

          <Separator className="my-6" />

          {/* 作者信息和互动 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Avatar className="w-12 h-12">
                <AvatarFallback className="text-lg">
                  {post.author.username.charAt(0)}
                </AvatarFallback>
              </Avatar>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold">{post.author.username}</span>
                  <Badge
                    variant={
                      post.author.role === 'mentor' ? 'default' : 'secondary'
                    }
                    className="text-xs"
                  >
                    {post.author.role === 'mentor' ? '学长/学姐' : '学弟/学妹'}
                  </Badge>
                  <span className="text-xs text-gray-500">
                    声望 {post.author.reputation}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  {post.author.university} · {post.author.major}
                </div>
                <div className="text-xs text-gray-500">
                  发布于 {formatTimeAgo(post.created_at)}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1 text-sm text-gray-500">
                <Eye className="w-4 h-4" />
                <span>{post.views}</span>
              </div>

              <Button
                variant="ghost"
                size="sm"
                onClick={handleLike}
                className={isLiked ? 'text-red-600' : 'text-gray-600'}
              >
                <Heart
                  className={`w-4 h-4 mr-1 ${isLiked ? 'fill-current' : ''}`}
                />
                {likesCount}
              </Button>

              <Button variant="ghost" size="sm">
                <Share className="w-4 h-4 mr-1" />
                分享
              </Button>

              <Button variant="ghost" size="sm">
                <Flag className="w-4 h-4 mr-1" />
                举报
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 回复列表 */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageCircle className="w-5 h-5" />
            {replies.length} 条回复
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {replies.map((reply, index) => (
              <div key={reply.id}>
                <div className="flex gap-4">
                  <Avatar className="w-10 h-10 flex-shrink-0">
                    <AvatarFallback>
                      {reply.author.username.charAt(0)}
                    </AvatarFallback>
                  </Avatar>

                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-medium">
                        {reply.author.username}
                      </span>
                      <Badge
                        variant={
                          reply.author.role === 'mentor'
                            ? 'default'
                            : 'secondary'
                        }
                        className="text-xs"
                      >
                        {reply.author.role === 'mentor'
                          ? '学长/学姐'
                          : '学弟/学妹'}
                      </Badge>
                      <span className="text-xs text-gray-500">
                        声望 {reply.author.reputation}
                      </span>
                      <span className="text-xs text-gray-500">
                        #{index + 1}
                      </span>
                    </div>

                    <div className="text-sm text-gray-600 mb-2">
                      {reply.author.university} · {reply.author.major}
                    </div>

                    <div className="mb-3 text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {reply.content}
                    </div>

                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-gray-500">
                        {formatTimeAgo(reply.created_at)}
                      </span>

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleReplyLike(reply.id)}
                        className={
                          reply.isLiked ? 'text-red-600' : 'text-gray-600'
                        }
                      >
                        <Heart
                          className={`w-3 h-3 mr-1 ${reply.isLiked ? 'fill-current' : ''}`}
                        />
                        {reply.likes}
                      </Button>

                      <Button variant="ghost" size="sm">
                        <Reply className="w-3 h-3 mr-1" />
                        回复
                      </Button>
                    </div>
                  </div>
                </div>

                {index < replies.length - 1 && <Separator className="mt-6" />}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 发表回复 */}
      <Card>
        <CardHeader>
          <CardTitle>发表回复</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Textarea
              placeholder="写下你的回复..."
              value={newReply}
              onChange={e => setNewReply(e.target.value)}
              rows={4}
              className="resize-none"
            />

            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-500">支持 Markdown 格式</div>

              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setNewReply('')}>
                  取消
                </Button>
                <Button onClick={handleSubmitReply} disabled={!newReply.trim()}>
                  发表回复
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

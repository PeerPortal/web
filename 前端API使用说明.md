# 🚀 PeerPortal 前端 API 使用说明

## 📋 **更新完成清单**

✅ **API配置文件更新** - 添加了AI智能体v2.0、智能匹配、文件上传等新端点  
✅ **AI智能体v2.0 API客户端** - 完整的留学规划师和咨询师对话功能  
✅ **智能匹配系统 API客户端** - 推荐引路人、筛选、保存匹配等功能  
✅ **文件上传 API客户端** - 头像、文档上传，支持进度监控  
✅ **统一API导出** - 方便组件导入和使用

---

## 🎯 **如何使用新的API**

### 1. **AI智能体 v2.0 对话**

```typescript
import { aiAgentAPI, ChatRequest, ChatResponse } from '@/lib';

// 与留学规划师对话
const handlePlannerChat = async () => {
  try {
    const request: ChatRequest = {
      message: '我想申请美国CS硕士，需要什么准备？',
      user_id: 'user123',
      session_id: 'session456'
    };

    const response: ChatResponse = await aiAgentAPI.chatWithPlanner(request);
    console.log('规划师回复:', response.response);
  } catch (error) {
    console.error('对话失败:', error);
  }
};

// 与留学咨询师对话
const handleConsultantChat = async () => {
  const request: ChatRequest = {
    message: '请帮我分析这个学校的录取要求',
    user_id: 'user123'
  };

  const response = await aiAgentAPI.chatWithConsultant(request);
  console.log('咨询师回复:', response.response);
};

// 智能选择合适的智能体
const handleAutoChat = async () => {
  const response = await aiAgentAPI.chatWithAutoAgent({
    message: '我想了解留学申请流程'
  });

  console.log(`${response.agent_type}回复:`, response.response);
};
```

### 2. **智能匹配系统**

```typescript
import { matchingAPI, MatchingRequest, MatchingResult } from '@/lib';

// 推荐引路人
const handleMatchingRecommend = async () => {
  const request: MatchingRequest = {
    target_universities: ['Stanford University', 'MIT'],
    target_majors: ['Computer Science'],
    preferred_degree: 'Master',
    budget_range: [100, 200], // 每小时100-200美元
    preferred_languages: ['中文', '英文'],
    academic_background: {
      gpa: 3.8,
      major: 'Computer Science',
      university: 'Tsinghua University',
      graduation_year: 2023
    }
  };

  const result: MatchingResult = await matchingAPI.recommendMentors(request);

  result.matches.forEach(mentor => {
    console.log(`引路人: ${mentor.mentor_name}`);
    console.log(`匹配度: ${mentor.match_score}%`);
    console.log(`学校: ${mentor.mentor_profile.university}`);
    console.log(`专业: ${mentor.mentor_profile.major}`);
  });
};

// 保存感兴趣的引路人
const handleSaveMatch = async (mentorId: number) => {
  await matchingAPI.saveMatch(mentorId, '这位导师经验很符合我的需求');
};

// 获取保存的匹配
const handleGetSavedMatches = async () => {
  const savedMatches = await matchingAPI.getSavedMatches();
  console.log('已保存的匹配:', savedMatches);
};
```

### 3. **文件上传**

```typescript
import { fileUploadAPI, FileUploadResponse, FileUploadProgress } from '@/lib';

// 上传头像
const handleAvatarUpload = async (file: File) => {
  try {
    const response: FileUploadResponse = await fileUploadAPI.uploadAvatar(
      file,
      (progress: FileUploadProgress) => {
        console.log(`上传进度: ${progress.percentage}%`);
      }
    );

    console.log('头像上传成功:', response.file_url);
    return response.file_url;
  } catch (error) {
    console.error('头像上传失败:', error);
  }
};

// 上传申请文档
const handleDocumentUpload = async (file: File) => {
  const response = await fileUploadAPI.uploadDocument(
    file,
    '我的成绩单',
    'transcript',
    progress => {
      console.log(`文档上传: ${progress.percentage}%`);
    }
  );

  return response;
};

// 批量上传文件
const handleMultipleUpload = async (files: File[]) => {
  const results = await fileUploadAPI.uploadMultiple(
    files,
    'document',
    (fileIndex, progress) => {
      console.log(`文件${fileIndex + 1}上传进度: ${progress.percentage}%`);
    },
    (fileIndex, response) => {
      console.log(`文件${fileIndex + 1}上传完成:`, response.filename);
    },
    (fileIndex, error) => {
      console.error(`文件${fileIndex + 1}上传失败:`, error);
    }
  );

  return results;
};
```

### 4. **组合使用示例**

```typescript
import { API, aiAgentAPI, matchingAPI, fileUploadAPI } from '@/lib';

// React组件中的使用示例
const useAIAgent = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<string>('');

  const chatWithPlanner = async (message: string) => {
    setIsLoading(true);
    try {
      const result = await API.ai.chatWithPlanner({ message });
      setResponse(result.response);
    } catch (error) {
      console.error('AI对话失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return { chatWithPlanner, isLoading, response };
};

// 智能匹配Hook
const useMatching = () => {
  const [matches, setMatches] = useState<MentorMatch[]>([]);

  const findMentors = async (criteria: MatchingRequest) => {
    const result = await API.matching.recommendMentors(criteria);
    setMatches(result.matches);
  };

  return { matches, findMentors };
};

// 文件上传Hook
const useFileUpload = () => {
  const [uploadProgress, setUploadProgress] = useState(0);

  const uploadFile = async (file: File, type: 'avatar' | 'document') => {
    if (type === 'avatar') {
      return await API.files.uploadAvatar(file, progress => {
        setUploadProgress(progress.percentage);
      });
    } else {
      return await API.files.uploadDocument(
        file,
        undefined,
        undefined,
        progress => {
          setUploadProgress(progress.percentage);
        }
      );
    }
  };

  return { uploadFile, uploadProgress };
};
```

---

## 🔧 **环境配置**

创建 `.env.local` 文件：

```bash
# 后端API基础URL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# AI智能体配置
NEXT_PUBLIC_AI_AGENT_TIMEOUT=30000

# 文件上传配置
NEXT_PUBLIC_FILE_UPLOAD_MAX_SIZE=10485760

# 功能开关
NEXT_PUBLIC_ENABLE_AI_AGENT_V2=true
NEXT_PUBLIC_ENABLE_MATCHING_SYSTEM=true
NEXT_PUBLIC_ENABLE_FILE_UPLOAD=true
```

---

## 📝 **类型定义**

所有TypeScript类型都已导出，可以直接使用：

```typescript
import type {
  // AI智能体类型
  ChatRequest,
  ChatResponse,
  SystemStatusResponse,

  // 智能匹配类型
  MatchingRequest,
  MentorMatch,
  MatchingResult,

  // 文件上传类型
  FileUploadResponse,
  FileUploadProgress,

  // 基础类型
  User,
  LoginRequest,
  RegisterRequest
} from '@/lib';
```

---

## 🎯 **组件集成建议**

### 1. **AI对话组件**

```typescript
// components/AIChat.tsx
import { aiAgentAPI } from '@/lib';

const AIChat = () => {
  // 实现AI对话界面
  // 支持选择规划师或咨询师
  // 显示对话历史
};
```

### 2. **引路人匹配组件**

```typescript
// components/MentorMatching.tsx
import { matchingAPI } from '@/lib';

const MentorMatching = () => {
  // 实现匹配条件设置
  // 显示匹配结果
  // 支持保存和联系引路人
};
```

### 3. **文件上传组件**

```typescript
// components/FileUploader.tsx
import { fileUploadAPI } from '@/lib';

const FileUploader = () => {
  // 实现拖拽上传
  // 显示上传进度
  // 支持多文件上传
};
```

---

## ⚡ **立即开始使用**

1. **导入需要的API**:

   ```typescript
   import { aiAgentAPI, matchingAPI, fileUploadAPI } from '@/lib';
   ```

2. **确保后端服务运行**:

   ```bash
   cd backend && python -m uvicorn app.main:app --reload
   ```

3. **开始开发新功能**:
   - AI智能体对话界面
   - 智能匹配功能页面
   - 文件上传组件

---

**🎉 前端已完全支持后端所有核心接口！现在可以开始开发完整的用户体验了！**

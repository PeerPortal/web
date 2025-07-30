# 🧪 PeerPortal API 功能测试指南

## 📋 **测试前准备**

### 1. **启动后端服务**

```bash
# 切换到后端目录
cd backend

# 启动后端服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或者使用快速启动脚本
./start_server.sh
```

验证后端是否启动成功：

- 访问 http://localhost:8000
- 访问 http://localhost:8000/docs (Swagger API文档)

### 2. **启动前端服务**

```bash
# 切换到前端目录
cd web

# 安装依赖（如果还没有）
npm install

# 启动开发服务器
npm run dev
```

验证前端是否启动成功：

- 访问 http://localhost:3000

### 3. **环境配置**

创建 `web/.env.local` 文件：

```bash
# 后端API基础URL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# 调试模式
NEXT_PUBLIC_DEBUG_MODE=true

# 功能开关
NEXT_PUBLIC_ENABLE_AI_AGENT_V2=true
NEXT_PUBLIC_ENABLE_MATCHING_SYSTEM=true
NEXT_PUBLIC_ENABLE_FILE_UPLOAD=true
```

---

## 🤖 **AI智能体v2.0功能测试**

### 测试方案1：浏览器控制台测试

打开浏览器开发工具 (F12)，在控制台执行：

```javascript
// 1. 测试与留学规划师对话
const testPlannerChat = async () => {
  try {
    // 确保用户已登录
    const response = await fetch(
      'http://localhost:8000/api/v2/agents/planner/chat',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
          // 'Authorization': 'Bearer YOUR_TOKEN_HERE' // 如果需要认证
        },
        body: JSON.stringify({
          message: '我想申请美国CS硕士，需要什么准备？',
          user_id: 'test_user_123'
        })
      }
    );

    if (response.ok) {
      const data = await response.json();
      console.log('✅ AI规划师回复:', data);
      return data;
    } else {
      console.error('❌ 请求失败:', response.status, await response.text());
    }
  } catch (error) {
    console.error('❌ 网络错误:', error);
  }
};

// 执行测试
testPlannerChat();
```

```javascript
// 2. 测试与留学咨询师对话
const testConsultantChat = async () => {
  const response = await fetch(
    'http://localhost:8000/api/v2/agents/consultant/chat',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: '请帮我分析MIT的录取要求',
        user_id: 'test_user_123'
      })
    }
  );

  const data = await response.json();
  console.log('✅ AI咨询师回复:', data);
};

testConsultantChat();
```

```javascript
// 3. 测试系统状态
const testSystemStatus = async () => {
  const response = await fetch('http://localhost:8000/api/v2/agents/status');
  const data = await response.json();
  console.log('✅ 系统状态:', data);
};

testSystemStatus();
```

### 测试方案2：创建测试页面

创建 `web/app/test/ai-agent/page.tsx`：

```tsx
'use client';

import { useState } from 'react';
import { aiAgentAPI } from '@/lib';
import type { ChatRequest, ChatResponse } from '@/lib';

export default function AIAgentTestPage() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [agentType, setAgentType] = useState<'planner' | 'consultant'>(
    'planner'
  );

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    setLoading(true);
    try {
      const request: ChatRequest = {
        message,
        user_id: 'test_user_123',
        session_id: `test_session_${Date.now()}`
      };

      let result: ChatResponse;
      if (agentType === 'planner') {
        result = await aiAgentAPI.chatWithPlanner(request);
      } else {
        result = await aiAgentAPI.chatWithConsultant(request);
      }

      setResponse(result);
      console.log('✅ AI回复:', result);
    } catch (error) {
      console.error('❌ 对话失败:', error);
      alert(`对话失败: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">🤖 AI智能体测试</h1>

      <div className="space-y-4">
        {/* 智能体类型选择 */}
        <div>
          <label className="block text-sm font-medium mb-2">
            选择智能体类型:
          </label>
          <select
            value={agentType}
            onChange={e =>
              setAgentType(e.target.value as 'planner' | 'consultant')
            }
            className="border border-gray-300 rounded px-3 py-2"
          >
            <option value="planner">留学规划师</option>
            <option value="consultant">留学咨询师</option>
          </select>
        </div>

        {/* 消息输入 */}
        <div>
          <label className="block text-sm font-medium mb-2">输入消息:</label>
          <textarea
            value={message}
            onChange={e => setMessage(e.target.value)}
            placeholder="输入你的问题..."
            className="w-full border border-gray-300 rounded px-3 py-2 h-24"
          />
        </div>

        {/* 发送按钮 */}
        <button
          onClick={handleSendMessage}
          disabled={loading || !message.trim()}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-300"
        >
          {loading ? '发送中...' : '发送消息'}
        </button>

        {/* 响应显示 */}
        {response && (
          <div className="mt-6 p-4 bg-gray-100 rounded">
            <h3 className="font-semibold mb-2">AI回复:</h3>
            <p className="whitespace-pre-wrap">{response.response}</p>
            <div className="mt-2 text-sm text-gray-600">
              <p>智能体类型: {response.agent_type}</p>
              <p>版本: {response.version}</p>
              {response.metadata && (
                <p>处理时间: {response.metadata.processing_time}ms</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
```

访问 http://localhost:3000/test/ai-agent 进行测试。

---

## 🎯 **智能匹配系统测试**

### 测试方案1：控制台测试

```javascript
// 1. 测试推荐引路人
const testMatching = async () => {
  const matchingRequest = {
    target_universities: ['Stanford University', 'MIT'],
    target_majors: ['Computer Science'],
    preferred_degree: 'Master',
    budget_range: [100, 200],
    preferred_languages: ['中文', '英文'],
    academic_background: {
      gpa: 3.8,
      major: 'Computer Science',
      university: 'Tsinghua University',
      graduation_year: 2023
    }
  };

  const response = await fetch(
    'http://localhost:8000/api/v1/matching/recommend',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(matchingRequest)
    }
  );

  const data = await response.json();
  console.log('✅ 匹配结果:', data);
};

testMatching();
```

```javascript
// 2. 测试获取筛选条件
const testFilters = async () => {
  const response = await fetch('http://localhost:8000/api/v1/matching/filters');
  const data = await response.json();
  console.log('✅ 筛选条件:', data);
};

testFilters();
```

### 测试方案2：创建测试页面

创建 `web/app/test/matching/page.tsx`：

```tsx
'use client';

import { useState } from 'react';
import { matchingAPI } from '@/lib';
import type { MatchingRequest, MatchingResult, MentorMatch } from '@/lib';

export default function MatchingTestPage() {
  const [result, setResult] = useState<MatchingResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleTestMatching = async () => {
    setLoading(true);
    try {
      const request: MatchingRequest = {
        target_universities: [
          'Stanford University',
          'MIT',
          'Carnegie Mellon University'
        ],
        target_majors: ['Computer Science', 'Data Science'],
        preferred_degree: 'Master',
        budget_range: [80, 150],
        preferred_languages: ['中文', '英文'],
        academic_background: {
          gpa: 3.7,
          major: 'Computer Science',
          university: 'Beijing University',
          graduation_year: 2023
        },
        test_scores: {
          toefl: 108,
          gre: 325
        }
      };

      const matchingResult = await matchingAPI.recommendMentors(request);
      setResult(matchingResult);
      console.log('✅ 匹配成功:', matchingResult);
    } catch (error) {
      console.error('❌ 匹配失败:', error);
      alert(`匹配失败: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveMatch = async (mentorId: number) => {
    try {
      await matchingAPI.saveMatch(mentorId, '感兴趣的引路人');
      alert('保存成功！');
    } catch (error) {
      console.error('❌ 保存失败:', error);
      alert(`保存失败: ${error}`);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">🎯 智能匹配测试</h1>

      <button
        onClick={handleTestMatching}
        disabled={loading}
        className="bg-green-500 text-white px-4 py-2 rounded disabled:bg-gray-300 mb-6"
      >
        {loading ? '匹配中...' : '开始智能匹配'}
      </button>

      {result && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">
            匹配结果 (共 {result.total_matches} 个)
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {result.matches.map((mentor: MentorMatch) => (
              <div key={mentor.mentor_id} className="border p-4 rounded-lg">
                <h3 className="font-semibold">{mentor.mentor_name}</h3>
                <p className="text-sm text-gray-600">
                  {mentor.mentor_profile.university} -{' '}
                  {mentor.mentor_profile.major}
                </p>
                <p className="text-sm">匹配度: {mentor.match_score}%</p>
                <p className="text-sm">评分: {mentor.rating}/5</p>
                <p className="text-sm">经验: {mentor.total_sessions} 次指导</p>

                <div className="mt-2">
                  <p className="text-xs text-gray-500">匹配原因:</p>
                  <ul className="text-xs list-disc list-inside">
                    {mentor.match_reasons.map((reason, idx) => (
                      <li key={idx}>{reason}</li>
                    ))}
                  </ul>
                </div>

                <button
                  onClick={() => handleSaveMatch(mentor.mentor_id)}
                  className="mt-2 bg-blue-500 text-white px-3 py-1 rounded text-sm"
                >
                  保存
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## 📁 **文件上传功能测试**

### 测试方案1：控制台测试

```javascript
// 创建一个测试文件 (使用现有图片或文档)
const testFileUpload = async () => {
  // 创建一个测试文件
  const canvas = document.createElement('canvas');
  canvas.width = 100;
  canvas.height = 100;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#FF0000';
  ctx.fillRect(0, 0, 100, 100);

  canvas.toBlob(async blob => {
    const file = new File([blob], 'test-avatar.png', { type: 'image/png' });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(
        'http://localhost:8000/api/v1/files/upload/avatar',
        {
          method: 'POST',
          // headers: { 'Authorization': 'Bearer YOUR_TOKEN' }, // 如果需要认证
          body: formData
        }
      );

      const result = await response.json();
      console.log('✅ 文件上传成功:', result);
    } catch (error) {
      console.error('❌ 文件上传失败:', error);
    }
  });
};

testFileUpload();
```

### 测试方案2：创建测试页面

创建 `web/app/test/file-upload/page.tsx`：

```tsx
'use client';

import { useState } from 'react';
import { fileUploadAPI } from '@/lib';
import type { FileUploadResponse, FileUploadProgress } from '@/lib';

export default function FileUploadTestPage() {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState<FileUploadResponse | null>(
    null
  );
  const [uploading, setUploading] = useState(false);

  const handleAvatarUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      const result = await fileUploadAPI.uploadAvatar(
        file,
        (progress: FileUploadProgress) => {
          setUploadProgress(progress.percentage);
        }
      );

      setUploadResult(result);
      console.log('✅ 头像上传成功:', result);
    } catch (error) {
      console.error('❌ 头像上传失败:', error);
      alert(`上传失败: ${error}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDocumentUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      const result = await fileUploadAPI.uploadDocument(
        file,
        '测试文档',
        'transcript',
        (progress: FileUploadProgress) => {
          setUploadProgress(progress.percentage);
        }
      );

      setUploadResult(result);
      console.log('✅ 文档上传成功:', result);
    } catch (error) {
      console.error('❌ 文档上传失败:', error);
      alert(`上传失败: ${error}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">📁 文件上传测试</h1>

      <div className="space-y-6">
        {/* 头像上传测试 */}
        <div className="border p-4 rounded">
          <h2 className="text-lg font-semibold mb-4">头像上传测试</h2>
          <input
            type="file"
            accept="image/*"
            onChange={handleAvatarUpload}
            disabled={uploading}
            className="mb-2"
          />
          <p className="text-sm text-gray-600">
            支持格式: JPG, PNG, GIF, WebP (最大5MB)
          </p>
        </div>

        {/* 文档上传测试 */}
        <div className="border p-4 rounded">
          <h2 className="text-lg font-semibold mb-4">文档上传测试</h2>
          <input
            type="file"
            accept=".pdf,.doc,.docx,.txt"
            onChange={handleDocumentUpload}
            disabled={uploading}
            className="mb-2"
          />
          <p className="text-sm text-gray-600">
            支持格式: PDF, DOC, DOCX, TXT (最大10MB)
          </p>
        </div>

        {/* 上传进度 */}
        {uploading && (
          <div className="border p-4 rounded">
            <h3 className="font-semibold mb-2">上传进度</h3>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-sm mt-1">{uploadProgress}%</p>
          </div>
        )}

        {/* 上传结果 */}
        {uploadResult && (
          <div className="border p-4 rounded bg-green-50">
            <h3 className="font-semibold mb-2">✅ 上传成功</h3>
            <div className="text-sm space-y-1">
              <p>
                <strong>文件名:</strong> {uploadResult.filename}
              </p>
              <p>
                <strong>原始名:</strong> {uploadResult.original_filename}
              </p>
              <p>
                <strong>大小:</strong>{' '}
                {fileUploadAPI.formatFileSize(uploadResult.file_size)}
              </p>
              <p>
                <strong>类型:</strong> {uploadResult.content_type}
              </p>
              <p>
                <strong>URL:</strong>{' '}
                <a
                  href={uploadResult.file_url}
                  target="_blank"
                  className="text-blue-600 underline"
                >
                  {uploadResult.file_url}
                </a>
              </p>
            </div>

            {uploadResult.metadata?.width && (
              <p className="text-sm mt-2">
                <strong>尺寸:</strong> {uploadResult.metadata.width} ×{' '}
                {uploadResult.metadata.height}px
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## 🔧 **综合测试页面**

创建 `web/app/test/page.tsx`：

```tsx
'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { aiAgentAPI, matchingAPI } from '@/lib';

export default function TestPage() {
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [backendStatus, setBackendStatus] = useState<
    'online' | 'offline' | 'checking'
  >('checking');

  useEffect(() => {
    checkBackendStatus();
  }, []);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        setBackendStatus('online');

        // 尝试获取AI系统状态
        try {
          const status = await aiAgentAPI.getSystemStatus();
          setSystemStatus(status);
        } catch (error) {
          console.log('AI系统状态获取失败:', error);
        }
      } else {
        setBackendStatus('offline');
      }
    } catch (error) {
      setBackendStatus('offline');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">🧪 PeerPortal API 测试中心</h1>

      {/* 系统状态 */}
      <div className="mb-8 p-4 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">系统状态</h2>

        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span>后端服务:</span>
            <span
              className={`px-2 py-1 rounded text-sm ${
                backendStatus === 'online'
                  ? 'bg-green-100 text-green-800'
                  : backendStatus === 'offline'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
              }`}
            >
              {backendStatus === 'online'
                ? '🟢 在线'
                : backendStatus === 'offline'
                  ? '🔴 离线'
                  : '🟡 检查中'}
            </span>
          </div>

          {systemStatus && (
            <div className="text-sm text-gray-600">
              <p>AI系统版本: {systemStatus.version}</p>
              <p>可用智能体: {systemStatus.available_agents?.join(', ')}</p>
              <p>系统健康: {systemStatus.system_health}</p>
            </div>
          )}
        </div>

        <button
          onClick={checkBackendStatus}
          className="mt-2 bg-blue-500 text-white px-3 py-1 rounded text-sm"
        >
          重新检查
        </button>
      </div>

      {/* 功能测试链接 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Link
          href="/test/ai-agent"
          className="block p-6 border rounded-lg hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold mb-2">🤖 AI智能体测试</h3>
          <p className="text-gray-600">测试留学规划师和咨询师对话功能</p>
        </Link>

        <Link
          href="/test/matching"
          className="block p-6 border rounded-lg hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold mb-2">🎯 智能匹配测试</h3>
          <p className="text-gray-600">测试引路人推荐和匹配功能</p>
        </Link>

        <Link
          href="/test/file-upload"
          className="block p-6 border rounded-lg hover:shadow-lg transition-shadow"
        >
          <h3 className="text-lg font-semibold mb-2">📁 文件上传测试</h3>
          <p className="text-gray-600">测试头像和文档上传功能</p>
        </Link>
      </div>

      {/* 快速测试按钮 */}
      <div className="mt-8 p-4 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">快速测试</h2>
        <div className="flex gap-4 flex-wrap">
          <button
            onClick={async () => {
              try {
                const response = await aiAgentAPI.chatWithPlanner({
                  message: 'Hello, 测试消息'
                });
                alert('AI测试成功！查看控制台输出。');
                console.log('AI回复:', response);
              } catch (error) {
                alert('AI测试失败: ' + error);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            测试AI对话
          </button>

          <button
            onClick={async () => {
              try {
                const filters = await matchingAPI.getFilters();
                alert('匹配筛选器测试成功！查看控制台输出。');
                console.log('筛选器:', filters);
              } catch (error) {
                alert('匹配测试失败: ' + error);
              }
            }}
            className="bg-green-500 text-white px-4 py-2 rounded"
          >
            测试匹配筛选
          </button>
        </div>
      </div>

      {/* API文档链接 */}
      <div className="mt-8 p-4 border rounded-lg">
        <h2 className="text-xl font-semibold mb-4">相关资源</h2>
        <div className="space-y-2">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            className="block text-blue-600 hover:underline"
          >
            📚 后端API文档 (Swagger)
          </a>
          <Link
            href="/前端API使用说明.md"
            className="block text-blue-600 hover:underline"
          >
            📖 前端API使用说明
          </Link>
        </div>
      </div>
    </div>
  );
}
```

---

## 🐛 **调试和排错**

### 1. **常见问题和解决方案**

**问题1: CORS错误**

```
解决方案: 确保后端已配置CORS，允许http://localhost:3000
```

**问题2: 认证错误 (401)**

```
解决方案:
1. 检查是否已登录
2. 确保token正确传递
3. 检查token是否过期
```

**问题3: API端点404**

```
解决方案:
1. 确认后端服务正在运行
2. 检查API端点路径是否正确
3. 确认后端版本是否支持v2.0接口
```

### 2. **调试技巧**

**开启调试模式:**

```javascript
// 在浏览器控制台中
localStorage.setItem('debug', 'true');

// 查看网络请求
// Chrome DevTools -> Network 标签页
```

**监听API调用:**

```javascript
// 拦截fetch请求进行调试
const originalFetch = window.fetch;
window.fetch = function (...args) {
  console.log('API调用:', args[0], args[1]);
  return originalFetch.apply(this, args).then(response => {
    console.log('API响应:', response.status, response.url);
    return response;
  });
};
```

### 3. **性能监控**

```javascript
// 监控API响应时间
const measureApiPerformance = async apiCall => {
  const start = performance.now();
  try {
    const result = await apiCall();
    const end = performance.now();
    console.log(`API耗时: ${end - start}ms`);
    return result;
  } catch (error) {
    const end = performance.now();
    console.log(`API失败，耗时: ${end - start}ms`);
    throw error;
  }
};

// 使用示例
measureApiPerformance(() => aiAgentAPI.chatWithPlanner({ message: 'test' }));
```

---

## ✅ **测试检查清单**

### AI智能体v2.0

- [ ] 规划师对话功能
- [ ] 咨询师对话功能
- [ ] 自动智能体选择
- [ ] 系统状态检查
- [ ] 健康检查
- [ ] 错误处理

### 智能匹配系统

- [ ] 推荐引路人功能
- [ ] 获取筛选条件
- [ ] 高级筛选功能
- [ ] 保存匹配结果
- [ ] 获取匹配历史
- [ ] 兼容性检查

### 文件上传系统

- [ ] 头像上传功能
- [ ] 文档上传功能
- [ ] 上传进度监控
- [ ] 文件类型验证
- [ ] 文件大小限制
- [ ] 批量上传功能

### 集成测试

- [ ] 认证流程完整性
- [ ] 错误处理一致性
- [ ] 性能表现
- [ ] 移动端兼容性

---

**🎉 现在你可以开始全面测试所有新功能了！记得检查浏览器控制台的输出和网络请求。**

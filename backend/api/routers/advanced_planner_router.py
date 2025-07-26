"""
高级AI留学规划师的API路由
基于LangGraph实现的增强版智能咨询服务
集成LangSmith监控和评估
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
import time
import asyncio
from datetime import datetime

from app.agents.langgraph.agent_graph import get_advanced_agent
from app.agents.langgraph.knowledge_base import knowledge_manager
from app.core.langsmith_config import is_langsmith_enabled, study_abroad_tracer

router = APIRouter(prefix="/advanced-planner", tags=["高级AI留学规划师"])

class AdvancedPlannerRequest(BaseModel):
    """高级AI规划师请求模型"""
    input: str = Field(..., min_length=1, max_length=2000, description="用户的留学咨询问题")
    user_id: Optional[str] = Field(default="anonymous", description="用户ID，用于LangSmith追踪")
    session_id: Optional[str] = Field(default="default", description="会话ID，用于维持对话上下文")
    chat_history: Optional[List[dict]] = Field(default=[], description="对话历史")
    stream: bool = Field(default=False, description="是否启用流式响应")

class AdvancedPlannerResponse(BaseModel):
    """高级AI规划师响应模型"""
    output: str = Field(..., description="AI的回答内容")
    session_id: str = Field(..., description="会话ID")
    timestamp: str = Field(..., description="响应时间戳")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="响应元数据（执行时间、工具调用等）")
    langsmith_enabled: bool = Field(default=False, description="LangSmith是否启用")

class KnowledgeBaseStatus(BaseModel):
    """知识库状态模型"""
    files_count: int = Field(..., description="文档数量")
    vector_store_exists: bool = Field(..., description="向量库是否存在")
    files: List[str] = Field(..., description="文件列表")

def get_agent():
    """获取Agent实例"""
    try:
        return get_advanced_agent()
    except Exception as e:
        print(f"❌ 高级Agent初始化失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI服务初始化失败: {str(e)}")

@router.post("/invoke", 
             response_model=AdvancedPlannerResponse,
             summary="调用高级AI留学规划师", 
             description="发送问题给高级AI留学规划师，获得基于知识库和实时搜索的专业建议")
async def invoke_advanced_planner(request: AdvancedPlannerRequest):
    """
    调用高级AI留学规划师进行咨询
    
    新特性：
    - 🧠 长期记忆：跨会话记忆用户信息
    - 📚 知识库检索：从上传文档中获取专业建议  
    - 🔍 智能搜索：自动选择最合适的信息源
    - ⚡ 工具融合：数据库查询+网络搜索+知识库
    """
    try:
        agent = get_agent()
        
        if request.stream:
            # 流式响应（暂时保持原有逻辑，未来可扩展LangSmith流式追踪）
            return StreamingResponse(
                stream_generator(agent, request),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # 非流式响应
            start_time = time.time()
            
            input_data = {
                "input": request.input,
                "session_id": request.session_id,
                "chat_history": request.chat_history or []
            }
            
            # 检查是否启用LangSmith追踪
            langsmith_enabled = is_langsmith_enabled()
            
            if langsmith_enabled:
                # 使用LangSmith追踪执行Agent
                async with study_abroad_tracer.trace_agent_run(
                    agent_name="AI留学规划师",
                    user_id=request.user_id,
                    session_id=request.session_id,
                    input_data=input_data
                ) as trace_context:
                    result = await agent.ainvoke(input_data)
                    
                    # 构建元数据
                    metadata = {
                        "execution_time": time.time() - start_time,
                        "langsmith_run_id": trace_context.get("run_id") if trace_context else None,
                        "user_id": request.user_id,
                        "session_id": request.session_id
                    }
            else:
                # 标准执行（无追踪）
                result = await agent.ainvoke(input_data)
                
                metadata = {
                    "execution_time": time.time() - start_time,
                    "user_id": request.user_id,
                    "session_id": request.session_id
                }
            
            return AdvancedPlannerResponse(
                output=result["output"],
                session_id=result["session_id"],
                timestamp=datetime.now().isoformat(),
                metadata=metadata,
                langsmith_enabled=langsmith_enabled
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")

async def stream_generator(agent, request: AdvancedPlannerRequest):
    """流式响应生成器"""
    try:
        input_data = {
            "input": request.input,
            "session_id": request.session_id,
            "chat_history": request.chat_history or []
        }
        
        # 发送开始信号
        yield f"data: {json.dumps({'type': 'start', 'message': '开始处理您的问题...'}, ensure_ascii=False)}\n\n"
        
        # 流式处理
        full_response = ""
        for event in agent.stream(input_data):
            if "agent" in event:
                outcome = event["agent"].get("agent_outcome")
                if outcome and hasattr(outcome, 'return_values'):
                    chunk = outcome.return_values.get('output', '')
                    if chunk:
                        full_response += chunk
                        yield f"data: {json.dumps({'type': 'chunk', 'chunk': chunk}, ensure_ascii=False)}\n\n"
            
            if "tools" in event:
                # 工具调用信息
                tool_info = "正在调用工具获取信息..."
                yield f"data: {json.dumps({'type': 'tool', 'message': tool_info}, ensure_ascii=False)}\n\n"
        
        # 发送完成信号
        yield f"data: {json.dumps({'type': 'end', 'full_response': full_response}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        error_data = {
            "type": "error",
            "error": f"流式处理出错: {str(e)}"
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

@router.get("/health", summary="高级AI服务健康检查")
async def health_check():
    """检查高级AI留学规划师服务状态"""
    try:
        agent = get_agent()
        kb_stats = knowledge_manager.get_knowledge_base_stats()
        
        return {
            "status": "healthy",
            "service": "高级AI留学规划师",
            "version": "2.0",
            "features": ["LangGraph", "知识库", "长期记忆", "多工具融合"],
            "timestamp": datetime.now().isoformat(),
            "knowledge_base": {
                "files_count": kb_stats["files_count"],
                "vector_store_ready": kb_stats["vector_store_exists"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"高级AI服务不可用: {str(e)}")

@router.post("/upload-documents", summary="上传文档到知识库")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    上传PDF文档到知识库
    
    支持的文件格式：
    - PDF: 留学案例、学校介绍、申请指南等
    """
    try:
        uploaded_files = []
        
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file.filename}")
            
            # 保存文件
            file_content = await file.read()
            file_path = knowledge_manager.save_uploaded_file(file_content, file.filename)
            uploaded_files.append(file.filename)
        
        # 重建知识库
        vectorstore = knowledge_manager.load_and_embed_knowledge_base()
        
        return {
            "message": f"成功上传 {len(uploaded_files)} 个文件",
            "files": uploaded_files,
            "knowledge_base_ready": vectorstore is not None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.get("/knowledge-base/status", 
            response_model=KnowledgeBaseStatus,
            summary="获取知识库状态")
async def get_knowledge_base_status():
    """获取知识库的状态信息"""
    try:
        stats = knowledge_manager.get_knowledge_base_stats()
        return KnowledgeBaseStatus(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识库状态失败: {str(e)}")

@router.delete("/knowledge-base", summary="清空知识库")
async def clear_knowledge_base():
    """清空知识库中的所有文档和向量数据"""
    try:
        import shutil
        import os
        
        # 删除知识库文件
        if os.path.exists("./knowledge_base"):
            shutil.rmtree("./knowledge_base")
        
        # 删除向量库
        if os.path.exists("./vector_store"):
            shutil.rmtree("./vector_store")
        
        return {
            "message": "知识库已清空",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空知识库失败: {str(e)}")

@router.get("/capabilities", summary="获取高级AI能力说明")
async def get_capabilities():
    """获取高级AI留学规划师的完整能力说明"""
    return {
        "service_name": "启航AI留学规划师 2.0",
        "core_features": {
            "intelligent_routing": "智能选择最合适的信息源",
            "knowledge_base": "从上传文档中学习并提供专业建议",
            "long_term_memory": "跨会话记忆用户信息和偏好",
            "real_time_search": "获取最新的留学资讯和大学信息",
            "platform_integration": "匹配平台上的引路人和服务"
        },
        "capabilities": [
            "🧠 智能工具选择：根据问题类型自动选择最佳信息源",
            "📚 知识库学习：从PDF文档中学习专业留学知识",
            "🔍 实时信息获取：搜索最新的大学排名和申请要求",
            "👥 个性化匹配：推荐最合适的引路人和服务",
            "💭 上下文记忆：维持对话连贯性和个性化体验",
            "⚡ 多模态响应：支持流式和标准响应模式"
        ],
        "supported_regions": ["美国", "加拿大", "英国", "澳大利亚", "新加坡", "香港", "德国", "法国"],
        "supported_degrees": ["本科", "硕士", "博士", "交换项目"],
        "technical_stack": ["LangGraph", "OpenAI GPT", "ChromaDB", "Tavily Search", "FastAPI"],
        "response_modes": ["流式响应", "标准响应", "工具调用追踪"]
    }

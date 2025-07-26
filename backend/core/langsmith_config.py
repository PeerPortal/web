"""
LangSmith 集成配置模块
为AI留学规划师Agent提供全面的监控、评估和调试支持
"""
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import contextmanager

from langsmith import Client
from langsmith.schemas import Run, Example
from langchain.callbacks import LangChainTracer
from langchain.callbacks.base import BaseCallbackHandler

from app.core.config import settings

logger = logging.getLogger(__name__)


class StudyAbroadAgentTracer:
    """留学规划师Agent专用的LangSmith追踪器"""
    
    def __init__(self):
        self.client = None
        self.project_name = settings.LANGCHAIN_PROJECT or "AI留学规划师-默认"
        self.enabled = self._is_enabled()
        
        if self.enabled:
            self._initialize_client()
            self._setup_environment()
    
    def _is_enabled(self) -> bool:
        """检查LangSmith是否启用"""
        return (
            settings.LANGCHAIN_TRACING_V2 and
            settings.LANGCHAIN_API_KEY is not None and
            settings.LANGCHAIN_API_KEY.startswith('lsv2_')
        )
    
    def _initialize_client(self):
        """初始化LangSmith客户端"""
        try:
            self.client = Client(
                api_url=settings.LANGCHAIN_ENDPOINT,
                api_key=settings.LANGCHAIN_API_KEY
            )
            logger.info(f"✅ LangSmith客户端初始化成功 - 项目: {self.project_name}")
        except Exception as e:
            logger.error(f"❌ LangSmith客户端初始化失败: {e}")
            self.enabled = False
    
    def _setup_environment(self):
        """设置环境变量供LangChain使用"""
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = self.project_name
        os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
    
    def get_tracer(self) -> Optional[LangChainTracer]:
        """获取LangChain追踪器"""
        if not self.enabled:
            return None
        
        return LangChainTracer(
            project_name=self.project_name
        )
    
    def create_session(self, user_id: str, session_type: str = "chat") -> str:
        """创建追踪会话"""
        if not self.enabled:
            return f"local_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session_id = f"{session_type}_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return session_id
    
    @contextmanager
    def trace_agent_run(
        self, 
        run_name: str, 
        user_id: str, 
        inputs: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Agent运行的上下文管理器
        自动记录输入、输出和错误
        """
        session_id = self.create_session(user_id, "agent_run")
        run_metadata = {
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        if self.enabled:
            logger.info(f"🔍 开始追踪Agent运行: {run_name} (用户: {user_id})")
        
        try:
            yield session_id
        except Exception as e:
            if self.enabled:
                logger.error(f"❌ Agent运行出错: {run_name} - {str(e)}")
            raise
        finally:
            if self.enabled:
                logger.info(f"✅ 完成追踪Agent运行: {run_name}")


class StudyAbroadEvaluator:
    """留学规划师Agent评估器"""
    
    def __init__(self, tracer: StudyAbroadAgentTracer):
        self.tracer = tracer
        self.client = tracer.client
        self.enabled = tracer.enabled
    
    def create_evaluation_dataset(self, dataset_name: str, description: str) -> Optional[str]:
        """创建评估数据集"""
        if not self.enabled:
            logger.warning("LangSmith未启用，无法创建评估数据集")
            return None
        
        try:
            dataset = self.client.create_dataset(
                dataset_name=dataset_name,
                description=description
            )
            logger.info(f"✅ 创建评估数据集成功: {dataset_name}")
            return dataset.id
        except Exception as e:
            logger.error(f"❌ 创建评估数据集失败: {e}")
            return None
    
    def add_evaluation_example(
        self,
        dataset_name: str,
        input_data: Dict[str, Any],
        expected_output: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """添加评估示例到数据集"""
        if not self.enabled:
            return False
        
        try:
            self.client.create_example(
                inputs=input_data,
                outputs=expected_output,
                dataset_name=dataset_name,
                metadata=metadata
            )
            logger.info(f"✅ 添加评估示例成功到数据集: {dataset_name}")
            return True
        except Exception as e:
            logger.error(f"❌ 添加评估示例失败: {e}")
            return False
    
    def get_standard_evaluation_criteria(self) -> List[Dict[str, Any]]:
        """获取标准评估标准"""
        return [
            {
                "name": "response_relevance",
                "description": "回答与用户问题的相关性",
                "scoring": "1-5分，5分为完全相关"
            },
            {
                "name": "information_accuracy",
                "description": "提供信息的准确性",
                "scoring": "1-5分，5分为完全准确"
            },
            {
                "name": "actionability",
                "description": "建议的可操作性",
                "scoring": "1-5分，5分为非常具体可操作"
            },
            {
                "name": "response_completeness",
                "description": "回答的完整性",
                "scoring": "1-5分，5分为覆盖全面"
            },
            {
                "name": "tone_appropriateness",
                "description": "语调的合适性（友善、专业）",
                "scoring": "1-5分，5分为非常合适"
            }
        ]


class StudyAbroadCallbackHandler(BaseCallbackHandler):
    """留学规划师专用回调处理器"""
    
    def __init__(self, user_id: str, session_id: str):
        super().__init__()
        self.user_id = user_id
        self.session_id = session_id
        self.step_count = 0
    
    def on_agent_action(self, action, **kwargs):
        """Agent执行动作时的回调"""
        self.step_count += 1
        logger.info(f"🤖 Agent执行第{self.step_count}步动作: {action.tool}")
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        """工具开始执行时的回调"""
        tool_name = serialized.get("name", "未知工具")
        logger.info(f"🔧 开始使用工具: {tool_name}")
    
    def on_tool_end(self, output, **kwargs):
        """工具执行完成时的回调"""
        logger.info(f"✅ 工具执行完成，输出长度: {len(str(output))}")
    
    def on_tool_error(self, error, **kwargs):
        """工具执行错误时的回调"""
        logger.error(f"❌ 工具执行出错: {error}")
    
    def on_agent_finish(self, finish, **kwargs):
        """Agent完成时的回调"""
        logger.info(f"🎯 Agent完成，总共执行{self.step_count}步")


# 全局实例
study_abroad_tracer = StudyAbroadAgentTracer()
study_abroad_evaluator = StudyAbroadEvaluator(study_abroad_tracer)

def get_langsmith_callbacks(user_id: str, session_id: str) -> List[BaseCallbackHandler]:
    """获取LangSmith回调处理器列表"""
    callbacks = []
    
    # 添加自定义回调处理器
    callbacks.append(StudyAbroadCallbackHandler(user_id, session_id))
    
    # 添加LangSmith追踪器（如果启用）
    tracer = study_abroad_tracer.get_tracer()
    if tracer:
        callbacks.append(tracer)
    
    return callbacks

def is_langsmith_enabled() -> bool:
    """检查LangSmith是否启用"""
    return study_abroad_tracer.enabled

def log_agent_metrics(
    user_id: str,
    input_message: str,
    output_message: str,
    execution_time: float,
    tool_calls: int,
    error: Optional[str] = None
):
    """记录Agent性能指标"""
    metrics = {
        "user_id": user_id,
        "input_length": len(input_message),
        "output_length": len(output_message),
        "execution_time": execution_time,
        "tool_calls": tool_calls,
        "error": error,
        "timestamp": datetime.now().isoformat()
    }
    
    if is_langsmith_enabled():
        logger.info(f"📊 Agent性能指标: {metrics}")
    else:
        logger.info(f"📊 [本地] Agent性能指标: {metrics}")

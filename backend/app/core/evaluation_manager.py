"""
LangSmith 评估数据集管理工具
用于创建、管理和使用评估数据集来测试AI留学规划师的性能
"""
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path

from app.core.langsmith_config import study_abroad_evaluator, is_langsmith_enabled
from app.agents.langgraph.agent_graph import AdvancedPlannerAgent


class StudyAbroadDatasetManager:
    """留学规划师评估数据集管理器"""
    
    def __init__(self):
        self.evaluator = study_abroad_evaluator
        self.agent = AdvancedPlannerAgent()
        self.datasets_dir = Path("evaluation_datasets")
        self.datasets_dir.mkdir(exist_ok=True)
    
    def create_standard_datasets(self):
        """创建标准评估数据集"""
        datasets = {
            "基础咨询问题": self._get_basic_consultation_examples(),
            "学校推荐场景": self._get_school_recommendation_examples(),
            "申请规划场景": self._get_application_planning_examples(),
            "文书指导场景": self._get_essay_guidance_examples(),
            "时间规划场景": self._get_timeline_planning_examples()
        }
        
        for dataset_name, examples in datasets.items():
            self._create_dataset_with_examples(dataset_name, examples)
    
    def _create_dataset_with_examples(self, dataset_name: str, examples: List[Dict]):
        """创建数据集并添加示例"""
        print(f"📊 创建评估数据集: {dataset_name}")
        
        # 创建本地JSON文件
        dataset_file = self.datasets_dir / f"{dataset_name}.json"
        with open(dataset_file, 'w', encoding='utf-8') as f:
            json.dump(examples, f, ensure_ascii=False, indent=2)
        
        if is_langsmith_enabled():
            # 创建LangSmith数据集
            dataset_id = self.evaluator.create_evaluation_dataset(
                dataset_name=dataset_name,
                description=f"AI留学规划师评估数据集 - {dataset_name}"
            )
            
            if dataset_id:
                # 添加示例到LangSmith
                for example in examples:
                    self.evaluator.add_evaluation_example(
                        dataset_name=dataset_name,
                        input_data=example["input"],
                        expected_output=example["expected_output"],
                        metadata=example.get("metadata", {})
                    )
                print(f"✅ LangSmith数据集创建成功: {dataset_name}")
        else:
            print(f"📝 本地数据集文件已保存: {dataset_file}")
    
    def _get_basic_consultation_examples(self) -> List[Dict]:
        """基础咨询问题示例"""
        return [
            {
                "input": {
                    "input": "我想申请美国的计算机科学硕士，需要准备什么？",
                    "user_id": "test_user_1"
                },
                "expected_output": {
                    "contains_keywords": ["GRE", "TOEFL", "GPA", "推荐信", "个人陈述", "研究经历"],
                    "response_type": "comprehensive_guidance",
                    "tone": "professional_friendly"
                },
                "metadata": {
                    "category": "基础咨询",
                    "difficulty": "easy",
                    "expected_tools": ["knowledge_base_search", "find_mentors_tool"]
                }
            },
            {
                "input": {
                    "input": "英国和美国的研究生申请有什么区别？",
                    "user_id": "test_user_2"
                },
                "expected_output": {
                    "contains_keywords": ["申请时间", "学制", "费用", "签证", "录取要求"],
                    "response_type": "comparison_analysis",
                    "tone": "educational"
                },
                "metadata": {
                    "category": "国家对比",
                    "difficulty": "medium",
                    "expected_tools": ["knowledge_base_search", "web_search"]
                }
            }
        ]
    
    def _get_school_recommendation_examples(self) -> List[Dict]:
        """学校推荐场景示例"""
        return [
            {
                "input": {
                    "input": "我的GPA是3.5，GRE320，想申请美国TOP50的计算机科学硕士，有什么推荐？",
                    "user_id": "test_user_3"
                },
                "expected_output": {
                    "contains_keywords": ["匹配", "保底", "冲刺", "具体学校名称"],
                    "response_type": "personalized_recommendation",
                    "tone": "analytical"
                },
                "metadata": {
                    "category": "学校推荐",
                    "difficulty": "medium",
                    "user_profile": {"gpa": 3.5, "gre": 320, "major": "cs"},
                    "expected_tools": ["web_search", "find_mentors_tool"]
                }
            }
        ]
    
    def _get_application_planning_examples(self) -> List[Dict]:
        """申请规划场景示例"""
        return [
            {
                "input": {
                    "input": "我现在大三下学期，想明年秋季入学，应该怎么规划申请时间？",
                    "user_id": "test_user_4"
                },
                "expected_output": {
                    "contains_keywords": ["时间轴", "deadlines", "标准化考试", "文书", "推荐信"],
                    "response_type": "timeline_planning",
                    "tone": "actionable"
                },
                "metadata": {
                    "category": "时间规划",
                    "difficulty": "medium",
                    "timeline": "junior_spring_to_senior_fall",
                    "expected_tools": ["knowledge_base_search"]
                }
            }
        ]
    
    def _get_essay_guidance_examples(self) -> List[Dict]:
        """文书指导场景示例"""
        return [
            {
                "input": {
                    "input": "计算机科学的个人陈述应该包含哪些内容？有什么写作技巧？",
                    "user_id": "test_user_5"
                },
                "expected_output": {
                    "contains_keywords": ["研究兴趣", "项目经历", "职业目标", "结构", "技巧"],
                    "response_type": "writing_guidance",
                    "tone": "instructional"
                },
                "metadata": {
                    "category": "文书指导",
                    "difficulty": "medium",
                    "document_type": "personal_statement",
                    "expected_tools": ["knowledge_base_search", "find_services_tool"]
                }
            }
        ]
    
    def _get_timeline_planning_examples(self) -> List[Dict]:
        """时间规划场景示例"""
        return [
            {
                "input": {
                    "input": "2025年秋季入学的申请，现在12月份还来得及吗？",
                    "user_id": "test_user_6"
                },
                "expected_output": {
                    "contains_keywords": ["spring intake", "deadline", "rush", "建议"],
                    "response_type": "urgent_planning",
                    "tone": "realistic_supportive"
                },
                "metadata": {
                    "category": "紧急规划",
                    "difficulty": "hard",
                    "timing": "late_application_cycle",
                    "expected_tools": ["web_search", "knowledge_base_search"]
                }
            }
        ]
    
    async def run_evaluation_on_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """在指定数据集上运行评估"""
        dataset_file = self.datasets_dir / f"{dataset_name}.json"
        
        if not dataset_file.exists():
            print(f"❌ 数据集文件不存在: {dataset_file}")
            return {}
        
        with open(dataset_file, 'r', encoding='utf-8') as f:
            examples = json.load(f)
        
        print(f"🧪 开始在数据集 '{dataset_name}' 上运行评估...")
        results = []
        
        for i, example in enumerate(examples):
            print(f"  正在评估示例 {i+1}/{len(examples)}...")
            
            try:
                # 运行Agent
                agent_response = await self.agent.ainvoke(example["input"])
                
                # 简单的评估逻辑
                evaluation_result = self._evaluate_response(
                    agent_response,
                    example["expected_output"],
                    example.get("metadata", {})
                )
                
                results.append({
                    "example_id": i,
                    "input": example["input"],
                    "agent_output": agent_response["output"],
                    "expected": example["expected_output"],
                    "evaluation": evaluation_result,
                    "execution_time": agent_response.get("metadata", {}).get("execution_time", 0)
                })
                
            except Exception as e:
                print(f"    ❌ 示例 {i+1} 执行失败: {str(e)}")
                results.append({
                    "example_id": i,
                    "error": str(e)
                })
        
        # 计算总体评估结果
        evaluation_summary = self._calculate_evaluation_summary(results)
        
        # 保存评估结果
        result_file = self.datasets_dir / f"{dataset_name}_evaluation_results.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "dataset_name": dataset_name,
                "evaluation_summary": evaluation_summary,
                "detailed_results": results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 评估完成，结果已保存: {result_file}")
        return evaluation_summary
    
    def _evaluate_response(
        self, 
        agent_response: Dict, 
        expected_output: Dict, 
        metadata: Dict
    ) -> Dict[str, Any]:
        """评估Agent响应质量"""
        output = agent_response.get("output", "")
        
        # 检查关键词覆盖率
        expected_keywords = expected_output.get("contains_keywords", [])
        found_keywords = [kw for kw in expected_keywords if kw.lower() in output.lower()]
        keyword_coverage = len(found_keywords) / len(expected_keywords) if expected_keywords else 1.0
        
        # 检查响应长度（太短可能不够详细）
        response_length_score = min(1.0, len(output) / 200) if output else 0.0
        
        # 检查是否包含错误
        has_error = "抱歉" in output or "错误" in output or "失败" in output
        error_penalty = 0.3 if has_error else 0.0
        
        # 综合评分
        overall_score = max(0.0, keyword_coverage * 0.6 + response_length_score * 0.4 - error_penalty)
        
        return {
            "keyword_coverage": keyword_coverage,
            "found_keywords": found_keywords,
            "response_length": len(output),
            "response_length_score": response_length_score,
            "has_error": has_error,
            "overall_score": overall_score,
            "grade": self._score_to_grade(overall_score)
        }
    
    def _score_to_grade(self, score: float) -> str:
        """将数值评分转换为等级"""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    def _calculate_evaluation_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """计算评估汇总结果"""
        successful_results = [r for r in results if "error" not in r]
        failed_count = len(results) - len(successful_results)
        
        if not successful_results:
            return {
                "total_examples": len(results),
                "successful_examples": 0,
                "failed_examples": failed_count,
                "success_rate": 0.0,
                "average_score": 0.0,
                "grade_distribution": {}
            }
        
        scores = [r["evaluation"]["overall_score"] for r in successful_results]
        grades = [r["evaluation"]["grade"] for r in successful_results]
        
        grade_distribution = {}
        for grade in ["A", "B", "C", "D", "F"]:
            grade_distribution[grade] = grades.count(grade)
        
        return {
            "total_examples": len(results),
            "successful_examples": len(successful_results),
            "failed_examples": failed_count,
            "success_rate": len(successful_results) / len(results),
            "average_score": sum(scores) / len(scores),
            "average_keyword_coverage": sum(r["evaluation"]["keyword_coverage"] for r in successful_results) / len(successful_results),
            "grade_distribution": grade_distribution,
            "execution_stats": {
                "avg_execution_time": sum(r.get("execution_time", 0) for r in successful_results) / len(successful_results),
                "max_execution_time": max(r.get("execution_time", 0) for r in successful_results),
                "min_execution_time": min(r.get("execution_time", 0) for r in successful_results)
            }
        }
    
    def get_standard_datasets(self) -> Dict[str, Dict]:
        """获取标准评估数据集"""
        datasets = {}
        
        # 基础咨询数据集
        datasets["basic_consultation"] = {
            "name": "基础留学咨询",
            "description": "测试Agent对基础留学问题的回答质量",
            "examples": [
                {
                    "input": "我想申请美国的计算机科学硕士，需要什么条件？",
                    "expected_topics": ["GPA要求", "语言成绩", "GRE", "工作经验", "推荐信"],
                    "evaluation_criteria": ["准确性", "完整性", "实用性"]
                },
                {
                    "input": "英国和美国的留学费用大概是多少？",
                    "expected_topics": ["学费", "生活费", "奖学金", "打工政策"],
                    "evaluation_criteria": ["准确性", "时效性", "对比分析"]
                },
                {
                    "input": "我的背景适合申请哪些学校？",
                    "expected_topics": ["个人评估", "学校推荐", "申请策略"],
                    "evaluation_criteria": ["个性化", "准确性", "可操作性"]
                }
            ]
        }
        
        # 专业规划数据集
        datasets["career_planning"] = {
            "name": "专业与职业规划", 
            "description": "测试Agent对专业选择和职业规划的建议质量",
            "examples": [
                {
                    "input": "我学的是金融，想转到数据科学，有什么建议？",
                    "expected_topics": ["转专业准备", "先修课程", "项目经验", "技能提升"],
                    "evaluation_criteria": ["转换性", "实用性", "可行性"]
                },
                {
                    "input": "人工智能专业的就业前景如何？",
                    "expected_topics": ["行业趋势", "就业机会", "薪资水平", "技能要求"],
                    "evaluation_criteria": ["前瞻性", "准确性", "全面性"]
                }
            ]
        }
        
        # 申请流程数据集
        datasets["application_process"] = {
            "name": "申请流程指导",
            "description": "测试Agent对申请流程的指导质量",
            "examples": [
                {
                    "input": "申请研究生的时间线是什么样的？",
                    "expected_topics": ["申请时间表", "准备阶段", "截止日期", "关键节点"],
                    "evaluation_criteria": ["时序性", "完整性", "实用性"]
                },
                {
                    "input": "如何写好个人陈述？",
                    "expected_topics": ["结构要求", "内容要点", "写作技巧", "常见错误"],
                    "evaluation_criteria": ["指导性", "可操作性", "专业性"]
                }
            ]
        }
        
        return datasets


# 使用示例
async def main():
    """运行评估示例"""
    dataset_manager = StudyAbroadDatasetManager()
    
    # 创建标准数据集
    print("📊 创建标准评估数据集...")
    dataset_manager.create_standard_datasets()
    
    # 运行评估
    print("\n🧪 运行基础咨询问题评估...")
    results = await dataset_manager.run_evaluation_on_dataset("基础咨询问题")
    
    print(f"\n📈 评估结果汇总:")
    print(f"  成功率: {results.get('success_rate', 0):.1%}")
    print(f"  平均得分: {results.get('average_score', 0):.2f}")
    print(f"  等级分布: {results.get('grade_distribution', {})}")


if __name__ == "__main__":
    asyncio.run(main())

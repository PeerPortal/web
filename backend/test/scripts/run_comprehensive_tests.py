#!/usr/bin/env python3
"""
启航引路人平台 - 综合测试套件
运行所有测试并生成详细报告
"""
import subprocess
import sys
import time
import json
from datetime import datetime
from pathlib import Path

class TestSuiteRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {
            'start_time': datetime.now(),
            'tests': {},
            'summary': {
                'total_suites': 0,
                'passed_suites': 0,
                'failed_suites': 0,
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0
            }
        }
    
    def run_test_script(self, script_name: str, description: str) -> dict:
        """运行单个测试脚本"""
        print(f"\n🧪 运行测试: {description}")
        print("=" * 60)
        
        script_path = self.project_root / script_name
        
        if not script_path.exists():
            print(f"❌ 测试脚本不存在: {script_path}")
            return {
                'success': False,
                'error': f"Script not found: {script_name}",
                'duration': 0,
                'output': ""
            }
        
        start_time = time.time()
        
        try:
            # 运行测试脚本
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            return {
                'success': success,
                'return_code': result.returncode,
                'duration': duration,
                'output': result.stdout,
                'error': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            print(f"❌ 测试超时 (>5分钟): {script_name}")
            return {
                'success': False,
                'error': "Test timeout (>5 minutes)",
                'duration': 300,
                'output': ""
            }
        except Exception as e:
            print(f"❌ 运行测试失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'duration': 0,
                'output': ""
            }
    
    def check_server_status(self) -> bool:
        """检查服务器是否运行"""
        print("🔍 检查服务器状态...")
        
        try:
            import requests
            response = requests.get("http://localhost:8001/health", timeout=10)
            if response.status_code == 200:
                print("✅ 服务器运行正常")
                return True
            else:
                print(f"⚠️ 服务器响应异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到服务器: {str(e)}")
            print("💡 请确保服务器正在运行: ./start_server.sh")
            return False
    
    def run_all_tests(self):
        """运行所有测试套件"""
        print("🚀 启航引路人平台 - 综合测试套件")
        print("=" * 80)
        print(f"📅 开始时间: {self.test_results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📍 项目路径: {self.project_root}")
        print("=" * 80)
        
        # 检查服务器状态
        server_running = self.check_server_status()
        
        # 定义测试套件
        test_suites = [
            {
                'script': 'test_database_comprehensive.py',
                'name': '数据库测试',
                'description': '测试数据库连接、表结构和基本操作',
                'require_server': False
            },
            {
                'script': 'test_api_comprehensive.py',
                'name': 'API功能测试',
                'description': '测试所有API端点的功能性和安全性',
                'require_server': True
            }
        ]
        
        # 运行每个测试套件
        for suite in test_suites:
            self.test_results['summary']['total_suites'] += 1
            
            if suite['require_server'] and not server_running:
                print(f"\n⚠️ 跳过 {suite['name']}: 需要服务器运行")
                self.test_results['tests'][suite['name']] = {
                    'success': False,
                    'error': 'Server not running',
                    'duration': 0,
                    'skipped': True
                }
                self.test_results['summary']['failed_suites'] += 1
                continue
            
            result = self.run_test_script(suite['script'], suite['description'])
            self.test_results['tests'][suite['name']] = result
            
            if result['success']:
                self.test_results['summary']['passed_suites'] += 1
                print(f"✅ {suite['name']} 通过 ({result['duration']:.1f}s)")
            else:
                self.test_results['summary']['failed_suites'] += 1
                print(f"❌ {suite['name']} 失败 ({result['duration']:.1f}s)")
        
        # 运行原有的测试脚本（如果存在）
        legacy_tests = [
            ('test/check_database_complete.py', '数据库完整性检查'),
            ('test/test_all_api.py', '传统API测试')
        ]
        
        for script_path, description in legacy_tests:
            full_path = self.project_root / script_path
            if full_path.exists():
                self.test_results['summary']['total_suites'] += 1
                result = self.run_test_script(script_path, f"传统测试: {description}")
                self.test_results['tests'][f"传统-{description}"] = result
                
                if result['success']:
                    self.test_results['summary']['passed_suites'] += 1
                else:
                    self.test_results['summary']['failed_suites'] += 1
        
        # 生成测试报告
        self.generate_report()
        
        # 返回总体测试结果
        return self.test_results['summary']['failed_suites'] == 0
    
    def generate_report(self):
        """生成测试报告"""
        end_time = datetime.now()
        total_duration = (end_time - self.test_results['start_time']).total_seconds()
        
        print("\n" + "=" * 80)
        print("📊 综合测试报告")
        print("=" * 80)
        print(f"🕐 开始时间: {self.test_results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🕐 结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ 总耗时: {total_duration:.1f} 秒")
        print()
        
        # 测试套件统计
        summary = self.test_results['summary']
        print(f"📈 测试套件统计:")
        print(f"   总套件数: {summary['total_suites']}")
        print(f"   通过套件: {summary['passed_suites']} ✅")
        print(f"   失败套件: {summary['failed_suites']} ❌")
        success_rate = (summary['passed_suites'] / summary['total_suites'] * 100) if summary['total_suites'] > 0 else 0
        print(f"   成功率: {success_rate:.1f}%")
        print()
        
        # 详细结果
        print("📋 详细结果:")
        for test_name, result in self.test_results['tests'].items():
            status = "✅ 通过" if result['success'] else "❌ 失败"
            duration = f"({result['duration']:.1f}s)"
            
            if result.get('skipped'):
                status = "⚠️ 跳过"
                reason = f"- {result.get('error', 'Unknown reason')}"
            else:
                reason = f"- {result.get('error', '')}" if not result['success'] else ""
            
            print(f"   {status} | {test_name} {duration} {reason}")
        
        print("=" * 80)
        
        # 生成JSON报告文件
        report_file = self.project_root / f"test_report_{int(time.time())}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                # 准备可序列化的数据
                serializable_data = {
                    'start_time': self.test_results['start_time'].isoformat(),
                    'end_time': end_time.isoformat(),
                    'total_duration': total_duration,
                    'summary': summary,
                    'tests': {}
                }
                
                # 只保留可序列化的数据
                for test_name, result in self.test_results['tests'].items():
                    serializable_data['tests'][test_name] = {
                        'success': result['success'],
                        'duration': result['duration'],
                        'error': result.get('error', ''),
                        'return_code': result.get('return_code', -1)
                    }
                
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            
            print(f"📄 详细报告已保存到: {report_file}")
        except Exception as e:
            print(f"⚠️ 无法保存报告文件: {str(e)}")
        
        # 给出建议
        if summary['failed_suites'] == 0:
            print("🎉 所有测试套件都通过了！系统运行正常。")
        elif summary['failed_suites'] == 1:
            print("⚠️ 有1个测试套件失败，请检查具体问题。")
        else:
            print(f"🚨 有{summary['failed_suites']}个测试套件失败，建议检查系统配置。")
        
        print("\n💡 建议:")
        print("   - 如果数据库测试失败，请检查 .env 配置和数据库连接")
        print("   - 如果API测试失败，请确保服务器在 http://localhost:8001 运行")
        print("   - 可以单独运行具体的测试脚本进行调试")

def main():
    """主函数"""
    runner = TestSuiteRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n🎊 所有测试通过！系统运行正常。")
        sys.exit(0)
    else:
        print("\n💥 部分测试失败，请查看详细报告。")
        sys.exit(1)

if __name__ == "__main__":
    main()

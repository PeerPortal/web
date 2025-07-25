#!/usr/bin/env python3
"""
修复CRUD文件中的Supabase客户端调用
"""

import re

def fix_supabase_client_calls():
    """修复所有CRUD文件中的supabase_client调用"""
    
    files_to_fix = [
        '/Users/frederick/Documents/peerpotal/backend/app/crud/crud_mentor_fixed.py',
        '/Users/frederick/Documents/peerpotal/backend/app/crud/crud_student_fixed.py', 
        '/Users/frederick/Documents/peerpotal/backend/app/crud/crud_service_new.py'
    ]
    
    for file_path in files_to_fix:
        print(f"🔧 修复 {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换导入
            content = content.replace(
                'from app.core.supabase_client import supabase_client',
                'from app.core.supabase_client import get_supabase_client'
            )
            
            # 在每个异步方法开始处添加客户端获取
            # 查找所有 await supabase_client. 的调用，并在前面添加客户端获取
            
            # 使用正则表达式匹配方法
            pattern = r'(async def .*?\(.*?\):.*?""".*?""".*?try:)(.*?)(await supabase_client\.)'
            
            def replace_method(match):
                method_def = match.group(1)
                method_body = match.group(2)
                supabase_call = match.group(3)
                
                # 添加客户端获取
                client_init = '\n            supabase_client = await get_supabase_client()'
                return method_def + client_init + method_body + supabase_call
            
            # 对于每个方法，我们需要手动添加客户端获取
            # 更简单的方法：替换所有await supabase_client调用前添加客户端获取
            
            # 先找到所有使用supabase_client的方法
            methods_with_supabase = []
            lines = content.split('\n')
            current_method = None
            in_method = False
            
            for i, line in enumerate(lines):
                if line.strip().startswith('async def '):
                    current_method = i
                    in_method = True
                elif line.strip().startswith('def ') and not line.strip().startswith('async def'):
                    in_method = False
                elif 'await supabase_client.' in line and in_method and current_method is not None:
                    if current_method not in methods_with_supabase:
                        methods_with_supabase.append(current_method)
            
            # 在每个方法的try块后添加客户端获取
            for method_line in methods_with_supabase:
                # 找到该方法的try语句
                for i in range(method_line, len(lines)):
                    if 'try:' in lines[i]:
                        # 在try后插入客户端获取
                        indent = len(lines[i]) - len(lines[i].lstrip())
                        client_line = ' ' * (indent + 4) + 'supabase_client = await get_supabase_client()'
                        lines.insert(i + 1, client_line)
                        break
            
            content = '\n'.join(lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ {file_path} 修复完成")
        
        except Exception as e:
            print(f"❌ 修复 {file_path} 失败: {e}")
    
    print("🎉 所有CRUD文件修复完成！")

if __name__ == "__main__":
    fix_supabase_client_calls()

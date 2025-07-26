"""
创建一个快速修复脚本来替换路由引入
"""

import os

def update_main_app():
    """更新 main.py 以使用修复后的路由"""
    main_file = '/Users/frederick/Documents/peerpotal/backend/app/main.py'
    
    # 读取当前内容
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换路由导入
    replacements = [
        ('from .api.routers import auth_router, mentor_router, student_router, service_router, matching_router', 
         'from .api.routers import auth_router, service_router, matching_router\nfrom .api.routers.mentor_router_fixed import router as mentor_router\nfrom .api.routers.student_router_fixed import router as student_router'),
        ('app.include_router(mentor_router.router, prefix="/api/v1/mentors", tags=["mentors"])', 
         'app.include_router(mentor_router, prefix="/api/v1/mentors", tags=["mentors"])'),
        ('app.include_router(student_router.router, prefix="/api/v1/students", tags=["students"])', 
         'app.include_router(student_router, prefix="/api/v1/students", tags=["students"])')
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    # 写回文件
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ main.py 已更新以使用修复后的路由")

if __name__ == "__main__":
    update_main_app()
    print("🎉 路由更新完成！")

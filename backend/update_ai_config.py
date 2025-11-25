"""
临时脚本：更新 .env 文件配置为 DeepSeek
使用后可删除此文件
"""

import os
from pathlib import Path

def update_env_file():
    env_path = Path(__file__).parent / '.env'
    
    # 读取现有配置
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        print("⚠️  .env 文件不存在，将创建新文件")
        lines = []
    
    # AI配置项
    ai_config = {
        'AI_PROVIDER': 'deepseek',
        'AI_API_KEY': 'sk-c1991f56e6684c288ce54ee5034f4c04',
        'AI_BASE_URL': 'https://api.deepseek.com',
        'AI_MODEL': 'deepseek-chat',
        'AI_TIMEOUT': '60',
        'AI_MAX_TOKENS': '4096'
    }
    
    # 更新或添加配置
    updated_lines = []
    ai_keys_found = set()
    in_ai_section = False
    
    for line in lines:
        stripped = line.strip()
        
        # 检测AI配置区域
        if '# AI 服务配置' in line or '# AI服务配置' in line:
            in_ai_section = True
        elif stripped.startswith('# ===') and in_ai_section:
            in_ai_section = False
        
        # 检查是否是AI配置项
        updated = False
        for key, value in ai_config.items():
            if stripped.startswith(f'{key}='):
                updated_lines.append(f'{key}={value}\n')
                ai_keys_found.add(key)
                updated = True
                break
        
        if not updated:
            updated_lines.append(line)
    
    # 添加缺失的AI配置
    missing_keys = set(ai_config.keys()) - ai_keys_found
    if missing_keys:
        # 查找AI配置区域的结束位置
        insert_index = len(updated_lines)
        for i, line in enumerate(updated_lines):
            if '# 服务器配置' in line:
                insert_index = i
                break
        
        # 如果没有AI配置区域，添加一个
        if 'AI_PROVIDER' not in ai_keys_found:
            ai_section = [
                '\n',
                '# ======================================\n',
                '# AI 服务配置\n',
                '# ======================================\n'
            ]
            for key, value in ai_config.items():
                ai_section.append(f'{key}={value}\n')
            ai_section.append('\n')
            
            updated_lines = updated_lines[:insert_index] + ai_section + updated_lines[insert_index:]
    
    # 写入更新后的配置
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print("✅ .env 文件已更新为 DeepSeek 配置！")
    print("\n当前AI配置：")
    for key, value in ai_config.items():
        display_value = value if key != 'AI_API_KEY' else value[:15] + '...'
        print(f"  {key} = {display_value}")
    print("\n🚀 重启后端服务以应用新配置")

if __name__ == '__main__':
    update_env_file()

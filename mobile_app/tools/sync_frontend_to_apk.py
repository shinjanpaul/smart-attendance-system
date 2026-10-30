import os
import sys

def sync_frontend():
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    mobile_app_dir = os.path.dirname(tools_dir)
    root_dir = os.path.dirname(mobile_app_dir)
    
    src_html = os.path.join(root_dir, 'frontend', 'app.html')
    if not os.path.exists(src_html):
        src_html = os.path.join(root_dir, 'index.html')
        
    if not os.path.exists(src_html):
        print(f"[Sync] Error: Could not find frontend/app.html or index.html at {src_html}")
        return False

    with open(src_html, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 1. Write to Android Native Assets
    android_assets_dir = os.path.join(mobile_app_dir, 'android', 'app', 'src', 'main', 'assets')
    os.makedirs(android_assets_dir, exist_ok=True)
    android_target = os.path.join(android_assets_dir, 'index.html')
    with open(android_target, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[Sync] [OK] Packaged native Android asset: {android_target} ({len(html_content)} bytes)")

    # 2. Write to Flutter Assets
    flutter_assets_dir = os.path.join(mobile_app_dir, 'assets')
    os.makedirs(flutter_assets_dir, exist_ok=True)
    flutter_target = os.path.join(flutter_assets_dir, 'index.html')
    with open(flutter_target, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[Sync] [OK] Packaged Flutter asset: {flutter_target}")

    return True

if __name__ == '__main__':
    sync_frontend()

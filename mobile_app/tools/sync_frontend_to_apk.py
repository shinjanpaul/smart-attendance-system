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

    # Enhance backend routing for native Android APK:
    # On Android phone WebView, file:/// has no local server.
    # It must connect to the permanent Ngrok tunnel (or custom server host) to reach the laptop's Django & dlib AI backend!
    target_backend_block = """    const NGROK_HOST = 'famished-savor-seventeen.ngrok-free.dev';
    const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const isGitHub = window.location.hostname.includes('github.io');
    const isTunnel = window.location.hostname.includes('ngrok') || window.location.hostname.includes('trycloudflare.com');
    const isAndroidApp = window.location.protocol === 'file:' || navigator.userAgent.includes('VeriFaceAndroid');

    let BACKEND_BASE = 'http://127.0.0.1:8000';
    if (isAndroidApp) {
      BACKEND_BASE = localStorage.getItem('veriface_backend_override') || `https://${NGROK_HOST}`;
    } else if (isGitHub) {
      BACKEND_BASE = `https://${NGROK_HOST}`;
    } else if (isTunnel) {
      BACKEND_BASE = window.location.origin;
    } else if (isLocal) {
      BACKEND_BASE = 'http://127.0.0.1:8000';
    } else if (window.location.port === '8080' || window.location.port === '8000') {
      BACKEND_BASE = `${window.location.protocol}//${window.location.hostname}:8000`;
    } else {
      BACKEND_BASE = window.location.origin;
    }"""

    # Replace the old BACKEND_BASE block if present
    if "const NGROK_HOST = 'famished-savor-seventeen.ngrok-free.dev';" in html_content:
        # Find start and end of backend base setup
        start_idx = html_content.find("const NGROK_HOST = 'famished-savor-seventeen.ngrok-free.dev';")
        end_str = "const API_BASE = `${BACKEND_BASE}/api`;"
        end_idx = html_content.find(end_str)
        if start_idx != -1 and end_idx != -1:
            html_content = html_content[:start_idx] + target_backend_block + "\n    " + html_content[end_idx:]

    # Also enhance WebSocket host resolution for Android App
    old_ws_block = """      const isGitHubHost = window.location.hostname.includes('github.io');
      const isTunnelHost = window.location.hostname.includes('ngrok') || window.location.hostname.includes('trycloudflare.com');
      const protocol = (window.location.protocol === 'https:' || isGitHubHost || isTunnelHost) ? 'wss:' : 'ws:';
      let host = '127.0.0.1:8000';
      if (isGitHubHost) {
        host = 'famished-savor-seventeen.ngrok-free.dev';
      } else if (isTunnelHost) {
        host = window.location.host;
      } else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        host = '127.0.0.1:8000';
      } else if (window.location.hostname) {
        host = `${window.location.hostname}:8000`;
      }"""

    new_ws_block = """      const isGitHubHost = window.location.hostname.includes('github.io');
      const isTunnelHost = window.location.hostname.includes('ngrok') || window.location.hostname.includes('trycloudflare.com');
      const isAppHost = window.location.protocol === 'file:' || navigator.userAgent.includes('VeriFaceAndroid');
      const protocol = (window.location.protocol === 'https:' || isGitHubHost || isTunnelHost || isAppHost) ? 'wss:' : 'ws:';
      let host = '127.0.0.1:8000';
      if (isAppHost) {
        const customBackend = localStorage.getItem('veriface_backend_override');
        if (customBackend) {
          try { host = new URL(customBackend).host; } catch(e) { host = 'famished-savor-seventeen.ngrok-free.dev'; }
        } else {
          host = 'famished-savor-seventeen.ngrok-free.dev';
        }
      } else if (isGitHubHost) {
        host = 'famished-savor-seventeen.ngrok-free.dev';
      } else if (isTunnelHost) {
        host = window.location.host;
      } else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        host = '127.0.0.1:8000';
      } else if (window.location.hostname) {
        host = `${window.location.hostname}:8000`;
      }"""

    if old_ws_block in html_content:
        html_content = html_content.replace(old_ws_block, new_ws_block)

    # Enhance network status header text for Android App
    old_status_text = "connStatus.textContent = isGitHub ? 'Cloud Web • 24/7 Active' : 'API Live • 127.0.0.1:8000';"
    new_status_text = "connStatus.textContent = isAndroidApp ? 'VeriFace AI • Mobile App' : (isGitHub ? 'Cloud Web • 24/7 Active' : 'API Live • 127.0.0.1:8000');"
    if old_status_text in html_content:
        html_content = html_content.replace(old_status_text, new_status_text)

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

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil

def log(msg):
    print(f"[Flutter Setup] {msg}", flush=True)

def configure_git():
    """Fix Windows Schannel TLS decryption bug (SEC_E_DECRYPT_FAILURE 0x80090330)"""
    try:
        subprocess.run(["git", "config", "--global", "http.sslBackend", "openssl"], capture_output=True)
        subprocess.run(["git", "config", "--global", "http.postBuffer", "524288000"], capture_output=True)
        log("Configured Git SSL backend to OpenSSL (bypassing Windows Schannel TLS bug)")
    except Exception as e:
        log(f"Git config notice: {e}")

def download_and_extract(url, dest_dir, zip_name="archive.zip"):
    os.makedirs(dest_dir, exist_ok=True)
    temp_zip = os.path.join(dest_dir, zip_name)

    log(f"Downloading {url} ...")
    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = downloaded * 100 / total_size
            mb_down = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\rDownloading: {mb_down:.1f}MB / {mb_total:.1f}MB ({percent:.1f}%)", end="", flush=True)

    try:
        urllib.request.urlretrieve(url, temp_zip, reporthook=progress_hook)
        print()
        log(f"Extracting into {dest_dir} ...")
        with zipfile.ZipFile(temp_zip, 'r') as z:
            z.extractall(dest_dir)
        try:
            os.remove(temp_zip)
        except Exception:
            pass
        return True
    except Exception as e:
        print()
        log(f"Notice: Failed to download {url}: {e}")
        if os.path.exists(temp_zip):
            try:
                os.remove(temp_zip)
            except Exception:
                pass
        return False

def main():
    flutter_root = r"C:\src\flutter"
    if not os.path.exists(flutter_root):
        log(f"Error: Flutter directory not found at {flutter_root}")
        sys.exit(1)

    configure_git()

    engine_version_file = os.path.join(flutter_root, "bin", "internal", "engine.version")
    if not os.path.exists(engine_version_file):
        log(f"Error: engine.version not found at {engine_version_file}")
        sys.exit(1)

    with open(engine_version_file, "r") as f:
        engine_version = f.read().strip()

    log(f"Detected Flutter Engine version: {engine_version}")

    cache_dir = os.path.join(flutter_root, "bin", "cache")
    os.makedirs(cache_dir, exist_ok=True)

    # 1. Clean up lingering locks and corrupt downloads
    lock_file = os.path.join(cache_dir, "flutter.bat.lock")
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
            log("Removed stale lock file flutter.bat.lock")
        except Exception:
            pass

    downloads_dir = os.path.join(cache_dir, "downloads")
    if os.path.exists(downloads_dir):
        try:
            shutil.rmtree(downloads_dir, ignore_errors=True)
            log("Cleaned up temporary downloads directory")
        except Exception:
            pass

    # 2. Verify Dart SDK
    dart_sdk_dir = os.path.join(cache_dir, "dart-sdk")
    dart_exe = os.path.join(dart_sdk_dir, "bin", "dart.exe")
    engine_stamp = os.path.join(cache_dir, "engine-dart-sdk.stamp")
    engine_version_path = os.path.join(cache_dir, "engine.stamp")

    if not (os.path.exists(dart_exe) and os.path.exists(engine_stamp)):
        log("Downloading Dart SDK (~180 MB)...")
        dart_url = f"https://storage.googleapis.com/flutter_infra_release/flutter/{engine_version}/dart-sdk-windows-x64.zip"
        if not download_and_extract(dart_url, cache_dir, "dart-sdk-windows-x64.zip"):
            sys.exit(1)
        with open(engine_stamp, "w") as f:
            f.write(engine_version)
        with open(engine_version_path, "w") as f:
            f.write(engine_version)
    else:
        log("Dart SDK is already installed and verified.")

    # 3. Ensure sky_engine package is present
    sky_engine_dir = os.path.join(cache_dir, "pkg", "sky_engine")
    sky_engine_ui = os.path.join(sky_engine_dir, "lib", "ui", "ui.dart")
    if not os.path.exists(sky_engine_ui):
        log("Downloading and extracting sky_engine package...")
        sky_url = f"https://storage.googleapis.com/flutter_infra_release/flutter/{engine_version}/sky_engine.zip"
        pkg_dir = os.path.join(cache_dir, "pkg")
        download_and_extract(sky_url, pkg_dir, "sky_engine.zip")
        if os.path.exists(sky_engine_ui):
            log("[OK] sky_engine package ready!")
    else:
        log("sky_engine package is already installed.")

    # 4. Ensure flutter_web_sdk is present
    web_sdk_dir = os.path.join(cache_dir, "flutter_web_sdk")
    web_sdk_kernel = os.path.join(web_sdk_dir, "kernel", "flutter_ddc_sdk.dill")
    if not os.path.exists(web_sdk_dir) or not os.path.exists(web_sdk_kernel):
        log("Downloading and extracting flutter_web_sdk...")
        web_url = f"https://storage.googleapis.com/flutter_infra_release/flutter/{engine_version}/flutter_web_sdk.zip"
        download_and_extract(web_url, cache_dir, "flutter_web_sdk.zip")
        if os.path.exists(web_sdk_dir):
            log("[OK] flutter_web_sdk ready!")
    else:
        log("flutter_web_sdk is already installed.")

    # 5. Clean up downloads directory once more
    if os.path.exists(downloads_dir):
        try:
            shutil.rmtree(downloads_dir, ignore_errors=True)
        except Exception:
            pass

    log("=" * 60)
    log("All Flutter core artifacts are successfully bootstrapped!")
    log("=" * 60)

if __name__ == "__main__":
    main()

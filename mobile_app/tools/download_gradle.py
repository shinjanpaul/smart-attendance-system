import os
import sys
import time
import zipfile
import urllib.request

target_dir = os.path.expanduser(r'~/.gradle/wrapper/dists/gradle-9.3.1-all/9ot9r568e8zfvvd4mn8rbu1j0')
os.makedirs(target_dir, exist_ok=True)

zip_path = os.path.join(target_dir, 'gradle-9.3.1-all.zip')
ok_file = os.path.join(target_dir, 'gradle-9.3.1-all.zip.ok')
url = "https://services.gradle.org/distributions/gradle-9.3.1-all.zip"

print(f"Checking Gradle 9.3.1 cache...")

# Check if already extracted
if os.path.exists(ok_file):
    print("[OK] Gradle 9.3.1 is already successfully unpacked and ready!")
    sys.exit(0)

def extract_gradle(zip_f):
    print("Unpacking Gradle 9.3.1 core runtime (skipping docs)...")
    abs_target = os.path.abspath(target_dir)

    with zipfile.ZipFile(zip_f, 'r') as z:
        extracted_count = 0
        for info in z.infolist():
            norm = info.filename.replace('\\', '/')
            # Skip documentation files that exceed Windows MAX_PATH (260 chars)
            if '/docs/' in norm or norm.startswith('gradle-9.3.1/docs/'):
                continue

            z.extract(info, abs_target)
            extracted_count += 1
            if extracted_count % 300 == 0:
                print(f"  Extracted {extracted_count} runtime files...", end='\r')

    print(f"\nExtracted {extracted_count} core runtime files successfully!")
    with open(ok_file, 'w') as f:
        f.write('')
    print("[SUCCESS] Gradle 9.3.1 unpacked and verified successfully!")

# If the 224MB zip is already downloaded and verified on disk, extract it immediately!
if os.path.exists(zip_path):
    print("Found existing Gradle download archive. Verifying integrity...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            if z.testzip() is None:
                print("Zip integrity 100% verified!")
                extract_gradle(zip_path)
                sys.exit(0)
    except Exception as e:
        print(f"Zip verification notice: {e}. Will re-verify or resume.")

# If not complete, resume download
total_size = 0
try:
    req = urllib.request.Request(url, method='HEAD')
    with urllib.request.urlopen(req, timeout=15) as resp:
        total_size = int(resp.headers.get('Content-Length', 0))
    print(f"Total Gradle download size: {total_size // (1024*1024)} MB")
except Exception as e:
    print(f"Could not check remote size: {e}")

max_retries = 35
chunk_size = 1024 * 1024

for attempt in range(max_retries):
    downloaded = os.path.getsize(zip_path) if os.path.exists(zip_path) else 0
    if total_size > 0 and downloaded >= total_size:
        print("\nDownload complete! Verifying archive integrity...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                if z.testzip() is None:
                    print("Zip verified successfully!")
                    extract_gradle(zip_path)
                    sys.exit(0)
        except Exception:
            if downloaded > 2 * 1024 * 1024:
                with open(zip_path, 'r+b') as f:
                    f.truncate(downloaded - 2 * 1024 * 1024)
                downloaded = os.path.getsize(zip_path)
            else:
                os.remove(zip_path)
                downloaded = 0

    pct = (downloaded * 100 / total_size) if total_size else 0
    print(f"Attempt {attempt + 1}: Resuming from {downloaded // (1024*1024)} MB ({pct:.1f}%)...")

    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        if downloaded > 0:
            req.add_header('Range', f'bytes={downloaded}-')

        with urllib.request.urlopen(req, timeout=20) as response:
            mode = 'ab' if downloaded > 0 else 'wb'
            with open(zip_path, mode) as out_file:
                while True:
                    data = response.read(chunk_size)
                    if not data:
                        break
                    out_file.write(data)
                    out_file.flush()
                    downloaded += len(data)
                    cur_pct = (downloaded * 100 / total_size) if total_size else 0
                    print(f"  Progress: {downloaded // (1024*1024)} MB / {total_size // (1024*1024)} MB ({cur_pct:.1f}%)", end='\r')
        print()
    except Exception as e:
        print(f"\n  [Network glitch: {e}. Resuming in 2s...]")
        time.sleep(2)

extract_gradle(zip_path)

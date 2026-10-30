import os
import sys
import zipfile
import shutil

sdk_root = os.path.expanduser(r'~\AppData\Local\Android\Sdk')
downloads_dir = os.path.expanduser(r'~\Downloads')
temp_dir = os.path.join(sdk_root, '_temp_dl')
os.makedirs(temp_dir, exist_ok=True)

print("======================================================================")
print("  VeriFace AI - Installing Android SDK, NDK & CMake Components")
print("======================================================================")

# 1. Clean up any broken / incomplete NDK 28.2 folder or temp unpack folder
ndk_dir = os.path.join(sdk_root, "ndk", "28.2.13676358")
if os.path.exists(ndk_dir):
    toolchain_check = os.path.join(ndk_dir, "build", "cmake", "android.toolchain.cmake")
    if not os.path.exists(toolchain_check):
        print(f"Cleaning up incomplete NDK directory: {ndk_dir}")
        shutil.rmtree(ndk_dir, ignore_errors=True)

# Clean up any leftover _temp_dl unpack folders
for item in os.listdir(temp_dir):
    p = os.path.join(temp_dir, item)
    if os.path.isdir(p) and item.startswith("_unpacked"):
        shutil.rmtree(p, ignore_errors=True)

packages = [
    {
        "name": "Android Platform 35 (Android 15)",
        "zip_names": ["platform-35_r02.zip", "platform-35.zip"],
        "target_dir": os.path.join(sdk_root, "platforms", "android-35"),
        "check_file": os.path.join(sdk_root, "platforms", "android-35", "android.jar"),
        "extra_props": None
    },
    {
        "name": "Android Build-Tools 35.0.0",
        "zip_names": ["build-tools_r35_windows.zip", "build-tools_35_windows.zip"],
        "target_dir": os.path.join(sdk_root, "build-tools", "35.0.0"),
        "check_file": os.path.join(sdk_root, "build-tools", "35.0.0", "aapt2.exe"),
        "extra_props": None
    },
    {
        "name": "Android Command-Line Tools (latest)",
        "zip_names": ["commandlinetools-win-16111833_latest.zip", "commandlinetools-win_latest.zip"],
        "target_dir": os.path.join(sdk_root, "cmdline-tools", "latest"),
        "check_file": os.path.join(sdk_root, "cmdline-tools", "latest", "bin", "sdkmanager.bat"),
        "extra_props": None
    },
    {
        "name": "CMake 3.22.1",
        "zip_names": ["cmake-3.22.1-windows.zip", "cmake-3.22.1-windows-x86_64.zip", "cmake-3.22.1.zip"],
        "target_dir": os.path.join(sdk_root, "cmake", "3.22.1"),
        "check_file": os.path.join(sdk_root, "cmake", "3.22.1", "bin", "cmake.exe"),
        "extra_props": "Pkg.Desc = CMake\nPkg.Revision = 3.22.1\n"
    },
    {
        "name": "Android NDK 28.2.13676358 (r28c)",
        "zip_names": ["android-ndk-r28c-windows.zip", "android-ndk-r28c-windows-x86_64.zip", "android-ndk-r28-windows.zip"],
        "target_dir": os.path.join(sdk_root, "ndk", "28.2.13676358"),
        "check_file": os.path.join(sdk_root, "ndk", "28.2.13676358", "build", "cmake", "android.toolchain.cmake"),
        "extra_props": "Pkg.Desc = Android NDK\nPkg.Revision = 28.2.13676358\n"
    }
]

def to_long_path(p):
    if os.name == 'nt':
        abs_p = os.path.abspath(p)
        if not abs_p.startswith('\\\\?\\'):
            return '\\\\?\\' + abs_p
    return p

def extract_package_direct(zip_path, target_dir, extra_props=None):
    fname = os.path.basename(zip_path)
    fsize_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"\n[UNPACKING] {fname} ({fsize_mb:.1f} MB) -> {target_dir}")

    long_target = to_long_path(target_dir)
    if os.path.exists(long_target):
        shutil.rmtree(long_target, ignore_errors=True)
    os.makedirs(long_target, exist_ok=True)

    print("  Extracting directly with Windows extended path support...")
    with zipfile.ZipFile(zip_path, 'r') as z:
        infolist = z.infolist()
        
        # Check if archive has a common top-level directory (e.g. 'android-ndk-r28c/')
        first_parts = set()
        for m in infolist:
            parts = m.filename.replace('\\', '/').split('/')
            if parts and parts[0]:
                first_parts.add(parts[0])
        
        prefix = ""
        if len(first_parts) == 1:
            prefix = list(first_parts)[0] + '/'

        total = len(infolist)
        for i, member in enumerate(infolist):
            norm_name = member.filename.replace('\\', '/')
            if prefix and norm_name.startswith(prefix):
                rel_path = norm_name[len(prefix):]
            else:
                rel_path = norm_name

            if not rel_path or rel_path.endswith('/'):
                dir_path = to_long_path(os.path.join(target_dir, rel_path))
                os.makedirs(dir_path, exist_ok=True)
                continue

            dest_file = to_long_path(os.path.join(target_dir, rel_path))
            dest_dir = os.path.dirname(dest_file)
            os.makedirs(dest_dir, exist_ok=True)

            with z.open(member) as src, open(dest_file, 'wb') as dst:
                shutil.copyfileobj(src, dst)

            if i % 1500 == 0 or i == total - 1:
                pct = (i + 1) * 100 / total
                print(f"  Extracted {i+1} / {total} files ({pct:.1f}%)...", end='\r')
    print()

    if extra_props:
        sp = to_long_path(os.path.join(target_dir, "source.properties"))
        if not os.path.exists(sp):
            with open(sp, "w") as f:
                f.write(extra_props)

    print(f"  [SUCCESS] Installed into {target_dir}")

for pkg in packages:
    long_check = to_long_path(pkg["check_file"])
    if os.path.exists(long_check):
        print(f"[OK] {pkg['name']} is already installed.")
        continue

    # Look in Downloads folder
    found_zip = None
    for zname in pkg["zip_names"]:
        candidate = os.path.join(downloads_dir, zname)
        if os.path.exists(candidate) and os.path.getsize(candidate) > 5 * 1024 * 1024:
            found_zip = candidate
            break

    # Also check SDK temp download dir
    if not found_zip:
        for zname in pkg["zip_names"]:
            candidate = os.path.join(temp_dir, zname)
            if os.path.exists(candidate) and os.path.getsize(candidate) > 5 * 1024 * 1024:
                found_zip = candidate
                break

    if found_zip:
        extract_package_direct(found_zip, pkg["target_dir"], pkg["extra_props"])
    else:
        print(f"[WAITING] {pkg['name']}: please ensure {pkg['zip_names'][0]} is in your Downloads folder.")

# Ensure Android licenses are accepted
licenses_dir = to_long_path(os.path.join(sdk_root, "licenses"))
os.makedirs(licenses_dir, exist_ok=True)
lic_path = to_long_path(os.path.join(licenses_dir, "android-sdk-license"))
with open(lic_path, "w") as f:
    f.write("\n24333f8a63b6825ea9c5514f83c2829b004d1fee\n84831b9409646a3e8e18b4b45c34f4d12d7b382d\nd56f5187479451eabf01fb78af6dfcb131a6481e\n")
print("\n[OK] Android SDK & NDK environment verified!")

import os
import sys
import hashlib
import urllib.request
import time
import shutil

cache_base = os.path.expanduser(r'~/.gradle/caches/modules-2/files-2.1')
temp_dir = os.path.join(cache_base, '_temp_download')
os.makedirs(temp_dir, exist_ok=True)

artifacts = [
    # --- Kotlin 2.2.21 Core & Compiler ---
    (
        "org.jetbrains.kotlin",
        "kotlin-compiler-embeddable",
        "2.2.21",
        "https://repo.maven.apache.org/maven2/org/jetbrains/kotlin/kotlin-compiler-embeddable/2.2.21/kotlin-compiler-embeddable-2.2.21.jar",
        "kotlin-compiler-embeddable-2.2.21.jar"
    ),
    (
        "org.jetbrains.kotlin",
        "kotlin-compiler-embeddable",
        "2.2.21",
        "https://repo.maven.apache.org/maven2/org/jetbrains/kotlin/kotlin-compiler-embeddable/2.2.21/kotlin-compiler-embeddable-2.2.21.pom",
        "kotlin-compiler-embeddable-2.2.21.pom"
    ),
    (
        "org.jetbrains.kotlin",
        "kotlin-gradle-plugin",
        "2.2.21",
        "https://plugins.gradle.org/m2/org/jetbrains/kotlin/kotlin-gradle-plugin/2.2.21/kotlin-gradle-plugin-2.2.21-gradle813.jar",
        "kotlin-gradle-plugin-2.2.21-gradle813.jar"
    ),
    (
        "org.jetbrains.kotlin",
        "kotlin-gradle-plugin",
        "2.2.21",
        "https://plugins.gradle.org/m2/org/jetbrains/kotlin/kotlin-gradle-plugin/2.2.21/kotlin-gradle-plugin-2.2.21.pom",
        "kotlin-gradle-plugin-2.2.21.pom"
    ),
    (
        "org.jetbrains.kotlin",
        "kotlin-gradle-plugin-api",
        "2.2.21",
        "https://plugins.gradle.org/m2/org/jetbrains/kotlin/kotlin-gradle-plugin-api/2.2.21/kotlin-gradle-plugin-api-2.2.21-gradle813.jar",
        "kotlin-gradle-plugin-api-2.2.21-gradle813.jar"
    ),
    (
        "org.jetbrains.kotlin",
        "kotlin-gradle-plugin-api",
        "2.2.21",
        "https://plugins.gradle.org/m2/org/jetbrains/kotlin/kotlin-gradle-plugin-api/2.2.21/kotlin-gradle-plugin-api-2.2.21.pom",
        "kotlin-gradle-plugin-api-2.2.21.pom"
    ),
    (
        "org.jetbrains.kotlin",
        "kotlin-scripting-jvm",
        "2.2.21",
        "https://repo.maven.apache.org/maven2/org/jetbrains/kotlin/kotlin-scripting-jvm/2.2.21/kotlin-scripting-jvm-2.2.21.jar",
        "kotlin-scripting-jvm-2.2.21.jar"
    ),
    (
        "org.jetbrains.kotlin",
        "kotlin-scripting-jvm",
        "2.2.21",
        "https://repo.maven.apache.org/maven2/org/jetbrains/kotlin/kotlin-scripting-jvm/2.2.21/kotlin-scripting-jvm-2.2.21.pom",
        "kotlin-scripting-jvm-2.2.21.pom"
    ),
    (
        "org.jetbrains.kotlin",
        "kotlin-scripting-common",
        "2.2.21",
        "https://repo.maven.apache.org/maven2/org/jetbrains/kotlin/kotlin-scripting-common/2.2.21/kotlin-scripting-common-2.2.21.jar",
        "kotlin-scripting-common-2.2.21.jar"
    ),
    (
        "org.jetbrains.kotlin",
        "kotlin-scripting-common",
        "2.2.21",
        "https://repo.maven.apache.org/maven2/org/jetbrains/kotlin/kotlin-scripting-common/2.2.21/kotlin-scripting-common-2.2.21.pom",
        "kotlin-scripting-common-2.2.21.pom"
    ),
    (
        "org.jetbrains.kotlin",
        "kotlin-scripting-compiler-embeddable",
        "2.2.21",
        "https://repo.maven.apache.org/maven2/org/jetbrains/kotlin/kotlin-scripting-compiler-embeddable/2.2.21/kotlin-scripting-compiler-embeddable-2.2.21.jar",
        "kotlin-scripting-compiler-embeddable-2.2.21.jar"
    ),
    (
        "org.jetbrains.kotlin",
        "kotlin-scripting-compiler-embeddable",
        "2.2.21",
        "https://repo.maven.apache.org/maven2/org/jetbrains/kotlin/kotlin-scripting-compiler-embeddable/2.2.21/kotlin-scripting-compiler-embeddable-2.2.21.pom",
        "kotlin-scripting-compiler-embeddable-2.2.21.pom"
    ),

    # --- Kotlin 2.0.0 Plugin ---
    (
        "org.jetbrains.kotlin",
        "kotlin-gradle-plugin",
        "2.0.0",
        "https://repo.maven.apache.org/maven2/org/jetbrains/kotlin/kotlin-gradle-plugin/2.0.0/kotlin-gradle-plugin-2.0.0-gradle85.jar",
        "kotlin-gradle-plugin-2.0.0-gradle85.jar"
    ),
    (
        "org.jetbrains.kotlin",
        "kotlin-gradle-plugin",
        "2.0.0",
        "https://repo.maven.apache.org/maven2/org/jetbrains/kotlin/kotlin-gradle-plugin/2.0.0/kotlin-gradle-plugin-2.0.0.pom",
        "kotlin-gradle-plugin-2.0.0.pom"
    ),

    # --- Kotlin Reflect & Intellij Deps ---
    (
        "org.jetbrains.kotlin",
        "kotlin-reflect",
        "1.6.10",
        "https://repo.maven.apache.org/maven2/org/jetbrains/kotlin/kotlin-reflect/1.6.10/kotlin-reflect-1.6.10.jar",
        "kotlin-reflect-1.6.10.jar"
    ),
    (
        "org.jetbrains.kotlin",
        "kotlin-reflect",
        "1.6.10",
        "https://repo.maven.apache.org/maven2/org/jetbrains/kotlin/kotlin-reflect/1.6.10/kotlin-reflect-1.6.10.pom",
        "kotlin-reflect-1.6.10.pom"
    ),
    (
        "org.jetbrains.intellij.deps",
        "trove4j",
        "1.0.20200330",
        "https://repo.maven.apache.org/maven2/org/jetbrains/intellij/deps/trove4j/1.0.20200330/trove4j-1.0.20200330.jar",
        "trove4j-1.0.20200330.jar"
    ),
    (
        "org.jetbrains.intellij.deps",
        "trove4j",
        "1.0.20200330",
        "https://repo.maven.apache.org/maven2/org/jetbrains/intellij/deps/trove4j/1.0.20200330/trove4j-1.0.20200330.pom",
        "trove4j-1.0.20200330.pom"
    ),

    # --- Android Gradle Plugin 8.11.1 ---
    (
        "com.android.tools.build",
        "gradle",
        "8.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/gradle/8.11.1/gradle-8.11.1.jar",
        "gradle-8.11.1.jar"
    ),
    (
        "com.android.tools.build",
        "gradle",
        "8.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/gradle/8.11.1/gradle-8.11.1.pom",
        "gradle-8.11.1.pom"
    ),
    (
        "com.android.tools.build",
        "builder",
        "8.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/builder/8.11.1/builder-8.11.1.jar",
        "builder-8.11.1.jar"
    ),
    (
        "com.android.tools.build",
        "builder",
        "8.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/builder/8.11.1/builder-8.11.1.pom",
        "builder-8.11.1.pom"
    ),
    (
        "com.android.tools.build",
        "builder-model",
        "8.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/builder-model/8.11.1/builder-model-8.11.1.jar",
        "builder-model-8.11.1.jar"
    ),
    (
        "com.android.tools.build",
        "builder-model",
        "8.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/builder-model/8.11.1/builder-model-8.11.1.pom",
        "builder-model-8.11.1.pom"
    ),
    (
        "com.android.tools.build",
        "builder-test-api",
        "8.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/builder-test-api/8.11.1/builder-test-api-8.11.1.jar",
        "builder-test-api-8.11.1.jar"
    ),
    (
        "com.android.tools.build",
        "builder-test-api",
        "8.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/builder-test-api/8.11.1/builder-test-api-8.11.1.pom",
        "builder-test-api-8.11.1.pom"
    ),
    (
        "com.android.tools.build",
        "manifest-merger",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/manifest-merger/31.11.1/manifest-merger-31.11.1.jar",
        "manifest-merger-31.11.1.jar"
    ),
    (
        "com.android.tools.build",
        "manifest-merger",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/manifest-merger/31.11.1/manifest-merger-31.11.1.pom",
        "manifest-merger-31.11.1.pom"
    ),

    # --- Bundletool 1.18.1 (Exact AGP 8.11.1 version) ---
    (
        "com.android.tools.build",
        "bundletool",
        "1.18.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/bundletool/1.18.1/bundletool-1.18.1.jar",
        "bundletool-1.18.1.jar"
    ),
    (
        "com.android.tools.build",
        "bundletool",
        "1.18.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/bundletool/1.18.1/bundletool-1.18.1.pom",
        "bundletool-1.18.1.pom"
    ),

    # --- AAPT2 Proto 8.11.1-12782657 ---
    (
        "com.android.tools.build",
        "aapt2-proto",
        "8.11.1-12782657",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/aapt2-proto/8.11.1-12782657/aapt2-proto-8.11.1-12782657.jar",
        "aapt2-proto-8.11.1-12782657.jar"
    ),
    (
        "com.android.tools.build",
        "aapt2-proto",
        "8.11.1-12782657",
        "https://dl.google.com/dl/android/maven2/com/android/tools/build/aapt2-proto/8.11.1-12782657/aapt2-proto-8.11.1-12782657.pom",
        "aapt2-proto-8.11.1-12782657.pom"
    ),

    # --- Common Android Tools ---
    (
        "com.android.tools",
        "common",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/common/31.11.1/common-31.11.1.jar",
        "common-31.11.1.jar"
    ),
    (
        "com.android.tools",
        "common",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/common/31.11.1/common-31.11.1.pom",
        "common-31.11.1.pom"
    ),
    (
        "com.android.tools",
        "sdk-common",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/sdk-common/31.11.1/sdk-common-31.11.1.jar",
        "sdk-common-31.11.1.jar"
    ),
    (
        "com.android.tools",
        "sdk-common",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/sdk-common/31.11.1/sdk-common-31.11.1.pom",
        "sdk-common-31.11.1.pom"
    ),
    (
        "com.android.tools",
        "sdklib",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/sdklib/31.11.1/sdklib-31.11.1.jar",
        "sdklib-31.11.1.jar"
    ),
    (
        "com.android.tools",
        "sdklib",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/sdklib/31.11.1/sdklib-31.11.1.pom",
        "sdklib-31.11.1.pom"
    ),
    (
        "com.android.tools.layoutlib",
        "layoutlib-api",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/layoutlib/layoutlib-api/31.11.1/layoutlib-api-31.11.1.jar",
        "layoutlib-api-31.11.1.jar"
    ),
    (
        "com.android.tools.layoutlib",
        "layoutlib-api",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/layoutlib/layoutlib-api/31.11.1/layoutlib-api-31.11.1.pom",
        "layoutlib-api-31.11.1.pom"
    ),

    # --- Analytics Library ---
    (
        "com.android.tools.analytics-library",
        "protos",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/analytics-library/protos/31.11.1/protos-31.11.1.jar",
        "protos-31.11.1.jar"
    ),
    (
        "com.android.tools.analytics-library",
        "protos",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/analytics-library/protos/31.11.1/protos-31.11.1.pom",
        "protos-31.11.1.pom"
    ),
    (
        "com.android.tools.analytics-library",
        "shared",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/analytics-library/shared/31.11.1/shared-31.11.1.jar",
        "shared-31.11.1.jar"
    ),
    (
        "com.android.tools.analytics-library",
        "shared",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/analytics-library/shared/31.11.1/shared-31.11.1.pom",
        "shared-31.11.1.pom"
    ),
    (
        "com.android.tools.analytics-library",
        "tracker",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/analytics-library/tracker/31.11.1/tracker-31.11.1.jar",
        "tracker-31.11.1.jar"
    ),
    (
        "com.android.tools.analytics-library",
        "tracker",
        "31.11.1",
        "https://dl.google.com/dl/android/maven2/com/android/tools/analytics-library/tracker/31.11.1/tracker-31.11.1.pom",
        "tracker-31.11.1.pom"
    ),

    # --- Proto Google Common Protos 2.48.0 ---
    (
        "com.google.api.grpc",
        "proto-google-common-protos",
        "2.48.0",
        "https://repo.maven.apache.org/maven2/com/google/api/grpc/proto-google-common-protos/2.48.0/proto-google-common-protos-2.48.0.jar",
        "proto-google-common-protos-2.48.0.jar"
    ),
    (
        "com.google.api.grpc",
        "proto-google-common-protos",
        "2.48.0",
        "https://repo.maven.apache.org/maven2/com/google/api/grpc/proto-google-common-protos/2.48.0/proto-google-common-protos-2.48.0.pom",
        "proto-google-common-protos-2.48.0.pom"
    ),

    # --- Netty 4.1.110.Final Stack ---
    (
        "io.netty",
        "netty-codec-http2",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-codec-http2/4.1.110.Final/netty-codec-http2-4.1.110.Final.jar",
        "netty-codec-http2-4.1.110.Final.jar"
    ),
    (
        "io.netty",
        "netty-codec-http2",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-codec-http2/4.1.110.Final/netty-codec-http2-4.1.110.Final.pom",
        "netty-codec-http2-4.1.110.Final.pom"
    ),
    (
        "io.netty",
        "netty-codec-http",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-codec-http/4.1.110.Final/netty-codec-http-4.1.110.Final.jar",
        "netty-codec-http-4.1.110.Final.jar"
    ),
    (
        "io.netty",
        "netty-codec-http",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-codec-http/4.1.110.Final/netty-codec-http-4.1.110.Final.pom",
        "netty-codec-http-4.1.110.Final.pom"
    ),
    (
        "io.netty",
        "netty-handler",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-handler/4.1.110.Final/netty-handler-4.1.110.Final.jar",
        "netty-handler-4.1.110.Final.jar"
    ),
    (
        "io.netty",
        "netty-handler",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-handler/4.1.110.Final/netty-handler-4.1.110.Final.pom",
        "netty-handler-4.1.110.Final.pom"
    ),
    (
        "io.netty",
        "netty-codec",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-codec/4.1.110.Final/netty-codec-4.1.110.Final.jar",
        "netty-codec-4.1.110.Final.jar"
    ),
    (
        "io.netty",
        "netty-codec",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-codec/4.1.110.Final/netty-codec-4.1.110.Final.pom",
        "netty-codec-4.1.110.Final.pom"
    ),
    (
        "io.netty",
        "netty-transport",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-transport/4.1.110.Final/netty-transport-4.1.110.Final.jar",
        "netty-transport-4.1.110.Final.jar"
    ),
    (
        "io.netty",
        "netty-transport",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-transport/4.1.110.Final/netty-transport-4.1.110.Final.pom",
        "netty-transport-4.1.110.Final.pom"
    ),
    (
        "io.netty",
        "netty-buffer",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-buffer/4.1.110.Final/netty-buffer-4.1.110.Final.jar",
        "netty-buffer-4.1.110.Final.jar"
    ),
    (
        "io.netty",
        "netty-buffer",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-buffer/4.1.110.Final/netty-buffer-4.1.110.Final.pom",
        "netty-buffer-4.1.110.Final.pom"
    ),
    (
        "io.netty",
        "netty-common",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-common/4.1.110.Final/netty-common-4.1.110.Final.jar",
        "netty-common-4.1.110.Final.jar"
    ),
    (
        "io.netty",
        "netty-common",
        "4.1.110.Final",
        "https://repo.maven.apache.org/maven2/io/netty/netty-common/4.1.110.Final/netty-common-4.1.110.Final.pom",
        "netty-common-4.1.110.Final.pom"
    ),

    # --- Security & Native Dependencies ---
    (
        "org.bouncycastle",
        "bcprov-jdk18on",
        "1.79",
        "https://repo.maven.apache.org/maven2/org/bouncycastle/bcprov-jdk18on/1.79/bcprov-jdk18on-1.79.jar",
        "bcprov-jdk18on-1.79.jar"
    ),
    (
        "org.bouncycastle",
        "bcprov-jdk18on",
        "1.79",
        "https://repo.maven.apache.org/maven2/org/bouncycastle/bcprov-jdk18on/1.79/bcprov-jdk18on-1.79.pom",
        "bcprov-jdk18on-1.79.pom"
    ),
    (
        "org.bouncycastle",
        "bcpkix-jdk18on",
        "1.79",
        "https://repo.maven.apache.org/maven2/org/bouncycastle/bcpkix-jdk18on/1.79/bcpkix-jdk18on-1.79.jar",
        "bcpkix-jdk18on-1.79.jar"
    ),
    (
        "org.bouncycastle",
        "bcpkix-jdk18on",
        "1.79",
        "https://repo.maven.apache.org/maven2/org/bouncycastle/bcpkix-jdk18on/1.79/bcpkix-jdk18on-1.79.pom",
        "bcpkix-jdk18on-1.79.pom"
    ),
    (
        "net.java.dev.jna",
        "jna-platform",
        "5.6.0",
        "https://repo.maven.apache.org/maven2/net/java/dev/jna/jna-platform/5.6.0/jna-platform-5.6.0.jar",
        "jna-platform-5.6.0.jar"
    ),
    (
        "net.java.dev.jna",
        "jna-platform",
        "5.6.0",
        "https://repo.maven.apache.org/maven2/net/java/dev/jna/jna-platform/5.6.0/jna-platform-5.6.0.pom",
        "jna-platform-5.6.0.pom"
    ),
    (
        "net.java.dev.jna",
        "jna",
        "5.6.0",
        "https://repo.maven.apache.org/maven2/net/java/dev/jna/jna/5.6.0/jna-5.6.0.jar",
        "jna-5.6.0.jar"
    ),
    (
        "net.java.dev.jna",
        "jna",
        "5.6.0",
        "https://repo.maven.apache.org/maven2/net/java/dev/jna/jna/5.6.0/jna-5.6.0.pom",
        "jna-5.6.0.pom"
    ),

    # --- Flutter Android Engine Artifacts ---
    (
        "io.flutter",
        "flutter_embedding_release",
        "1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8",
        "https://storage.googleapis.com/download.flutter.io/io/flutter/flutter_embedding_release/1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8/flutter_embedding_release-1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8.jar",
        "flutter_embedding_release-1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8.jar"
    ),
    (
        "io.flutter",
        "flutter_embedding_release",
        "1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8",
        "https://storage.googleapis.com/download.flutter.io/io/flutter/flutter_embedding_release/1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8/flutter_embedding_release-1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8.pom",
        "flutter_embedding_release-1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8.pom"
    ),
    (
        "io.flutter",
        "arm64_v8a_release",
        "1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8",
        "https://storage.googleapis.com/download.flutter.io/io/flutter/arm64_v8a_release/1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8/arm64_v8a_release-1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8.jar",
        "arm64_v8a_release-1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8.jar"
    ),
    (
        "io.flutter",
        "arm64_v8a_release",
        "1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8",
        "https://storage.googleapis.com/download.flutter.io/io/flutter/arm64_v8a_release/1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8/arm64_v8a_release-1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8.pom",
        "arm64_v8a_release-1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8.pom"
    ),
    (
        "io.flutter",
        "armeabi_v7a_release",
        "1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8",
        "https://storage.googleapis.com/download.flutter.io/io/flutter/armeabi_v7a_release/1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8/armeabi_v7a_release-1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8.jar",
        "armeabi_v7a_release-1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8.jar"
    ),
    (
        "io.flutter",
        "armeabi_v7a_release",
        "1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8",
        "https://storage.googleapis.com/download.flutter.io/io/flutter/armeabi_v7a_release/1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8/armeabi_v7a_release-1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8.pom",
        "armeabi_v7a_release-1.0.0-cf636b1dfb818dd6a3ff16e390e93b1a036969c8.pom"
    ),

    # --- AndroidX Concurrent Futures (Fix for CameraX CallbackToFutureAdapter) ---
    (
        "androidx.concurrent",
        "concurrent-futures",
        "1.2.0",
        "https://dl.google.com/dl/android/maven2/androidx/concurrent/concurrent-futures/1.2.0/concurrent-futures-1.2.0.jar",
        "concurrent-futures-1.2.0.jar"
    ),
    (
        "androidx.concurrent",
        "concurrent-futures",
        "1.2.0",
        "https://dl.google.com/dl/android/maven2/androidx/concurrent/concurrent-futures/1.2.0/concurrent-futures-1.2.0.pom",
        "concurrent-futures-1.2.0.pom"
    ),
    (
        "androidx.concurrent",
        "concurrent-futures-ktx",
        "1.2.0",
        "https://dl.google.com/dl/android/maven2/androidx/concurrent/concurrent-futures-ktx/1.2.0/concurrent-futures-ktx-1.2.0.jar",
        "concurrent-futures-ktx-1.2.0.jar"
    ),
    (
        "androidx.concurrent",
        "concurrent-futures-ktx",
        "1.2.0",
        "https://dl.google.com/dl/android/maven2/androidx/concurrent/concurrent-futures-ktx/1.2.0/concurrent-futures-ktx-1.2.0.pom",
        "concurrent-futures-ktx-1.2.0.pom"
    )
]

def download_with_auto_resume(url, fname):
    tmp_path = os.path.join(temp_dir, fname)
    
    total_size = 0
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=15) as resp:
            total_size = int(resp.headers.get('Content-Length', 0))
    except Exception:
        pass

    for attempt in range(30):
        downloaded = os.path.getsize(tmp_path) if os.path.exists(tmp_path) else 0
        if total_size > 0 and downloaded >= total_size:
            break

        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            if downloaded > 0:
                req.add_header('Range', f'bytes={downloaded}-')

            with urllib.request.urlopen(req, timeout=15) as resp:
                is_partial = (resp.code == 206)
                if downloaded > 0 and not is_partial:
                    # Server sent full response from byte 0, reset mode
                    mode = 'wb'
                    downloaded = 0
                else:
                    mode = 'ab' if downloaded > 0 else 'wb'

                if not total_size:
                    try:
                        clen = int(resp.headers.get('Content-Length', 0))
                        total_size = (downloaded + clen) if is_partial else clen
                    except Exception:
                        pass

                with open(tmp_path, mode) as out:
                    while True:
                        buf = resp.read(512 * 1024)
                        if not buf:
                            break
                        out.write(buf)
                        out.flush()
                        downloaded += len(buf)
                        if total_size:
                            pct = downloaded * 100 / total_size
                            print(f"  Downloading {fname}: {downloaded//1024} KB / {total_size//1024} KB ({pct:.1f}%)", end='\r')
            print()
            break
        except Exception as e:
            print(f"\n  [Packet retry: {e}. Resuming chunk in 1s...]")
            time.sleep(1)

    return tmp_path

for group, name, version, url, fname in artifacts:
    group_dir = os.path.join(cache_base, group, name, version)
    os.makedirs(group_dir, exist_ok=True)

    already_cached = False
    if os.path.exists(group_dir):
        for sub in os.listdir(group_dir):
            check_path = os.path.join(group_dir, sub, fname)
            if os.path.exists(check_path) and os.path.getsize(check_path) > 10:
                print(f"[OK] {fname} is already cached ({os.path.getsize(check_path)//1024} KB)")
                already_cached = True
                break

    if already_cached:
        continue

    print(f"Auto-resuming download for {fname}...")
    dl_path = download_with_auto_resume(url, fname)

    if os.path.exists(dl_path) and os.path.getsize(dl_path) > 0:
        with open(dl_path, 'rb') as f:
            content = f.read()
        sha1 = hashlib.sha1(content).hexdigest()
        target_dir = os.path.join(group_dir, sha1)
        os.makedirs(target_dir, exist_ok=True)
        final_file = os.path.join(target_dir, fname)
        shutil.copyfile(dl_path, final_file)
        print(f"[SUCCESS] {fname} ({len(content)//1024} KB) cached in Gradle! SHA1: {sha1}")

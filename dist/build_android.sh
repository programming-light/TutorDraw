#!/bin/bash
# Build script for Android using Buildozer
echo "Setting up Android build environment..."

# Install buildozer if not already installed
pip install buildozer cython

# Initialize buildozer if not already done
if [ ! -f buildozer.spec ]; then
    buildozer init
fi

# Modify buildozer.spec for our app
cat > buildozer.spec << EOF
[app]
title = TutorDraw
package.name = tutordraw
package.domain = org.tutordraw

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt

version = 1.0
requirements = python3,pyjnius,pyside6

[buildozer]
log_level = 2

[app]
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,CAMERA
EOF

# Build for Android
buildozer android debug

echo "Android build completed!"

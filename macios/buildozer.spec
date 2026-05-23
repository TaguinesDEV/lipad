[app]

# (str) Title of your application
title = Floppy Bird

# (str) Package name
package.name = floppybird

# (str) Package domain (needed for android/ios packaging)
package.domain = org.macios

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,wav

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8v, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (str) The display name of the application on iOS
ios.display_name = Floppy Bird

# (str) Name of the certificate to use for signing the debug version
# ios.codesign.debug = "iPhone Developer: <firstname> <lastname> (<identifier>)"

# (list) iOS frameworks to include
ios.frameworks = CoreGraphics, QuartzCore, UIKit

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
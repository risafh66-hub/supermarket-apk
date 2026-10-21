[app]
title = سوبرماركت
package.name = supermarket
package.domain = com.supermarket.app
source.dir = .
source.include_exts = py
version = 2.0
requirements = python3,kivy==2.3.0,kivymd==1.1.1
orientation = portrait
[app:android]
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.accept_sdk_license_agreement = True
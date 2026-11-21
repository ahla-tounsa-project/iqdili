# Android release signing — Ahla Tounsa

## Release identity
- App label: أحلى توانسة
- Application ID: `tn.ahlatounsa.app`
- Release version: `1.1` (`versionCode 2`)
- Website loaded by the Android app: `https://ahla-tounsa-project.github.io/iqdili/`

## Permanent signing key
Create one release keystore on a trusted device with Java `keytool`. Do not use an online key generator. Keep the original keystore and its passwords in two separate, secure backups; at least one backup should be offline and encrypted. Losing the keystore prevents signing compatible future updates.

Example command (run locally; never paste the resulting file or passwords into chat or a repository):

```bash
keytool -genkeypair -v -keystore ahla-tounsa-release.jks -alias ahla-tounsa -keyalg RSA -keysize 2048 -validity 10000
```

## GitHub Actions secrets
In repository Settings → Secrets and variables → Actions, create:

- `ANDROID_KEYSTORE_BASE64`: the keystore file encoded as one Base64 string.
- `RELEASE_STORE_PASSWORD`: keystore password.
- `RELEASE_KEY_ALIAS`: exact alias used when creating the key (example: `ahla-tounsa`).
- `RELEASE_KEY_PASSWORD`: private-key password.

Never commit the keystore, Base64 content, or passwords. Never send them in chat, issues, pull requests, or ordinary files.

## Build and publish
The workflow is deliberately manual. After this workflow has been merged into `main` and all four secrets have been configured:

1. Open Actions → Build signed Ahla Tounsa Android APK → Run workflow.
2. Keep **Publish the verified APK** unchecked for a build-only run. The verified APK and SHA-256 checksum are retained as a workflow artifact for 90 days.
3. Only when the artifact is reviewed and publication is intended, run again with **Publish the verified APK** checked. This updates the stable `android-latest` GitHub Release asset.

The workflow verifies ZIP integrity, application ID, version code/name, APK signature, and alignment before creating the artifact or publishing. It does not upload the keystore.

## Installing and updating
The previous public APK was a Debug build. Its signing identity differs from the permanent Release key, so Android will normally require uninstalling the old Debug app before installing this Release APK. Uninstalling may erase local app data; back up anything important first. Future updates must use the same permanent keystore and a higher versionCode each time.

A valid signature does not guarantee that Android or Google Play Protect will never show a warning for an app installed outside Google Play.

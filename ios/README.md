# Blockapp for iPhone

The iPhone version of Blockapp, written in SwiftUI. It blocks apps and websites with Apple's
Screen Time system, so it works even when Blockapp is closed.

It has the same three tabs as the Windows dashboard:

- **🎯 Focus:** tap 📱 Apps to pick apps (Apple's own picker), or tap website tiles like YouTube
  to block them in Safari. Pick 25m, 50m or 90m and press Start. Start stays grey until you've
  picked something. While focusing you see a countdown and a Stop early button (−10 points).
- **⏰ Schedule:** pick days and a time, and focus turns on by itself.
- **📈 Stats:** today's Focus Score and the last 7 days.

When you open a blocked app, you get a purple "Focus time 🎯" screen instead.

## What you need

- A Mac with Xcode 15 or newer
- A paid Apple Developer account (Family Controls only works with one)
- An iPhone on iOS 16 or newer. The simulator can't block apps.

## Run it on your iPhone

```bash
brew install xcodegen
cd ios
```

1. Open `project.yml` and set `BUNDLE_PREFIX` to something unique, like `com.yourname.blockapp`,
   and `DEVELOPMENT_TEAM` to your Team ID (Xcode › Settings › Accounts).
2. Run `xcodegen` to make `Blockapp.xcodeproj`, then open it.
3. Plug in your iPhone, choose it at the top of Xcode and press ▶︎. Xcode registers the App Group
   and the Family Controls capability for you.
4. On the phone, tap **Allow Screen Time**.

The Family Controls capability works for your own testing straight away. To publish on the
App Store, Apple has to approve it first: request the "Family Controls (Distribution)"
entitlement at https://developer.apple.com/contact/request/family-controls-distribution.

## How it fits together

| Folder | What it does |
| --- | --- |
| `Blockapp/` | The app's screens |
| `Shared/` | Settings, schedules and the Focus Score, shared with the extensions |
| `Monitor/` | Starts and ends blocking at the right times, even when the app is closed |
| `ShieldConfig/` | The "Focus time" screen shown over blocked apps |
| `ShieldAction/` | Counts taps on that screen for the Focus Score |

## Differences from Windows

- Apps are picked with Apple's picker, because iOS doesn't let apps see what else is installed.
- The Focus Score counts blocked opens and early stops. iOS keeps minutes-per-app private, so
  there's no "distracted time" part.
- iOS allows about 19 automatic day-slots in total (a schedule for every day uses one,
  weekdays uses five).
- The iPhone and Windows apps keep their own settings; they don't sync yet.

Every push that changes `ios/` is built on GitHub (see `.github/workflows/ios.yml`) to check it compiles.

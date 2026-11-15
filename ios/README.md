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

## Put it on your iPhone from Windows (TestFlight)

You don't need a Mac. GitHub builds and signs the app on one of its Macs and sends it to
TestFlight, Apple's app for installing test versions. Everything below is done in a web browser.

**1. Wait for Apple to approve your Developer account.** Apple emails you when it's done.

**2. Collect three things from Apple.**
- **Team ID:** https://developer.apple.com/account, under Membership details (10 letters and numbers).
- **API key:** https://appstoreconnect.apple.com/access/integrations/api, open Team Keys, press +,
  name it `GitHub` and pick **Admin** access. Download the `.p8` file (Apple only lets you
  download it once). Note the **Key ID** next to it and the **Issuer ID** above the list.

**3. Register your iPhone.** Xcode signs builds with a development profile first, and Apple only
makes one when at least one iPhone is registered. Connect the iPhone to your PC, open the
Apple Devices app (or iTunes) and click the serial number until it shows the UDID, then copy it.
Add it at https://developer.apple.com/account/resources/devices/add.

**4. Give GitHub the secrets.** At https://github.com/gaurijain21/blockapp/settings/secrets/actions
press New repository secret four times:

| Name | Value |
| --- | --- |
| `APPLE_TEAM_ID` | your Team ID |
| `ASC_KEY_ID` | the Key ID |
| `ASC_ISSUER_ID` | the Issuer ID |
| `ASC_KEY_P8` | open the `.p8` file in Notepad and paste all of it |

**5. Run the build once.** Open https://github.com/gaurijain21/blockapp/actions/workflows/ios-testflight.yml
and press Run workflow (this button appears once the iPhone pull request is merged). This first run
registers Blockapp's app IDs with Apple. It's expected to stop before uploading until step 6 is approved.

**6. Ask Apple for the Family Controls permission.** Apps that block other apps need Apple's
approval before they can go on TestFlight. Fill in
https://developer.apple.com/contact/request/family-controls-distribution once for each of these IDs:
`com.gaurijain21.blockapp`, `com.gaurijain21.blockapp.monitor`,
`com.gaurijain21.blockapp.shieldconfig` and `com.gaurijain21.blockapp.shieldaction`.
Apple usually answers in a few days to a few weeks.

**7. Create the app listing.** At https://appstoreconnect.apple.com/apps press + and New App.
Pick iOS, any free name (for example "Blockapp Focus"), bundle ID `com.gaurijain21.blockapp`, and SKU `blockapp`.

**8. Install it.** Once Apple approves step 6, run the build again. After 5 to 30 minutes it shows up
in App Store Connect under TestFlight. Add yourself under Internal Testing, install the TestFlight
app on your iPhone, and open Blockapp from there. Each later run sends a new version.

## Or, with a Mac

Install Xcode 15 or newer, then:

```bash
brew install xcodegen
cd ios
xcodegen
open Blockapp.xcodeproj
```

Set your team under Signing & Capabilities, plug in your iPhone and press ▶︎. Development builds
work right away, without waiting for the Family Controls approval. The simulator can't block apps.

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

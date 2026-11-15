import DeviceActivity
import Foundation

/// iOS calls this when a focus time starts or ends, even if Blockapp isn't open.
class MonitorExtension: DeviceActivityMonitor {
    override func intervalDidStart(for activity: DeviceActivityName) {
        super.intervalDidStart(for: activity)
        // A second later, so the edge of the window counts as "on".
        Blocker.sync(at: Date().addingTimeInterval(1))
    }

    override func intervalDidEnd(for activity: DeviceActivityName) {
        super.intervalDidEnd(for: activity)
        let shared = SharedStore.shared
        if activity == Scheduler.focusNow, let until = shared.focusUntil, until <= Date().addingTimeInterval(60) {
            shared.focusUntil = nil
        }
        Blocker.sync(at: Date().addingTimeInterval(1))
    }
}

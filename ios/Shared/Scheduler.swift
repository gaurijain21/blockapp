import Foundation
import DeviceActivity

/// Registers focus times with iOS, so blocking starts and stops even when the app is closed.
enum Scheduler {
    static let center = DeviceActivityCenter()
    static let focusNow = DeviceActivityName("focusNow")
    static let schedulePrefix = "sched-"
    /// iOS watches at most 20 activities per app; one is kept for Start.
    static let maxScheduleActivities = 19

    static func startFocus(until end: Date, from start: Date = Date()) throws {
        let parts: Set<Calendar.Component> = [.hour, .minute, .second]
        let cal = Calendar.current
        let schedule = DeviceActivitySchedule(
            intervalStart: cal.dateComponents(parts, from: start),
            intervalEnd: cal.dateComponents(parts, from: end),
            repeats: false)
        center.stopMonitoring([focusNow])
        try center.startMonitoring(focusNow, during: schedule)
    }

    static func stopFocus() {
        center.stopMonitoring([focusNow])
    }

    static func activityCount(_ schedules: [FocusSchedule]) -> Int {
        schedules.reduce(0) { $0 + (Set($1.days).count == 7 ? 1 : Set($1.days).count) }
    }

    static func sync(_ schedules: [FocusSchedule]) throws {
        let old = center.activities.filter { $0.rawValue.hasPrefix(schedulePrefix) }
        center.stopMonitoring(old)
        for s in schedules {
            for (name, schedule) in activities(for: s) {
                try center.startMonitoring(name, during: schedule)
            }
        }
    }

    static func activities(for s: FocusSchedule) -> [(DeviceActivityName, DeviceActivitySchedule)] {
        let (sh, sm) = (s.startMinutes / 60, s.startMinutes % 60)
        let (eh, em) = (s.endMinutes / 60, s.endMinutes % 60)
        let base = schedulePrefix + s.id.uuidString
        if Set(s.days).count == 7 {
            return [(DeviceActivityName(base), DeviceActivitySchedule(
                intervalStart: DateComponents(hour: sh, minute: sm),
                intervalEnd: DateComponents(hour: eh, minute: em),
                repeats: true))]
        }
        return Set(s.days).sorted().map { day in
            let endDay = s.endMinutes > s.startMinutes ? day : day % 7 + 1
            return (DeviceActivityName("\(base)-\(day)"), DeviceActivitySchedule(
                intervalStart: DateComponents(hour: sh, minute: sm, weekday: day),
                intervalEnd: DateComponents(hour: eh, minute: em, weekday: endDay),
                repeats: true))
        }
    }
}

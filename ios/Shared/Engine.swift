import Foundation

/// Works out whether focus is on, the same way the Windows app does.
enum Engine {
    static var calendar = Calendar.current

    /// If this schedule is on at `now`, when it ends. A window that crosses midnight
    /// belongs to the day it starts.
    static func activeEnd(of s: FocusSchedule, at now: Date) -> Date? {
        let today = calendar.startOfDay(for: now)
        for offset in [0, -1] {
            guard let day = calendar.date(byAdding: .day, value: offset, to: today),
                  s.days.contains(calendar.component(.weekday, from: day)),
                  let (start, end) = window(of: s, on: day) else { continue }
            if start <= now && now < end { return end }
        }
        return nil
    }

    static func window(of s: FocusSchedule, on day: Date) -> (Date, Date)? {
        guard let start = calendar.date(byAdding: .minute, value: s.startMinutes, to: day),
              var end = calendar.date(byAdding: .minute, value: s.endMinutes, to: day) else { return nil }
        if s.endMinutes <= s.startMinutes { end = calendar.date(byAdding: .day, value: 1, to: end) ?? end }
        return (start, end)
    }

    /// When the current focus session ends (automatic or started now), or nil if none is on.
    static func sessionEnd(at now: Date, store: SharedStore = .shared) -> Date? {
        var ends = store.schedules.compactMap { activeEnd(of: $0, at: now) }
        if let manual = store.focusUntil, now < manual { ends.append(manual) }
        return ends.max()
    }

    static func isSkipped(at now: Date, store: SharedStore = .shared) -> Bool {
        guard let skip = store.skipUntil else { return false }
        return now < skip
    }

    static func shouldBlock(at now: Date, store: SharedStore = .shared) -> Bool {
        sessionEnd(at: now, store: store) != nil && !isSkipped(at: now, store: store)
    }

    /// When the next automatic focus time starts, looking a week ahead.
    static func nextStart(after now: Date, schedules: [FocusSchedule]) -> Date? {
        let today = calendar.startOfDay(for: now)
        var best: Date?
        for s in schedules {
            for offset in 0..<8 {
                guard let day = calendar.date(byAdding: .day, value: offset, to: today),
                      s.days.contains(calendar.component(.weekday, from: day)),
                      let (start, _) = window(of: s, on: day), start > now else { continue }
                if best == nil || start < best! { best = start }
                break
            }
        }
        return best
    }

    // MARK: - Labels

    /// Monday first, the way people read a week.
    static let weekOrder = [2, 3, 4, 5, 6, 7, 1]

    static func daysLabel(_ days: [Int]) -> String {
        let set = Set(days)
        if set == [2, 3, 4, 5, 6] { return "Weekdays" }
        if set.count == 7 { return "Every day" }
        if set == [1, 7] { return "Weekends" }
        let symbols = calendar.weekdaySymbols
        if set.count == 1, let d = set.first { return symbols[d - 1] + "s" }
        let short = calendar.shortWeekdaySymbols
        return weekOrder.filter(set.contains).map { short[$0 - 1] }.joined(separator: ", ")
    }

    static func clock(_ minutes: Int) -> String {
        let date = calendar.date(byAdding: .minute, value: minutes, to: calendar.startOfDay(for: Date())) ?? Date()
        return date.formatted(date: .omitted, time: .shortened)
    }

    static func describe(_ s: FocusSchedule) -> String {
        "\(daysLabel(s.days)), \(clock(s.startMinutes)) to \(clock(s.endMinutes))"
    }
}

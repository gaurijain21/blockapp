import Foundation

/// The Focus Score, from 0 to 100, as in the Windows app. On iPhone there's no
/// distracted-time part: Apple keeps per-app minutes private to the Screen Time report.
struct DayStats: Identifiable {
    var day: Date
    var attempts = 0
    var skips = 0
    var id: Date { day }

    static let attemptPoints = 5, attemptCap = 40
    static let skipPoints = 10, skipCap = 20

    var attemptPenalty: Int { min(Self.attemptCap, attempts * Self.attemptPoints) }
    var skipPenalty: Int { min(Self.skipCap, skips * Self.skipPoints) }
    var score: Int { max(0, 100 - attemptPenalty - skipPenalty) }

    static func label(_ score: Int) -> String {
        switch score {
        case 90...: return "Locked in"
        case 70...: return "Mostly focused"
        case 50...: return "Easily distracted"
        default: return "Very distracted"
        }
    }

    /// The last `count` days, oldest first.
    static func lastDays(_ count: Int, events: [FocusEvent], now: Date = Date(),
                         calendar: Calendar = .current) -> [DayStats] {
        let today = calendar.startOfDay(for: now)
        var stats = (0..<count).reversed().compactMap { offset in
            calendar.date(byAdding: .day, value: -offset, to: today).map { DayStats(day: $0) }
        }
        for event in events {
            let day = calendar.startOfDay(for: event.time)
            guard let i = stats.firstIndex(where: { $0.day == day }) else { continue }
            switch event.kind {
            case .blocked: stats[i].attempts += 1
            case .skip: stats[i].skips += 1
            case .focusNow: break
            }
        }
        return stats
    }
}

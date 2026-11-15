import Foundation
import FamilyControls
import SwiftUI

@MainActor
final class AppModel: ObservableObject {
    private let shared = SharedStore.shared

    @Published var authorized = false
    @Published var selection = FamilyActivitySelection()
    @Published var sites: [String] = []
    @Published var schedules: [FocusSchedule] = []
    @Published var sessionEnd: Date?
    @Published var sessionStart: Date?
    @Published var events: [FocusEvent] = []
    @Published var error: String?

    private var timer: Timer?

    init() {
        refresh()
        timer = Timer.scheduledTimer(withTimeInterval: 5, repeats: true) { [weak self] _ in
            Task { @MainActor in self?.tick() }
        }
    }

    // MARK: - State

    var pickedCount: Int {
        selection.applicationTokens.count + selection.categoryTokens.count
            + selection.webDomainTokens.count + sites.count
    }

    var appCount: Int {
        selection.applicationTokens.count + selection.categoryTokens.count + selection.webDomainTokens.count
    }

    var isFocusing: Bool { sessionEnd != nil }

    var today: DayStats { DayStats.lastDays(1, events: events)[0] }
    var week: [DayStats] { DayStats.lastDays(7, events: events) }

    func refresh() {
        authorized = AuthorizationCenter.shared.authorizationStatus == .approved
        selection = shared.selection
        sites = shared.sites
        schedules = shared.schedules
        events = shared.events
        updateSession()
    }

    private func updateSession(now: Date = Date()) {
        if let until = shared.focusUntil, until <= now { shared.focusUntil = nil }
        let end = Engine.isSkipped(at: now) ? nil : Engine.sessionEnd(at: now)
        if end != sessionEnd {
            sessionStart = end == nil ? nil : (sessionStart ?? now)
            sessionEnd = end
        }
        if authorized { Blocker.sync(at: now) }
    }

    private func tick() {
        let wasFocusing = isFocusing
        updateSession()
        if wasFocusing != isFocusing { events = shared.events }
    }

    func requestAuthorization() async {
        do {
            try await AuthorizationCenter.shared.requestAuthorization(for: .individual)
            error = nil
        } catch {
            self.error = "Screen Time permission is needed to block apps."
        }
        refresh()
    }

    // MARK: - Picks

    func setSelection(_ new: FamilyActivitySelection) {
        selection = new
        shared.selection = new
        if isFocusing { Blocker.apply() }
    }

    func toggleSite(_ id: String) {
        if let i = sites.firstIndex(of: id) { sites.remove(at: i) } else { sites.append(id) }
        shared.sites = sites
        if isFocusing { Blocker.apply() }
    }

    // MARK: - Focus

    func startFocus(minutes: Int) {
        let now = Date()
        let end = now.addingTimeInterval(TimeInterval(minutes * 60))
        shared.focusUntil = end
        shared.skipUntil = nil
        shared.log(.focusNow, at: now)
        sessionStart = now
        Blocker.apply()
        do {
            try Scheduler.startFocus(until: end, from: now)
        } catch {
            // Blocking is on already; the app ends it when opened if iOS can't.
            self.error = "Focus is on, but iOS may not end it on its own. Open Blockapp after."
        }
        refresh()
    }

    func stopEarly() {
        let now = Date()
        guard let end = Engine.sessionEnd(at: now) else { return }
        shared.focusUntil = nil
        shared.skipUntil = end
        shared.log(.skip, at: now)
        Scheduler.stopFocus()
        Blocker.clear()
        sessionStart = nil
        refresh()
    }

    // MARK: - Schedules

    func addSchedule(days: Set<Int>, start: Date, end: Date) {
        let cal = Calendar.current
        func minutes(_ d: Date) -> Int { cal.component(.hour, from: d) * 60 + cal.component(.minute, from: d) }
        let s = FocusSchedule(days: Engine.weekOrder.filter(days.contains),
                              startMinutes: minutes(start), endMinutes: minutes(end))
        guard !s.days.isEmpty else { error = "Pick at least one day."; return }
        guard s.startMinutes != s.endMinutes else { error = "Start and end can't be the same."; return }
        let length = (s.endMinutes - s.startMinutes + 24 * 60) % (24 * 60)
        guard length >= 15 else { error = "Make it at least 15 minutes."; return }
        let all = schedules + [s]
        guard Scheduler.activityCount(all) <= Scheduler.maxScheduleActivities else {
            error = "That's too many for iOS. Remove one first."
            return
        }
        save(all)
    }

    func removeSchedule(_ s: FocusSchedule) {
        save(schedules.filter { $0.id != s.id })
    }

    private func save(_ new: [FocusSchedule]) {
        shared.schedules = new
        schedules = new
        error = nil
        do {
            try Scheduler.sync(new)
        } catch {
            self.error = "iOS couldn't set that up: \(error.localizedDescription)"
        }
        updateSession()
    }
}

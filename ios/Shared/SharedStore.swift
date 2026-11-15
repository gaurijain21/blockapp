import Foundation
import FamilyControls

/// Settings shared between the app and its Screen Time extensions, through an App Group.
final class SharedStore {
    static let shared = SharedStore()

    static let groupID: String =
        Bundle.main.object(forInfoDictionaryKey: "AppGroup") as? String ?? "group.com.example.blockapp"

    private let defaults: UserDefaults

    init(defaults: UserDefaults? = nil) {
        self.defaults = defaults ?? UserDefaults(suiteName: SharedStore.groupID) ?? .standard
    }

    private func load<T: Decodable>(_ key: String, as type: T.Type) -> T? {
        guard let data = defaults.data(forKey: key) else { return nil }
        return try? JSONDecoder().decode(T.self, from: data)
    }

    private func save<T: Encodable>(_ key: String, _ value: T?) {
        if let value, let data = try? JSONEncoder().encode(value) {
            defaults.set(data, forKey: key)
        } else {
            defaults.removeObject(forKey: key)
        }
    }

    /// Apps, categories and websites picked with Apple's picker.
    var selection: FamilyActivitySelection {
        get { load("selection", as: FamilyActivitySelection.self) ?? FamilyActivitySelection() }
        set { save("selection", newValue) }
    }

    /// One-tap websites (Catalog ids), blocked in Safari.
    var sites: [String] {
        get { load("sites", as: [String].self) ?? [] }
        set { save("sites", newValue) }
    }

    var siteDomains: [String] { sites.compactMap(Catalog.site).flatMap(\.domains) }

    var schedules: [FocusSchedule] {
        get { load("schedules", as: [FocusSchedule].self) ?? [] }
        set { save("schedules", newValue) }
    }

    /// End of a session started with Start.
    var focusUntil: Date? {
        get { load("focusUntil", as: Date.self) }
        set { save("focusUntil", newValue) }
    }

    /// Focus was stopped early; stay unblocked until this time.
    var skipUntil: Date? {
        get { load("skipUntil", as: Date.self) }
        set { save("skipUntil", newValue) }
    }

    var events: [FocusEvent] {
        get { load("events", as: [FocusEvent].self) ?? [] }
        set { save("events", newValue) }
    }

    func log(_ kind: FocusEvent.Kind, at time: Date = Date()) {
        // Keep about two weeks, which is all the Stats tab shows.
        let cutoff = time.addingTimeInterval(-14 * 24 * 3600)
        events = events.filter { $0.time > cutoff } + [FocusEvent(time: time, kind: kind)]
    }

    var pickedCount: Int {
        let s = selection
        return s.applicationTokens.count + s.categoryTokens.count + s.webDomainTokens.count + sites.count
    }
}

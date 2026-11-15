import Foundation
import FamilyControls
import ManagedSettings

/// Turns Screen Time shields on and off.
enum Blocker {
    static let store = ManagedSettingsStore()

    static func apply(_ shared: SharedStore = .shared) {
        let picked = shared.selection
        store.shield.applications = picked.applicationTokens.isEmpty ? nil : picked.applicationTokens
        store.shield.applicationCategories = picked.categoryTokens.isEmpty ? nil : .specific(picked.categoryTokens)
        store.shield.webDomains = picked.webDomainTokens.isEmpty ? nil : picked.webDomainTokens
        let domains = Set(shared.siteDomains.map { WebDomain(domain: $0) })
        store.webContent.blockedByFilter = domains.isEmpty ? nil : .specific(domains)
    }

    static func clear() {
        store.clearAllSettings()
    }

    /// Block or unblock to match the schedules and any running session.
    static func sync(at now: Date = Date(), _ shared: SharedStore = .shared) {
        if Engine.shouldBlock(at: now, store: shared) { apply(shared) } else { clear() }
    }
}

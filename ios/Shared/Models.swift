import Foundation

/// A recurring automatic focus time, like weekdays 9:00 to 12:00.
struct FocusSchedule: Codable, Identifiable, Equatable {
    var id = UUID()
    /// Calendar weekdays: 1 = Sunday, 2 = Monday ... 7 = Saturday.
    var days: [Int]
    /// Minutes since midnight. An end before the start runs past midnight.
    var startMinutes: Int
    var endMinutes: Int
}

/// Something that happened, for the Focus Score.
struct FocusEvent: Codable, Equatable {
    enum Kind: String, Codable { case blocked, skip, focusNow }
    var time: Date
    var kind: Kind
}

/// A website that can be blocked in Safari with one tap.
struct Site: Identifiable, Equatable {
    let id: String
    let name: String
    let emoji: String
    let domains: [String]
}

enum Catalog {
    static let sites: [Site] = [
        Site(id: "youtube", name: "YouTube", emoji: "📺", domains: ["youtube.com", "youtu.be"]),
        Site(id: "instagram", name: "Instagram", emoji: "📸", domains: ["instagram.com"]),
        Site(id: "tiktok", name: "TikTok", emoji: "🎵", domains: ["tiktok.com"]),
        Site(id: "netflix", name: "Netflix", emoji: "🍿", domains: ["netflix.com"]),
        Site(id: "reddit", name: "Reddit", emoji: "👽", domains: ["reddit.com"]),
        Site(id: "twitch", name: "Twitch", emoji: "🟣", domains: ["twitch.tv"]),
        Site(id: "facebook", name: "Facebook", emoji: "👍", domains: ["facebook.com"]),
        Site(id: "x", name: "X", emoji: "✖️", domains: ["x.com", "twitter.com"]),
        Site(id: "pinterest", name: "Pinterest", emoji: "📌", domains: ["pinterest.com"]),
        Site(id: "discord", name: "Discord", emoji: "💬", domains: ["discord.com"]),
        Site(id: "roblox", name: "Roblox", emoji: "🧱", domains: ["roblox.com"]),
    ]

    static func site(_ id: String) -> Site? { sites.first { $0.id == id } }
}

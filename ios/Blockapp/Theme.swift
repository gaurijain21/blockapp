import SwiftUI
import UIKit

/// The same purple-to-pink look as the Windows dashboard.
enum Theme {
    static let bg = Color(light: 0xf6f4ff, dark: 0x0e0c17)
    static let card = Color(light: 0xffffff, dark: 0x181527)
    static let ink = Color(light: 0x1b1530, dark: 0xf3f0ff)
    static let muted = Color(light: 0x7a7491, dark: 0x9b95b5)
    static let line = Color(light: 0xe8e4f7, dark: 0x2a2640)
    static let soft = Color(light: 0xf0edfc, dark: 0x221e35)
    static let a1 = Color(light: 0x6d4aff, dark: 0x8d74ff)
    static let a2 = Color(light: 0xff5c9a, dark: 0xff6fa8)
    static let good = Color(light: 0x12b76a, dark: 0x34d399)
    static let warn = Color(light: 0xf59e0b, dark: 0xfbbf24)
    static let bad = Color(light: 0xef4444, dark: 0xf87171)

    static let gradient = LinearGradient(colors: [a1, a2], startPoint: .topLeading, endPoint: .bottomTrailing)

    static func scoreColor(_ score: Int) -> Color {
        score >= 70 ? good : score >= 50 ? warn : bad
    }
}

extension Color {
    init(light: UInt32, dark: UInt32) {
        self.init(UIColor { traits in
            UIColor(hex: traits.userInterfaceStyle == .dark ? dark : light)
        })
    }
}

extension UIColor {
    convenience init(hex: UInt32) {
        self.init(red: CGFloat((hex >> 16) & 0xff) / 255,
                  green: CGFloat((hex >> 8) & 0xff) / 255,
                  blue: CGFloat(hex & 0xff) / 255, alpha: 1)
    }
}

struct CardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(18)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Theme.card, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).stroke(Theme.line))
            .shadow(color: Theme.a1.opacity(0.08), radius: 15, y: 8)
    }
}

extension View {
    func card() -> some View { modifier(CardStyle()) }
}

/// "① Pick distractions" style heading.
struct StepTitle: View {
    let number: Int
    let title: String
    var done = false

    var body: some View {
        HStack(spacing: 10) {
            Text("\(number)")
                .font(.system(size: 13, weight: .heavy, design: .rounded))
                .frame(width: 26, height: 26)
                .foregroundStyle(done ? Color.white : Theme.a1)
                .background {
                    if done { Circle().fill(Theme.gradient) } else { Circle().fill(Theme.soft) }
                }
            Text(title).font(.system(size: 17, weight: .heavy, design: .rounded))
        }
        .foregroundStyle(Theme.ink)
    }
}

struct GradientButtonStyle: ButtonStyle {
    @Environment(\.isEnabled) private var enabled

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 18, weight: .heavy, design: .rounded))
            .foregroundStyle(enabled ? Color.white : Theme.muted)
            .frame(maxWidth: .infinity, minHeight: 56)
            .background {
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .fill(enabled ? AnyShapeStyle(Theme.gradient) : AnyShapeStyle(Theme.soft))
            }
            .shadow(color: enabled ? Theme.a1.opacity(0.3) : .clear, radius: 12, y: 6)
            .scaleEffect(configuration.isPressed ? 0.97 : 1)
            .animation(.easeOut(duration: 0.12), value: configuration.isPressed)
    }
}

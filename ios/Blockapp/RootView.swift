import SwiftUI

enum Tab: String, CaseIterable {
    case focus = "🎯 Focus", schedule = "⏰ Schedule", stats = "📈 Stats"
}

struct RootView: View {
    @EnvironmentObject private var model: AppModel
    @AppStorage("theme") private var theme = "system"
    @Environment(\.colorScheme) private var scheme
    @State private var tab = Tab.focus

    var body: some View {
        ZStack {
            Theme.bg.ignoresSafeArea()
            ScrollView {
                VStack(spacing: 14) {
                    header
                    if model.authorized {
                        tabs
                        switch tab {
                        case .focus: FocusView()
                        case .schedule: ScheduleView()
                        case .stats: StatsView()
                        }
                    } else {
                        WelcomeView()
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
            }
        }
        .foregroundStyle(Theme.ink)
        .tint(Theme.a1)
    }

    private var header: some View {
        HStack {
            HStack(spacing: 8) {
                Text("⛔️")
                    .font(.system(size: 15))
                    .frame(width: 30, height: 30)
                    .background(Theme.gradient, in: RoundedRectangle(cornerRadius: 10, style: .continuous))
                Text("blockapp").font(.system(size: 22, weight: .heavy, design: .rounded))
            }
            Spacer()
            Text("🔥 \(model.today.score)")
                .font(.system(size: 14, weight: .bold, design: .rounded))
                .padding(.horizontal, 12).padding(.vertical, 6)
                .background(Theme.card, in: Capsule())
                .overlay(Capsule().stroke(Theme.line))
                .onTapGesture { tab = .stats }
                .accessibilityLabel("Focus Score \(model.today.score)")
            Button {
                theme = scheme == .dark ? "light" : "dark"
            } label: {
                Text(scheme == .dark ? "☀️" : "🌙")
                    .frame(width: 36, height: 36)
                    .background(Theme.card, in: Circle())
                    .overlay(Circle().stroke(Theme.line))
            }
            .accessibilityLabel("Switch light or dark mode")
        }
    }

    private var tabs: some View {
        HStack(spacing: 6) {
            ForEach(Tab.allCases, id: \.self) { t in
                Button {
                    withAnimation(.easeOut(duration: 0.15)) { tab = t }
                } label: {
                    HStack(spacing: 6) {
                        Text(t.rawValue)
                        if t == .schedule && !model.schedules.isEmpty {
                            Circle().fill(Theme.good).frame(width: 7, height: 7)
                        }
                    }
                    .font(.system(size: 15, weight: .bold, design: .rounded))
                    .lineLimit(1).minimumScaleFactor(0.8)
                    .foregroundStyle(tab == t ? Color.white : Theme.muted)
                    .frame(maxWidth: .infinity, minHeight: 42)
                    .background {
                        if tab == t {
                            RoundedRectangle(cornerRadius: 14, style: .continuous).fill(Theme.gradient)
                        }
                    }
                }
                .buttonStyle(.plain)
                .accessibilityAddTraits(tab == t ? .isSelected : [])
            }
        }
        .padding(5)
        .background(Theme.card, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(Theme.line))
    }
}

/// Shown once, to get Screen Time permission.
struct WelcomeView: View {
    @EnvironmentObject private var model: AppModel

    var body: some View {
        VStack(spacing: 16) {
            Text("🎯").font(.system(size: 56))
            Text("Block what distracts you")
                .font(.system(size: 22, weight: .heavy, design: .rounded))
                .multilineTextAlignment(.center)
            Text("Blockapp uses Screen Time to lock apps while you focus.")
                .font(.system(size: 15, design: .rounded))
                .foregroundStyle(Theme.muted)
                .multilineTextAlignment(.center)
            Button("Allow Screen Time") {
                Task { await model.requestAuthorization() }
            }
            .buttonStyle(GradientButtonStyle())
            if let error = model.error {
                Text(error).font(.footnote).foregroundStyle(Theme.bad)
            }
        }
        .padding(.vertical, 12)
        .card()
    }
}

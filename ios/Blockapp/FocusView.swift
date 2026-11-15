import FamilyControls
import SwiftUI

struct FocusView: View {
    @EnvironmentObject private var model: AppModel
    @AppStorage("length") private var length = 25
    @State private var showPicker = false
    @State private var confirmStop = false

    private let columns = [GridItem(.adaptive(minimum: 96), spacing: 10)]

    var body: some View {
        if model.isFocusing { running } else { setup }
    }

    // MARK: - Before starting

    private var setup: some View {
        VStack(spacing: 14) {
            VStack(alignment: .leading, spacing: 14) {
                StepTitle(number: 1, title: "Pick distractions", done: model.pickedCount > 0)
                LazyVGrid(columns: columns, spacing: 10) {
                    Tile(emoji: "📱", name: model.appCount > 0 ? "\(model.appCount) apps" : "Apps",
                         picked: model.appCount > 0) { showPicker = true }
                    ForEach(Catalog.sites) { site in
                        Tile(emoji: site.emoji, name: site.name, picked: model.sites.contains(site.id)) {
                            model.toggleSite(site.id)
                        }
                    }
                }
            }
            .card()

            VStack(spacing: 16) {
                StepTitle(number: 2, title: "Focus")
                HStack(spacing: 4) {
                    ForEach([25, 50, 90], id: \.self) { m in
                        Button("\(m)m") { length = m }
                            .buttonStyle(.plain)
                            .font(.system(size: 16, weight: .bold, design: .rounded))
                            .foregroundStyle(length == m ? Theme.ink : Theme.muted)
                            .frame(width: 66, height: 38)
                            .background {
                                if length == m { Capsule().fill(Theme.card).shadow(color: .black.opacity(0.08), radius: 4, y: 2) }
                            }
                    }
                }
                .padding(4)
                .background(Theme.soft, in: Capsule())

                Button("Start") { model.startFocus(minutes: length) }
                    .buttonStyle(GradientButtonStyle())
                    .disabled(model.pickedCount == 0)
                    .padding(.horizontal, 20)

                Text(model.pickedCount == 0 ? "Pick something first" : "Blocking \(model.pickedCount) \(model.pickedCount == 1 ? "thing" : "things")")
                    .font(.system(size: 13, design: .rounded))
                    .foregroundStyle(Theme.muted)
                if let error = model.error {
                    Text(error).font(.footnote).foregroundStyle(Theme.bad).multilineTextAlignment(.center)
                }
            }
            .frame(maxWidth: .infinity)
            .card()
        }
        .familyActivityPicker(isPresented: $showPicker, selection: Binding(
            get: { model.selection },
            set: { model.setSelection($0) }))
    }

    // MARK: - While focusing

    private var running: some View {
        TimelineView(.periodic(from: .now, by: 1)) { context in
            let end = model.sessionEnd ?? context.date
            let left = max(0, end.timeIntervalSince(context.date))
            let total = max(1, end.timeIntervalSince(model.sessionStart ?? context.date))
            VStack(spacing: 18) {
                Text("Focusing 🔒")
                    .font(.system(size: 17, weight: .heavy, design: .rounded))
                ZStack {
                    Circle().stroke(Theme.soft, lineWidth: 14)
                    Circle()
                        .trim(from: 0, to: min(1, left / total))
                        .stroke(Theme.gradient, style: StrokeStyle(lineWidth: 14, lineCap: .round))
                        .rotationEffect(.degrees(-90))
                        .animation(.linear(duration: 1), value: left)
                    VStack(spacing: 2) {
                        Text(countdown(left))
                            .font(.system(size: 44, weight: .heavy, design: .rounded))
                            .monospacedDigit()
                        Text("until \(end.formatted(date: .omitted, time: .shortened))")
                            .font(.system(size: 13, design: .rounded))
                            .foregroundStyle(Theme.muted)
                    }
                }
                .frame(width: 210, height: 210)

                Text("Blocking \(model.pickedCount) \(model.pickedCount == 1 ? "thing" : "things")")
                    .font(.system(size: 13, design: .rounded))
                    .foregroundStyle(Theme.muted)

                Button("Stop early") { confirmStop = true }
                    .font(.system(size: 15, weight: .semibold, design: .rounded))
                    .foregroundStyle(Theme.muted)
                    .padding(.horizontal, 18).padding(.vertical, 9)
                    .overlay(RoundedRectangle(cornerRadius: 12).stroke(Theme.line))
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 8)
            .card()
        }
        .confirmationDialog("Stop early? −10 points.", isPresented: $confirmStop, titleVisibility: .visible) {
            Button("Stop early", role: .destructive) { model.stopEarly() }
            Button("Keep focusing", role: .cancel) {}
        }
    }

    private func countdown(_ seconds: TimeInterval) -> String {
        let s = Int(seconds.rounded(.up))
        let h = s / 3600, m = (s % 3600) / 60, sec = s % 60
        return h > 0 ? String(format: "%d:%02d:%02d", h, m, sec) : String(format: "%d:%02d", m, sec)
    }
}

struct Tile: View {
    let emoji: String
    let name: String
    let picked: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                Text(emoji).font(.system(size: 26))
                Text(name)
                    .font(.system(size: 13, weight: .semibold, design: .rounded))
                    .lineLimit(1).minimumScaleFactor(0.8)
            }
            .frame(maxWidth: .infinity, minHeight: 76)
            .background(Theme.card, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .stroke(picked ? Theme.a1 : Theme.line, lineWidth: 2)
            }
            .shadow(color: picked ? Theme.a1.opacity(0.3) : .clear, radius: 6)
            .overlay(alignment: .topTrailing) {
                if picked {
                    Image(systemName: "checkmark")
                        .font(.system(size: 10, weight: .heavy))
                        .foregroundStyle(.white)
                        .frame(width: 18, height: 18)
                        .background(Theme.a1, in: Circle())
                        .padding(6)
                }
            }
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(picked ? .isSelected : [])
    }
}

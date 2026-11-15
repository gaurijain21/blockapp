import SwiftUI

struct StatsView: View {
    @EnvironmentObject private var model: AppModel

    var body: some View {
        let today = model.today
        VStack(spacing: 14) {
            HStack(spacing: 18) {
                ZStack {
                    Circle().stroke(Theme.soft, lineWidth: 12)
                    Circle()
                        .trim(from: 0, to: CGFloat(today.score) / 100)
                        .stroke(Theme.scoreColor(today.score), style: StrokeStyle(lineWidth: 12, lineCap: .round))
                        .rotationEffect(.degrees(-90))
                    Text("\(today.score)")
                        .font(.system(size: 34, weight: .heavy, design: .rounded))
                }
                .frame(width: 110, height: 110)
                VStack(alignment: .leading, spacing: 6) {
                    Text(DayStats.label(today.score))
                        .font(.system(size: 18, weight: .heavy, design: .rounded))
                    Text("\(today.attempts) tries · \(today.skips) stops")
                        .font(.system(size: 14, design: .rounded))
                        .foregroundStyle(Theme.muted)
                }
            }
            .card()

            VStack(alignment: .leading, spacing: 12) {
                Text("Last 7 days").font(.system(size: 17, weight: .heavy, design: .rounded))
                HStack(alignment: .bottom, spacing: 10) {
                    ForEach(model.week) { d in
                        VStack(spacing: 6) {
                            GeometryReader { geo in
                                VStack {
                                    Spacer(minLength: 0)
                                    RoundedRectangle(cornerRadius: 8, style: .continuous)
                                        .fill(Theme.scoreColor(d.score))
                                        .frame(height: max(4, geo.size.height * CGFloat(d.score) / 100))
                                }
                            }
                            Text(d.day.formatted(.dateTime.weekday(.narrow)))
                                .font(.system(size: 12, weight: .semibold, design: .rounded))
                                .foregroundStyle(Theme.muted)
                        }
                        .accessibilityElement(children: .ignore)
                        .accessibilityLabel("\(d.day.formatted(.dateTime.weekday(.wide))): \(d.score)")
                    }
                }
                .frame(height: 140)
            }
            .card()
        }
    }
}

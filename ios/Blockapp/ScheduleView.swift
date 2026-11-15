import SwiftUI

struct ScheduleView: View {
    @EnvironmentObject private var model: AppModel
    @State private var days: Set<Int> = [2, 3, 4, 5, 6]
    @State private var start = ScheduleView.time(9, 0)
    @State private var end = ScheduleView.time(12, 0)

    private static func time(_ h: Int, _ m: Int) -> Date {
        Calendar.current.date(bySettingHour: h, minute: m, second: 0, of: Date()) ?? Date()
    }

    var body: some View {
        VStack(spacing: 14) {
            VStack(alignment: .leading, spacing: 14) {
                StepTitle(number: 1, title: "Days")
                HStack(spacing: 6) {
                    ForEach(Engine.weekOrder, id: \.self) { d in
                        let on = days.contains(d)
                        Button {
                            if on { days.remove(d) } else { days.insert(d) }
                        } label: {
                            Text(Calendar.current.veryShortWeekdaySymbols[d - 1])
                                .font(.system(size: 15, weight: .bold, design: .rounded))
                                .foregroundStyle(on ? Color.white : Theme.muted)
                                .frame(maxWidth: .infinity, minHeight: 40)
                                .background {
                                    if on { Circle().fill(Theme.gradient) } else { Circle().fill(Theme.soft) }
                                }
                        }
                        .buttonStyle(.plain)
                        .accessibilityLabel(Calendar.current.weekdaySymbols[d - 1])
                        .accessibilityAddTraits(on ? .isSelected : [])
                    }
                }

                StepTitle(number: 2, title: "Time")
                HStack {
                    DatePicker("From", selection: $start, displayedComponents: .hourAndMinute)
                        .labelsHidden()
                    Text("–").foregroundStyle(Theme.muted)
                    DatePicker("To", selection: $end, displayedComponents: .hourAndMinute)
                        .labelsHidden()
                    Spacer()
                    Button {
                        model.addSchedule(days: days, start: start, end: end)
                    } label: {
                        Image(systemName: "plus")
                            .font(.system(size: 18, weight: .heavy))
                            .foregroundStyle(.white)
                            .frame(width: 44, height: 44)
                            .background(Theme.gradient, in: Circle())
                    }
                    .accessibilityLabel("Add")
                }
                if let error = model.error {
                    Text(error).font(.footnote).foregroundStyle(Theme.bad)
                }
            }
            .card()

            VStack(alignment: .leading, spacing: 10) {
                if model.schedules.isEmpty {
                    Text("Nothing yet")
                        .font(.system(size: 14, design: .rounded))
                        .foregroundStyle(Theme.muted)
                        .frame(maxWidth: .infinity)
                } else {
                    ForEach(model.schedules) { s in
                        HStack {
                            Text("⏰")
                            Text(Engine.describe(s)).font(.system(size: 15, weight: .semibold, design: .rounded))
                            Spacer()
                            Button { model.removeSchedule(s) } label: {
                                Image(systemName: "xmark").foregroundStyle(Theme.muted)
                            }
                            .accessibilityLabel("Remove")
                        }
                        .padding(12)
                        .background(Theme.soft, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                    }
                    if let next = Engine.nextStart(after: Date(), schedules: model.schedules) {
                        Text("Next: \(next.formatted(.dateTime.weekday(.abbreviated).hour().minute()))")
                            .font(.system(size: 13, design: .rounded))
                            .foregroundStyle(Theme.muted)
                    }
                }
            }
            .card()
        }
    }
}

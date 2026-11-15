import SwiftUI

@main
struct BlockappApp: App {
    @StateObject private var model = AppModel()
    @AppStorage("theme") private var theme = "system"
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(model)
                .preferredColorScheme(theme == "dark" ? .dark : theme == "light" ? .light : nil)
                .onChange(of: scenePhase) { phase in
                    if phase == .active { model.refresh() }
                }
        }
    }
}

import ManagedSettings
import ManagedSettingsUI
import UIKit

/// The screen people see when they open something blocked.
class ShieldConfigExtension: ShieldConfigurationDataSource {
    override func configuration(shielding application: Application) -> ShieldConfiguration {
        shield(application.localizedDisplayName)
    }

    override func configuration(shielding application: Application, in category: ActivityCategory) -> ShieldConfiguration {
        shield(application.localizedDisplayName)
    }

    override func configuration(shielding webDomain: WebDomain) -> ShieldConfiguration {
        shield(webDomain.domain)
    }

    override func configuration(shielding webDomain: WebDomain, in category: ActivityCategory) -> ShieldConfiguration {
        shield(webDomain.domain)
    }

    private func shield(_ name: String?) -> ShieldConfiguration {
        let purple = UIColor(red: 0x6d / 255, green: 0x4a / 255, blue: 1, alpha: 1)
        let pink = UIColor(red: 1, green: 0x5c / 255, blue: 0x9a / 255, alpha: 1)
        return ShieldConfiguration(
            backgroundBlurStyle: .systemUltraThinMaterialDark,
            backgroundColor: purple.withAlphaComponent(0.85),
            icon: UIImage(systemName: "target"),
            title: ShieldConfiguration.Label(text: "Focus time 🎯", color: .white),
            subtitle: ShieldConfiguration.Label(
                text: "\(name ?? "This") is blocked until your session ends.",
                color: UIColor.white.withAlphaComponent(0.85)),
            primaryButtonLabel: ShieldConfiguration.Label(text: "Back to focus", color: .white),
            primaryButtonBackgroundColor: pink,
            secondaryButtonLabel: nil)
    }
}

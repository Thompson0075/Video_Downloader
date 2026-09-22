pragma Singleton
import QtQuick

QtObject {
    // Brand
    readonly property color accent: "#6C8CFF"
    readonly property color accentAlt: "#A78BFA"
    readonly property color success: "#34D399"
    readonly property color warn: "#FBBF24"
    readonly property color danger: "#F87171"

    // Surfaces (dark glass)
    readonly property color bg: "#0B0D14"
    readonly property color bgElevated: "#12162A"
    readonly property color card: "#161B2E"
    readonly property color cardHover: "#1C2340"
    readonly property color stroke: "#2A3352"
    readonly property color strokeSoft: "#232A44"

    // Text
    readonly property color textPrimary: "#F3F5FF"
    readonly property color textSecondary: "#A8B0CC"
    readonly property color textMuted: "#6B7394"

    readonly property int radiusSm: 10
    readonly property int radiusMd: 14
    readonly property int radiusLg: 20

    readonly property int animFast: 140
    readonly property int animBase: 220
    readonly property int animSlow: 380

    readonly property string fontFamilies: "Segoe UI, Microsoft YaHei UI, PingFang SC, sans-serif"
}

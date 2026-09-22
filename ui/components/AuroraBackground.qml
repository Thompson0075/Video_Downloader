import QtQuick
import QtQuick.Effects

// Soft animated aurora background with floating orbs.
Item {
    id: root

    Rectangle {
        anchors.fill: parent
        color: "#0B0D14"
    }

    // Large blurred gradient blobs
    component Orb: Rectangle {
        property real baseX: 0.2
        property real baseY: 0.3
        property real amp: 40
        property real speed: 0.00025
        property color orbColor: "#6C8CFF"
        property real orbSize: 320
        property real orbOpacity: 0.35
        property real phase: 0

        x: parent.width * baseX - width / 2
        y: parent.height * baseY - height / 2
        width: orbSize
        height: orbSize
        radius: width / 2
        color: orbColor
        opacity: orbOpacity
        layer.enabled: true
        layer.effect: MultiEffect {
            blurEnabled: true
            blur: 0.85
            blurMax: 64
        }

        NumberAnimation on x {
            loops: Animation.Infinite
            running: true
            from: root.width * baseX - width / 2 - amp
            to: root.width * baseX - width / 2 + amp
            duration: 7000 + (phase * 1300)
            easing.type: Easing.InOutSine
        }
        NumberAnimation on y {
            loops: Animation.Infinite
            running: true
            from: root.height * baseY - height / 2 + amp * 0.6
            to: root.height * baseY - height / 2 - amp * 0.6
            duration: 9000 + (phase * 900)
            easing.type: Easing.InOutSine
        }
        NumberAnimation on opacity {
            loops: Animation.Infinite
            running: true
            from: orbOpacity * 0.7
            to: orbOpacity
            duration: 4200
            easing.type: Easing.InOutSine
        }
    }

    Orb {
        baseX: 0.15
        baseY: 0.2
        orbColor: "#5B7CFF"
        orbSize: 360
        orbOpacity: 0.32
        phase: 0
    }
    Orb {
        baseX: 0.85
        baseY: 0.15
        orbColor: "#A78BFA"
        orbSize: 300
        orbOpacity: 0.28
        phase: 1.2
    }
    Orb {
        baseX: 0.75
        baseY: 0.85
        orbColor: "#22D3EE"
        orbSize: 280
        orbOpacity: 0.18
        phase: 2.1
    }
    Orb {
        baseX: 0.25
        baseY: 0.9
        orbColor: "#F472B6"
        orbSize: 240
        orbOpacity: 0.14
        phase: 3.0
    }

    // Subtle vignette
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#55000000" }
            GradientStop { position: 0.45; color: "#22000000" }
            GradientStop { position: 1.0; color: "#66000000" }
        }
    }
}

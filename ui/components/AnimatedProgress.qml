import QtQuick

// Slim animated progress bar with shimmer.
Item {
    id: root
    property real value: 0 // 0..1
    property color barFrom: "#6C8CFF"
    property color barTo: "#A78BFA"
    property string label: ""
    property string trailing: ""

    implicitHeight: 10
    implicitWidth: 240

    Rectangle {
        id: track
        anchors.fill: parent
        radius: height / 2
        color: "#232A44"
        clip: true

        Rectangle {
            id: fill
            width: Math.max(parent.width * root.value, root.value > 0 ? 8 : 0)
            height: parent.height
            radius: height / 2
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: root.barFrom }
                GradientStop { position: 1.0; color: root.barTo }
            }
            Behavior on width {
                NumberAnimation { duration: 280; easing.type: Easing.OutCubic }
            }

            // Shimmer highlight
            Rectangle {
                width: 36
                height: parent.height
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0.0; color: "#00FFFFFF" }
                    GradientStop { position: 0.5; color: "#66FFFFFF" }
                    GradientStop { position: 1.0; color: "#00FFFFFF" }
                }
                x: -width
                visible: root.value > 0 && root.value < 1
                SequentialAnimation on x {
                    running: visible
                    loops: Animation.Infinite
                    NumberAnimation { from: -36; to: fill.width; duration: 1100; easing.type: Easing.InOutSine }
                    NumberAnimation { from: fill.width; to: -36; duration: 0 }
                }
            }
        }
    }

    Text {
        visible: root.label.length > 0
        anchors.right: parent.left
        anchors.rightMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        text: root.label
        color: "#A8B0CC"
        font.pixelSize: 12
        font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
    }

    Text {
        visible: root.trailing.length > 0
        anchors.left: parent.right
        anchors.leftMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        text: root.trailing
        color: "#A8B0CC"
        font.pixelSize: 12
        font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
    }
}

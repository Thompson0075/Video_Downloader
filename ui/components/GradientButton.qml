import QtQuick

// Gradient pill button with press / hover animation.
Rectangle {
    id: root
    property alias text: label.text
    property bool enabled: true
    property bool busy: false
    property color accentFrom: "#6C8CFF"
    property color accentTo: "#A78BFA"
    property int fontSize: 15
    signal clicked()

    implicitWidth: 132
    implicitHeight: 44
    radius: height / 2
    opacity: enabled ? 1.0 : 0.45
    scale: press.pressed ? 0.96 : (hover.containsMouse ? 1.04 : 1.0)

    gradient: Gradient {
        GradientStop { id: g0; position: 0.0; color: root.enabled ? root.accentFrom : "#3A415F" }
        GradientStop { id: g1; position: 1.0; color: root.enabled ? root.accentTo : "#2A3148" }
    }

    Behavior on scale {
        NumberAnimation { duration: 150; easing.type: Easing.OutBack }
    }
    Behavior on opacity {
        NumberAnimation { duration: 150 }
    }

    // Hover sheen
    Rectangle {
        anchors.fill: parent
        radius: parent.radius
        opacity: hover.containsMouse ? 0.18 : 0.0
        color: "#FFFFFF"
        Behavior on opacity { NumberAnimation { duration: 180 } }
    }

    // Busy spinner
    Item {
        id: spinner
        visible: root.busy
        anchors.centerIn: parent
        width: 18
        height: 18
        rotation: 0
        NumberAnimation on rotation {
            running: root.busy
            loops: Animation.Infinite
            from: 0
            to: 360
            duration: 800
        }
        Rectangle {
            anchors.fill: parent
            radius: width / 2
            color: "transparent"
            border.color: "#FFFFFF55"
            border.width: 2
        }
        Rectangle {
            width: 4
            height: 4
            radius: 2
            color: "#FFFFFF"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: -1
        }
    }

    Text {
        id: label
        visible: !root.busy
        anchors.centerIn: parent
        color: "#FFFFFF"
        font.pixelSize: root.fontSize
        font.bold: true
        font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
    }

    MouseArea {
        id: hover
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
    }

    MouseArea {
        id: press
        anchors.fill: parent
        enabled: root.enabled && !root.busy
        onClicked: root.clicked()
    }
}

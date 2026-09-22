import QtQuick

// Frosted glass card with hover lift. Children fill the padded content area.
Item {
    id: root

    property bool interactive: false
    property color baseColor: "#161B2ECC"
    property color hoverColor: "#1C2340DD"
    property int padding: 18

    default property alias content: contentArea.data

    // Size to content when not explicitly laid out
    implicitWidth: contentArea.implicitWidth + padding * 2
    implicitHeight: contentArea.childrenRect.height + padding * 2

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: 18
        color: mouse.containsMouse && root.interactive ? root.hoverColor : root.baseColor
        border.color: mouse.containsMouse && root.interactive ? "#6C8CFF55" : "#2A3352AA"
        border.width: 1

        Behavior on color {
            ColorAnimation { duration: 180 }
        }
        Behavior on border.color {
            ColorAnimation { duration: 180 }
        }
    }

    Item {
        id: contentArea
        x: root.padding
        y: root.padding
        width: Math.max(0, root.width - root.padding * 2)
        height: childrenRect.height
    }

    // Soft outer edge
    Rectangle {
        anchors.fill: bg
        anchors.margins: -1
        z: -1
        radius: bg.radius + 1
        color: "transparent"
        border.color: "#00000055"
        border.width: 1
    }

    scale: mouse.containsMouse && interactive ? 1.015 : 1.0
    Behavior on scale {
        NumberAnimation { duration: 180; easing.type: Easing.OutCubic }
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        enabled: root.interactive
        propagateComposedEvents: true
        onPressed: (mouse) => mouse.accepted = false
    }
}

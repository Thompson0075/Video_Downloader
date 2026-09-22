import QtQuick

// Pill toggle switch with label.
Item {
    id: root
    property alias text: label.text
    property bool checked: false
    signal toggled(bool checked)

    implicitHeight: 30
    implicitWidth: row.implicitWidth

    Row {
        id: row
        anchors.verticalCenter: parent.verticalCenter
        spacing: 8

        Text {
            id: label
            anchors.verticalCenter: parent.verticalCenter
            color: "#A8B0CC"
            font.pixelSize: 12
            font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
        }

        Rectangle {
            id: track
            width: 40
            height: 22
            radius: 11
            anchors.verticalCenter: parent.verticalCenter
            color: root.checked ? "#6C8CFF" : "#2A3352"
            border.color: root.checked ? "#A78BFA" : "#3A4568"
            Behavior on color { ColorAnimation { duration: 160 } }

            Rectangle {
                id: knob
                width: 18
                height: 18
                radius: 9
                color: "#FFFFFF"
                anchors.verticalCenter: parent.verticalCenter
                x: root.checked ? parent.width - width - 2 : 2
                Behavior on x {
                    NumberAnimation { duration: 180; easing.type: Easing.OutCubic }
                }
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    root.checked = !root.checked
                    root.toggled(root.checked)
                }
            }
        }
    }
}

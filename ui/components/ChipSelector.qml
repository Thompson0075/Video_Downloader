import QtQuick

// Quality / mode chip selector.
Item {
    id: root
    property var options: [
        { key: "best", label: "最佳画质" },
        { key: "1080", label: "1080p" },
        { key: "720", label: "720p" },
        { key: "480", label: "480p" },
        { key: "audio", label: "仅音频" }
    ]
    property string current: "best"
    signal selected(string key)

    implicitHeight: 40
    implicitWidth: row.implicitWidth + 8

    Rectangle {
        anchors.fill: parent
        radius: 20
        color: "#12162AEE"
        border.color: "#2A3352"
        border.width: 1
    }

    Row {
        id: row
        anchors.centerIn: parent
        spacing: 4

        Repeater {
            model: root.options
            delegate: Rectangle {
                id: chip
                required property var modelData
                property bool active: root.current === modelData.key

                width: chipLabel.implicitWidth + 28
                height: 32
                radius: 16
                color: active ? "#6C8CFF" : (hover.containsMouse ? "#1C2340" : "transparent")
                scale: hover.containsMouse && !active ? 1.05 : 1.0

                Behavior on color { ColorAnimation { duration: 160 } }
                Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutBack } }

                Text {
                    id: chipLabel
                    anchors.centerIn: parent
                    text: chip.modelData.label
                    color: chip.active ? "#FFFFFF" : "#A8B0CC"
                    font.pixelSize: 13
                    font.bold: chip.active
                    font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                    Behavior on color { ColorAnimation { duration: 160 } }
                }

                MouseArea {
                    id: hover
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.selected(chip.modelData.key)
                }
            }
        }
    }
}

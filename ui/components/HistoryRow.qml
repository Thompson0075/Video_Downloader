import QtQuick
import QtQuick.Layouts

// One history item: clearly separated card with open / redownload / delete.
Rectangle {
    id: root
    property var item: ({
        id: "", title: "", url: "", filepath: "",
        quality: "", time: "", exists: false
    })
    property int rowIndex: 0
    signal openRequested(string path)
    signal redownloadRequested(string id)
    signal removeRequested(string id)

    // Layout-managed: never animate y (would overlap siblings)
    Layout.fillWidth: true
    Layout.preferredHeight: 88
    Layout.minimumHeight: 88
    radius: 14
    color: "#161B2ECC"
    border.color: hover.containsMouse ? "#6C8CFF55" : "#2A3352AA"
    border.width: 1

    // Entrance: opacity + scale only
    opacity: 0
    scale: 0.98
    Component.onCompleted: {
        animOpacity.start()
        animScale.start()
    }
    NumberAnimation { id: animOpacity; target: root; property: "opacity"; to: 1; duration: 240; easing.type: Easing.OutCubic }
    NumberAnimation { id: animScale; target: root; property: "scale"; to: 1; duration: 280; easing.type: Easing.OutCubic }
    Behavior on border.color { ColorAnimation { duration: 150 } }
    Behavior on color { ColorAnimation { duration: 150 } }

    HoverHandler {
        id: hover
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 12

        // Index badge
        Rectangle {
            Layout.preferredWidth: 28
            Layout.preferredHeight: 28
            Layout.alignment: Qt.AlignVCenter
            radius: 8
            color: "#0B0D14AA"
            border.color: "#2A3352"
            Text {
                anchors.centerIn: parent
                text: (root.rowIndex + 1).toString()
                color: "#6B7394"
                font.pixelSize: 11
                font.bold: true
                font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
            }
        }

        // Text block (expands, elides)
        ColumnLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            spacing: 4

            Text {
                Layout.fillWidth: true
                text: root.item.title || root.item.url || "未命名"
                color: "#F3F5FF"
                elide: Text.ElideRight
                font.pixelSize: 13
                font.bold: true
                font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
            }
            Text {
                Layout.fillWidth: true
                text: {
                    var bits = []
                    if (root.item.time) bits.push(root.item.time)
                    if (root.item.quality) bits.push(root.item.quality)
                    bits.push(root.item.exists ? "已就绪" : "文件缺失")
                    return bits.join("  ·  ")
                }
                color: root.item.exists ? "#6B7394" : "#FBBF24"
                elide: Text.ElideRight
                font.pixelSize: 11
                font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
            }
        }

        // Action buttons — fixed compact row, never overlaps text
        RowLayout {
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
            spacing: 6

            component HBtn: Rectangle {
                property alias text: t.text
                property color fg: "#A8B0CC"
                signal clicked()
                Layout.preferredWidth: Math.max(52, t.implicitWidth + 16)
                Layout.preferredHeight: 28
                radius: 10
                color: btnHover.containsMouse ? "#1C2340" : "transparent"
                border.color: "#2A3352"
                Text {
                    id: t
                    anchors.centerIn: parent
                    color: parent.fg
                    font.pixelSize: 12
                    font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                }
                HoverHandler { id: btnHover }
                TapHandler {
                    onTapped: parent.clicked()
                }
            }

            HBtn {
                text: "打开"
                fg: root.item.exists ? "#34D399" : "#4A5170"
                onClicked: {
                    if (root.item.filepath)
                        root.openRequested(root.item.filepath)
                }
            }
            HBtn {
                text: "重下"
                fg: "#6C8CFF"
                onClicked: root.redownloadRequested(root.item.id)
            }
            HBtn {
                text: "删除"
                fg: "#F87171"
                onClicked: root.removeRequested(root.item.id)
            }
        }
    }
}

import QtQuick
import QtQuick.Layouts

// One download task row with live progress.
Rectangle {
    id: root
    property var job: ({
        id: "", title: "", status: "queued", percent: 0,
        speed_text: "—", eta_text: "—", size_text: "—",
        url: "", filepath: "", error: ""
    })
    signal cancelRequested(string jobId)
    signal openRequested(string path)

    // Layout-managed width/height — do not animate y (overlaps siblings)
    Layout.fillWidth: true
    Layout.preferredHeight: 108
    radius: 16
    color: "#161B2ECC"
    border.color: statusColor(0.35)
    border.width: 1

    function statusColor(alpha) {
        var s = root.job.status
        if (s === "completed") return Qt.rgba(0.20, 0.83, 0.60, alpha)
        if (s === "error") return Qt.rgba(0.97, 0.44, 0.44, alpha)
        if (s === "cancelled") return Qt.rgba(0.42, 0.45, 0.58, alpha)
        if (s === "cancelling") return Qt.rgba(0.98, 0.75, 0.14, alpha)
        return Qt.rgba(0.42, 0.55, 1.0, alpha)
    }

    function statusLabel() {
        var s = root.job.status
        if (s === "queued") return "排队中"
        if (s === "starting") return "准备中"
        if (s === "downloading") return "下载中"
        if (s === "processing") return "合并中"
        if (s === "completed") return "已完成"
        if (s === "cancelled") return "已取消"
        if (s === "cancelling") return "取消中"
        if (s === "error") return "失败"
        return s
    }

    // Entry animation (opacity/scale only — y would fight ColumnLayout)
    opacity: 0
    scale: 0.98
    Component.onCompleted: {
        enterOpacity.start()
        enterScale.start()
    }
    NumberAnimation { id: enterOpacity; target: root; property: "opacity"; to: 1; duration: 280; easing.type: Easing.OutCubic }
    NumberAnimation { id: enterScale; target: root; property: "scale"; to: 1; duration: 320; easing.type: Easing.OutCubic }

    Row {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 16
        spacing: 12

        // Status dot with pulse while downloading
        Rectangle {
            width: 10
            height: 10
            radius: 5
            anchors.verticalCenter: parent.verticalCenter
            color: root.statusColor(1.0)
            SequentialAnimation on scale {
                running: root.job.status === "downloading" || root.job.status === "starting"
                loops: Animation.Infinite
                NumberAnimation { from: 1.0; to: 1.35; duration: 550; easing.type: Easing.InOutSine }
                NumberAnimation { from: 1.35; to: 1.0; duration: 550; easing.type: Easing.InOutSine }
            }
        }

        Column {
            width: parent.width - 10 - 12 - 90
            spacing: 4

            Text {
                width: parent.width
                text: root.job.title || root.job.url
                color: "#F3F5FF"
                elide: Text.ElideRight
                font.pixelSize: 14
                font.bold: true
                font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
            }

            Text {
                width: parent.width
                text: {
                    if (root.job.status === "error")
                        return root.job.error || "未知错误"
                    return statusLabel() + "  ·  " + root.job.speed_text
                           + "  ·  ETA " + root.job.eta_text
                           + "  ·  " + root.job.size_text
                }
                color: root.job.status === "error" ? "#F87171" : "#A8B0CC"
                elide: Text.ElideRight
                font.pixelSize: 12
                font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
            }
        }

        // Actions
        Row {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 8

            Rectangle {
                visible: root.job.status === "completed" && root.job.filepath
                width: openLabel.implicitWidth + 18
                height: 28
                radius: 14
                color: "#34D39933"
                border.color: "#34D39988"
                Text {
                    id: openLabel
                    anchors.centerIn: parent
                    text: "打开"
                    color: "#34D399"
                    font.pixelSize: 12
                    font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                }
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.openRequested(root.job.filepath)
                }
            }

            Rectangle {
                visible: ["queued","starting","downloading","processing"].indexOf(root.job.status) >= 0
                width: cancelLabel.implicitWidth + 18
                height: 28
                radius: 14
                color: "#F8717133"
                border.color: "#F8717188"
                Text {
                    id: cancelLabel
                    anchors.centerIn: parent
                    text: "取消"
                    color: "#F87171"
                    font.pixelSize: 12
                    font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                }
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.cancelRequested(root.job.id)
                }
            }
        }
    }

    // Progress bar
    AnimatedProgress {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        anchors.bottomMargin: 16
        height: 8
        value: (root.job.percent || 0) / 100.0
        barFrom: root.job.status === "error" ? "#F87171" : (root.job.status === "completed" ? "#34D399" : "#6C8CFF")
        barTo: root.job.status === "error" ? "#FCA5A5" : (root.job.status === "completed" ? "#6EE7B7" : "#A78BFA")
    }
}

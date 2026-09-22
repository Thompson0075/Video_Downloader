import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import "components"

ApplicationWindow {
    id: window
    width: 1080
    height: 720
    minimumWidth: 880
    minimumHeight: 620
    visible: true
    title: qsTr("视频下载器 · Video Downloader")
    color: "transparent"
    flags: Qt.Window | Qt.FramelessWindowHint

    // ---- helpers ----
    property string analyzeUrl: ""
    property var videoInfo: null
    property bool analyzing: false
    property var jobs: ({})  // id -> job dict
    property var jobOrder: []
    property var sortedIds: []
    property var historyItems: []
    property bool subsEnabled: false
    property bool shutdownEnabled: false

    function statusRank(s) {
        if (s === "downloading" || s === "starting" || s === "processing") return 0
        if (s === "queued") return 1
        if (s === "cancelling") return 2
        return 3
    }

    function recomputeSorted() {
        var ids = jobOrder.slice()
        ids.sort(function (a, b) {
            var ja = jobs[a] || {}
            var jb = jobs[b] || {}
            var ra = statusRank(ja.status)
            var rb = statusRank(jb.status)
            if (ra !== rb) return ra - rb
            return 0
        })
        sortedIds = ids
    }

    function upsertJob(job) {
        if (!job || !job.id) return
        var map = {}
        for (var k in jobs) map[k] = jobs[k]
        map[job.id] = job
        jobs = map
        if (jobOrder.indexOf(job.id) < 0) {
            var order = jobOrder.slice()
            order.unshift(job.id)
            jobOrder = order
        }
        recomputeSorted()
    }

    // Frameless drag
    MouseArea {
        id: dragArea
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 52
        property real startX: 0
        property real startY: 0
        onPressed: (mouse) => {
            startX = mouse.globalX - window.x
            startY = mouse.globalY - window.y
        }
        onPositionChanged: (mouse) => {
            if (pressed) {
                window.x = mouse.globalX - startX
                window.y = mouse.globalY - startY
            }
        }
        onDoubleClicked: {
            if (window.visibility === Window.Maximized)
                window.showNormal()
            else
                window.showMaximized()
        }
    }

    // Outer glass frame
    Rectangle {
        anchors.fill: parent
        anchors.margins: 8
        radius: 20
        color: "#E60B0D14"
        border.color: "#2A3352"
        border.width: 1
        clip: true

        AuroraBackground {
            anchors.fill: parent
        }

        // Title bar
        Rectangle {
            id: titleBar
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 52
            color: "transparent"

            Row {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: 18
                spacing: 10

                // Logo mark
                Rectangle {
                    width: 28
                    height: 28
                    radius: 8
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: "#6C8CFF" }
                        GradientStop { position: 1.0; color: "#A78BFA" }
                    }
                    Text {
                        anchors.centerIn: parent
                        text: "↓"
                        color: "white"
                        font.pixelSize: 16
                        font.bold: true
                    }
                    // subtle pulse
                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        running: true
                        NumberAnimation { from: 1.0; to: 1.06; duration: 1600; easing.type: Easing.InOutSine }
                        NumberAnimation { from: 1.06; to: 1.0; duration: 1600; easing.type: Easing.InOutSine }
                    }
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: qsTr("视频下载器")
                    color: "#F3F5FF"
                    font.pixelSize: 15
                    font.bold: true
                    font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "v" + Backend.appVersion()
                    color: "#6B7394"
                    font.pixelSize: 11
                    font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                }
            }

            // Window controls
            Row {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.rightMargin: 10
                spacing: 4

                component WinBtn: Rectangle {
                    property alias glyph: g.text
                    property color hoverBg: "#1C2340"
                    signal activated()
                    width: 34
                    height: 28
                    radius: 8
                    color: btnHover.containsMouse ? hoverBg : "transparent"
                    Behavior on color { ColorAnimation { duration: 140 } }
                    Text {
                        id: g
                        anchors.centerIn: parent
                        color: "#A8B0CC"
                        font.pixelSize: 12
                        font.family: "Segoe UI Symbol, Segoe UI, sans-serif"
                    }
                    MouseArea {
                        id: btnHover
                        hoverEnabled: true
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: parent.activated()
                    }
                }

                WinBtn {
                    glyph: "—"
                    onActivated: window.showMinimized()
                }
                WinBtn {
                    glyph: window.visibility === Window.Maximized ? "❐" : "☐"
                    onActivated: {
                        if (window.visibility === Window.Maximized)
                            window.showNormal()
                        else
                            window.showMaximized()
                    }
                }
                WinBtn {
                    glyph: "✕"
                    hoverBg: "#F8717155"
                    onActivated: Qt.quit()
                }
            }
        }

        // Main content
        Flickable {
            id: scroller
            anchors.top: titleBar.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.leftMargin: 22
            anchors.rightMargin: 22
            anchors.bottomMargin: 18
            contentWidth: width
            contentHeight: mainCol.implicitHeight + 24
            clip: true
            boundsBehavior: Flickable.StopAtBounds

            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
                contentItem: Rectangle {
                    implicitWidth: 6
                    radius: 3
                    color: "#2A3352"
                }
            }

            ColumnLayout {
                id: mainCol
                width: scroller.width
                spacing: 16

                // Hero / URL input
                GlassCard {
                    id: heroCard
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.max(180, heroCol.implicitHeight + 36)
                    // entrance
                    opacity: 0
                    y: 16
                    Component.onCompleted: { a1.start(); a2.start() }
                    NumberAnimation { id: a1; target: heroCard; property: "opacity"; to: 1; duration: 420; easing.type: Easing.OutCubic }
                    NumberAnimation { id: a2; target: heroCard; property: "y"; to: 0; duration: 480; easing.type: Easing.OutCubic }

                    ColumnLayout {
                        id: heroCol
                        width: parent.width
                        spacing: 14

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                text: qsTr("粘贴视频链接，一键解析下载")
                                color: "#F3F5FF"
                                font.pixelSize: 20
                                font.bold: true
                                font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                            }
                            Item { Layout.fillWidth: true }
                            Text {
                                text: Backend.supportedHint()
                                color: "#6B7394"
                                font.pixelSize: 12
                                font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10

                            // URL field
                            Rectangle {
                                Layout.fillWidth: true
                                height: 48
                                radius: 14
                                color: "#0B0D14AA"
                                border.color: urlField.activeFocus ? "#6C8CFF" : "#2A3352"
                                border.width: 1
                                Behavior on border.color { ColorAnimation { duration: 160 } }

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 14
                                    anchors.rightMargin: 8
                                    spacing: 8

                                    Text {
                                        text: "🔗"
                                        font.pixelSize: 14
                                        color: "#6B7394"
                                    }

                                    TextInput {
                                        id: urlField
                                        Layout.fillWidth: true
                                        color: "#F3F5FF"
                                        font.pixelSize: 14
                                        font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                                        clip: true
                                        selectByMouse: true
                                        verticalAlignment: TextInput.AlignVCenter
                                        Text {
                                            visible: urlField.text.length === 0
                                            text: qsTr("https://  支持 YouTube / Bilibili / …")
                                            color: "#6B7394"
                                            font.pixelSize: 14
                                            font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                                            anchors.verticalCenter: parent.verticalCenter
                                        }
                                        Keys.onReturnPressed: analyzeBtn.clicked()
                                        Keys.onEnterPressed: analyzeBtn.clicked()
                                    }

                                    // Paste
                                    Rectangle {
                                        width: 64
                                        height: 32
                                        radius: 10
                                        color: pasteHover.containsMouse ? "#1C2340" : "transparent"
                                        Text {
                                            anchors.centerIn: parent
                                            text: qsTr("粘贴")
                                            color: "#A8B0CC"
                                            font.pixelSize: 12
                                            font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                                        }
                                        MouseArea {
                                            id: pasteHover
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                var t = Backend.pasteClipboard()
                                                if (t) {
                                                    urlField.text = t
                                                    toast.push("info", "已粘贴剪贴板内容")
                                                }
                                            }
                                        }
                                    }
                                }
                            }

                            GradientButton {
                                id: analyzeBtn
                                text: qsTr("解析")
                                busy: window.analyzing
                                implicitWidth: 108
                                onClicked: {
                                    window.analyzeUrl = urlField.text
                                    Backend.analyze(urlField.text)
                                }
                            }

                            GradientButton {
                                id: downloadBtn
                                text: qsTr("直接下载")
                                implicitWidth: 124
                                accentFrom: "#A78BFA"
                                accentTo: "#F472B6"
                                onClicked: {
                                    if (!urlField.text.trim()) {
                                        toast.push("error", "请输入视频链接")
                                        return
                                    }
                                    Backend.startDownload(urlField.text, "auto")
                                }
                            }
                        }

                        // Quality chips
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12
                            Text {
                                text: qsTr("画质")
                                color: "#6B7394"
                                font.pixelSize: 12
                                font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                            }
                            ChipSelector {
                                id: qualityChip
                                current: Backend.quality
                                onSelected: (key) => {
                                    Backend.quality = key
                                    current = key
                                }
                            }
                            Item { Layout.fillWidth: true }
                            Text {
                                text: qsTr("保存至 ") + Backend.downloadDir
                                color: "#6B7394"
                                elide: Text.ElideMiddle
                                Layout.maximumWidth: 280
                                font.pixelSize: 12
                                font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                            }
                            Rectangle {
                                width: folderLabel.implicitWidth + 16
                                height: 28
                                radius: 10
                                color: folderHover.containsMouse ? "#1C2340" : "transparent"
                                border.color: "#2A3352"
                                Text {
                                    id: folderLabel
                                    anchors.centerIn: parent
                                    text: qsTr("更改")
                                    color: "#A8B0CC"
                                    font.pixelSize: 12
                                    font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                                }
                                MouseArea {
                                    id: folderHover
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: Backend.pickFolder()
                                }
                            }
                            Rectangle {
                                width: openFolderLabel.implicitWidth + 16
                                height: 28
                                radius: 10
                                color: ofHover.containsMouse ? "#1C2340" : "transparent"
                                border.color: "#2A3352"
                                Text {
                                    id: openFolderLabel
                                    anchors.centerIn: parent
                                    text: qsTr("打开目录")
                                    color: "#A8B0CC"
                                    font.pixelSize: 12
                                    font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                                }
                                MouseArea {
                                    id: ofHover
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: Backend.openDownloadDir()
                                }
                            }
                        }

                        // Options row: subtitles + auto shutdown
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 18

                            ToggleSwitch {
                                id: subsToggle
                                text: qsTr("下载字幕（优先中文）")
                                checked: window.subsEnabled
                                onToggled: (v) => {
                                    Backend.downloadSubtitles = v
                                    window.subsEnabled = v
                                }
                            }

                            ToggleSwitch {
                                id: shutdownToggle
                                text: qsTr("全部完成后自动关机")
                                checked: window.shutdownEnabled
                                onToggled: (v) => {
                                    Backend.autoShutdown = v
                                    window.shutdownEnabled = v
                                    if (v)
                                        toast.push("info", "已开启：下载全部完成后 60 秒关机")
                                }
                            }

                            Rectangle {
                                visible: window.shutdownEnabled
                                width: cancelShutLabel.implicitWidth + 14
                                height: 26
                                radius: 8
                                color: csHover.containsMouse ? "#F8717133" : "transparent"
                                border.color: "#2A3352"
                                Text {
                                    id: cancelShutLabel
                                    anchors.centerIn: parent
                                    text: qsTr("取消关机")
                                    color: "#FBBF24"
                                    font.pixelSize: 11
                                    font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                                }
                                MouseArea {
                                    id: csHover
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        Backend.cancelAutoShutdown()
                                        window.shutdownEnabled = false
                                        Backend.autoShutdown = false
                                        shutdownToggle.checked = false
                                    }
                                }
                            }

                            Item { Layout.fillWidth: true }
                            Text {
                                visible: window.subsEnabled
                                text: qsTr("字幕语言: ") + Backend.subtitleLangs
                                color: "#4A5170"
                                font.pixelSize: 11
                                font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                            }
                        }
                    }
                }

                // Video preview card (animated in)
                GlassCard {
                    id: previewCard
                    Layout.fillWidth: true
                    Layout.preferredHeight: 140
                    visible: window.videoInfo !== null
                    opacity: window.videoInfo !== null ? 1 : 0
                    Behavior on opacity { NumberAnimation { duration: 280 } }

                    RowLayout {
                        width: parent.width
                        spacing: 16

                        // Thumbnail
                        Rectangle {
                            width: 160
                            height: 90
                            radius: 12
                            color: "#0B0D14"
                            border.color: "#2A3352"
                            clip: true

                            Image {
                                id: thumb
                                anchors.fill: parent
                                fillMode: Image.PreserveAspectCrop
                                source: (window.videoInfo && window.videoInfo.thumbnail) ? window.videoInfo.thumbnail : ""
                                opacity: status === Image.Ready ? 1 : 0
                                Behavior on opacity { NumberAnimation { duration: 280 } }
                            }

                            Text {
                                anchors.centerIn: parent
                                visible: thumb.status !== Image.Ready
                                text: "🎬"
                                font.pixelSize: 28
                                opacity: 0.5
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                Layout.fillWidth: true
                                text: (window.videoInfo && window.videoInfo.title) || ""
                                color: "#F3F5FF"
                                font.pixelSize: 16
                                font.bold: true
                                elide: Text.ElideRight
                                maximumLineCount: 2
                                wrapMode: Text.WordWrap
                                font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                            }

                            Text {
                                text: {
                                    if (!window.videoInfo) return ""
                                    var d = window.videoInfo.duration || 0
                                    var m = Math.floor(d / 60)
                                    var s = Math.floor(d % 60)
                                    return (window.videoInfo.uploader || "") + "  ·  "
                                           + m + ":" + (s < 10 ? "0" : "") + s
                                }
                                color: "#A8B0CC"
                                font.pixelSize: 13
                                font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                            }

                            Item { Layout.fillHeight: true }

                            GradientButton {
                                text: qsTr("下载此视频")
                                implicitWidth: 140
                                implicitHeight: 40
                                onClicked: {
                                    Backend.startDownload(
                                        (window.videoInfo && (window.videoInfo.webpage_url || window.videoInfo.url)) || urlField.text,
                                        "auto"
                                    )
                                }
                            }
                        }
                    }
                }

                // Queue section
                RowLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: 8
                    Text {
                        text: qsTr("下载队列")
                        color: "#F3F5FF"
                        font.pixelSize: 16
                        font.bold: true
                        font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                    }
                    Text {
                        text: {
                            var n = jobOrder.length
                            return n > 0 ? ("(" + n + ")") : ""
                        }
                        color: "#6B7394"
                        font.pixelSize: 13
                        font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        visible: jobOrder.length === 0
                        text: qsTr("暂无任务 — 解析或直接下载以开始")
                        color: "#6B7394"
                        font.pixelSize: 13
                        font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Repeater {
                        model: window.sortedIds
                        delegate: DownloadRow {
                            required property string modelData
                            Layout.fillWidth: true
                            job: window.jobs[modelData] || {}
                            onCancelRequested: (id) => Backend.cancelJob(id)
                            onOpenRequested: (path) => Backend.openFile(path)
                        }
                    }
                }

                // History section
                RowLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: 10
                    Text {
                        text: qsTr("下载历史")
                        color: "#F3F5FF"
                        font.pixelSize: 16
                        font.bold: true
                        font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                    }
                    Text {
                        visible: historyItems.length > 0
                        text: "(" + historyItems.length + ")"
                        color: "#6B7394"
                        font.pixelSize: 13
                        font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                    }
                    Item { Layout.fillWidth: true }
                    Rectangle {
                        visible: historyItems.length > 0
                        width: clearHistLabel.implicitWidth + 16
                        height: 28
                        radius: 10
                        color: clearHover.containsMouse ? "#F8717133" : "transparent"
                        border.color: "#2A3352"
                        Text {
                            id: clearHistLabel
                            anchors.centerIn: parent
                            text: qsTr("清空历史")
                            color: "#F87171"
                            font.pixelSize: 12
                            font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                        }
                        MouseArea {
                            id: clearHover
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: Backend.clearHistory()
                        }
                    }
                }

                Text {
                    visible: historyItems.length === 0
                    Layout.fillWidth: true
                    text: qsTr("暂无历史 — 完成的下载会出现在这里，可一键重新下载")
                    color: "#6B7394"
                    font.pixelSize: 13
                    font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                }

                // History list — each item is a separate, evenly spaced card
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Repeater {
                        model: window.historyItems
                        delegate: HistoryRow {
                            required property var modelData
                            required property int index
                            Layout.fillWidth: true
                            item: modelData
                            rowIndex: index
                            onOpenRequested: (path) => Backend.openFile(path)
                            onRedownloadRequested: (id) => Backend.redownloadFromHistory(id)
                            onRemoveRequested: (id) => Backend.removeHistory(id)
                        }
                    }
                }

                // Footer
                RowLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: 12
                    Layout.bottomMargin: 8
                    Text {
                        text: qsTr("仅供学习使用 · 请尊重创作者版权 · 禁止商业用途")
                        color: "#4A5170"
                        font.pixelSize: 11
                        font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: {
                            var st = Backend.ffmpegStatus()
                            return st === "ok" ? "FFmpeg ✓ 内置" : "FFmpeg 缺失"
                        }
                        color: Backend.ffmpegStatus() === "ok" ? "#34D399" : "#F87171"
                        font.pixelSize: 11
                        font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                    }
                }
            }
        }
    }

    ToastOverlay {
        id: toast
        anchors.fill: parent
    }

    // Resize handles (right / bottom / corner)
    component ResizeArea: MouseArea {
        property real minW: 880
        property real minH: 620
        property int edges: 0 // bit0 right, bit1 bottom
        hoverEnabled: true
        cursorShape: {
            if (edges === 3) Qt.SizeFDiagCursor
            else if (edges === 1) Qt.SizeHorCursor
            else if (edges === 2) Qt.SizeVerCursor
            else Qt.ArrowCursor
        }
        onPressed: {
            startX = mouseX
            startY = mouseY
            startW = window.width
            startH = window.height
        }
        property real startX: 0
        property real startY: 0
        property real startW: 0
        property real startH: 0
        onPositionChanged: (mouse) => {
            if (!pressed) return
            if (edges & 1) window.width = Math.max(minW, startW + (mouse.x - startX))
            if (edges & 2) window.height = Math.max(minH, startH + (mouse.y - startY))
        }
    }

    ResizeArea {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.rightMargin: 0
        anchors.topMargin: 40
        anchors.bottomMargin: 24
        width: 8
        edges: 1
    }
    ResizeArea {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 8
        anchors.leftMargin: 40
        anchors.rightMargin: 24
        edges: 2
    }
    ResizeArea {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: 18
        height: 18
        edges: 3
    }

    // Backend wiring
    Connections {
        target: Backend

        function onAnalyzeStarted() {
            window.analyzing = true
            toast.push("info", "正在解析视频信息…")
        }

        function onVideoInfoReady(info) {
            window.analyzing = false
            window.videoInfo = info
            toast.push("success", "解析成功：" + (info.title || ""))
        }

        function onVideoInfoFailed(message) {
            window.analyzing = false
            window.videoInfo = null
            toast.push("error", message || "解析失败")
        }

        function onJobAdded(job) {
            window.upsertJob(job)
        }

        function onJobUpdated(job) {
            window.upsertJob(job)
        }

        function onJobFinished(job) {
            window.upsertJob(job)
        }

        function onConfigChanged() {
            qualityChip.current = Backend.quality
            window.subsEnabled = Backend.downloadSubtitles
            window.shutdownEnabled = Backend.autoShutdown
            subsToggle.checked = Backend.downloadSubtitles
            shutdownToggle.checked = Backend.autoShutdown
        }

        function onHistoryChanged() {
            window.historyItems = Backend.getHistory()
        }
    }

    Component.onCompleted: {
        qualityChip.current = Backend.quality
        window.subsEnabled = Backend.downloadSubtitles
        window.shutdownEnabled = Backend.autoShutdown
        subsToggle.checked = Backend.downloadSubtitles
        shutdownToggle.checked = Backend.autoShutdown
        window.historyItems = Backend.getHistory()
    }
}

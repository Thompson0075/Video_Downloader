import QtQuick

// Floating toast notification stack.
Item {
    id: root
    property var items: []

    function push(type, message) {
        var next = items.slice()
        next.push({ type: type, message: message, key: Date.now() + Math.random() })
        items = next
        clearTimer.restart()
    }

    anchors.fill: parent

    Timer {
        id: clearTimer
        interval: 3200
        onTriggered: {
            if (root.items.length > 0) {
                var next = root.items.slice()
                next.shift()
                root.items = next
            }
            if (root.items.length > 0)
                clearTimer.restart()
        }
    }

    Column {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 24
        spacing: 10
        z: 100

        Repeater {
            model: root.items
            delegate: Rectangle {
                id: toast
                required property var modelData
                required property int index

                width: Math.min(360, root.width - 48)
                height: msg.implicitHeight + 28
                radius: 14
                color: "#161B2EEE"
                border.color: accentColor()
                border.width: 1
                opacity: 0
                scale: 0.92

                function accentColor() {
                    var t = toast.modelData.type
                    if (t === "success") return "#34D399"
                    if (t === "error") return "#F87171"
                    if (t === "warn") return "#FBBF24"
                    return "#6C8CFF"
                }

                Component.onCompleted: {
                    opacityAnim.from = 0; opacityAnim.to = 1; opacityAnim.start()
                    scaleAnim.from = 0.92; scaleAnim.to = 1; scaleAnim.start()
                }

                NumberAnimation { id: opacityAnim; target: toast; property: "opacity"; duration: 220; easing.type: Easing.OutCubic }
                NumberAnimation { id: scaleAnim; target: toast; property: "scale"; duration: 260; easing.type: Easing.OutBack }

                Rectangle {
                    width: 4
                    radius: 2
                    height: parent.height - 16
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.leftMargin: 8
                    color: toast.accentColor()
                }

                Text {
                    id: msg
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: 22
                    anchors.rightMargin: 14
                    text: toast.modelData.message
                    color: "#F3F5FF"
                    wrapMode: Text.Wrap
                    font.pixelSize: 13
                    font.family: "Segoe UI, Microsoft YaHei UI, sans-serif"
                }
            }
        }
    }

    Connections {
        target: Backend
        function onToast(type, message) {
            root.push(type, message)
        }
    }
}

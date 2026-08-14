console.log("Initializing QWebChannel...");

new QWebChannel(
    qt.webChannelTransport,
    function (channel) {

        console.log("QWebChannel connected.");

        window.examBridge =
            channel.objects.examBridge;

        console.log(
            "examBridge:",
            window.examBridge
        );
    }
);
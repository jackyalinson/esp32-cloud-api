
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

device_state = {"command": "LED_ON"}

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ESP32 Control Panel</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #101827;
            color: white;
            text-align: center;
            padding: 50px 20px;
        }
        .panel {
            max-width: 400px;
            margin: auto;
            padding: 30px;
            background: #1e293b;
            border-radius: 16px;
        }
        button {
            padding: 14px 28px;
            margin: 10px 5px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }
        .on { background: #22c55e; color: #052e16; }
        .off { background: #ef4444; color: white; }
        #status { font-size: 24px; margin: 25px 0; }
        #message { color: #cbd5e1; font-size: 14px; }
    </style>
</head>
<body>
    <div class="panel">
        <h1>ESP32 Control Panel</h1>
        <p>Cloud-connected LED controller</p>

        <div id="status">Checking status...</div>

        <button class="on" onclick="setCommand('LED_ON')">
            Turn ON
        </button>

        <button class="off" onclick="setCommand('LED_OFF')">
            Turn OFF
        </button>

        <p id="message">Connecting to API...</p>
    </div>

    <script>
        function showCommand(command) {
            document.getElementById("status").textContent =
                command === "LED_ON" ? "LED is ON 💡" :
                command === "LED_OFF" ? "LED is OFF 🌑" :
                "Unknown status";
        }

        async function getCommand() {
            try {
                const response = await fetch("/command");
                if (!response.ok) throw new Error("API error");

                const data = await response.json();
                showCommand(data.command);

                document.getElementById("message").textContent =
                    "Command received from API";
            } catch (error) {
                document.getElementById("message").textContent =
                    "Could not read command from API";
            }
        }

        async function setCommand(command) {
            const message = document.getElementById("message");
            message.textContent = "Sending command...";

            try {
                const response = await fetch("/command", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ command: command })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || "Request failed");
                }

                showCommand(data.command);
                message.textContent =
                    "Command sent: " + data.command;
            } catch (error) {
                message.textContent = "Error: " + error.message;
            }
        }

        getCommand();
    </script>
</body>
</html>
"""


@app.get("/")
def home():
    return render_template_string(PAGE)


@app.get("/command")
def get_command():
    return jsonify(device_state)


@app.post("/command")
def set_command():
    data = request.get_json(silent=True) or {}
    command = data.get("command")

    if command not in ["LED_ON", "LED_OFF"]:
        return jsonify({
            "error": "Command must be LED_ON or LED_OFF"
        }), 400

    device_state["command"] = command

    return jsonify({
        "success": True,
        "command": device_state["command"]
    })


from flask import Flask, jsonify, request, render_template_string
import time
import uuid

app = Flask(__name__)

device_state = {
    "command": "LED_OFF",
    "command_id": "initial",
    "click_time_ms": 0,
    "server_received_ms": 0
}

PAGE = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ESP32 Cloud Control</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      margin: 40px auto;
      max-width: 500px;
    }
    button {
      padding: 14px 25px;
      margin: 8px;
      font-size: 18px;
      cursor: pointer;
    }
    #status {
      margin-top: 20px;
      white-space: pre-wrap;
    }
  </style>
</head>
<body>
  <h2>ESP32 Cloud Control</h2>
  <button onclick="sendCommand('LED_ON')">Turn ON</button>
  <button onclick="sendCommand('LED_OFF')">Turn OFF</button>
  <p id="status">Ready</p>

  <script>
    async function sendCommand(command) {
      const clickTime = Date.now();
      const commandId = crypto.randomUUID();
      const status = document.getElementById("status");

      status.textContent = "Sending " + command + "...";

      try {
        const response = await fetch("/command", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            command: command,
            command_id: commandId,
            click_time_ms: clickTime
          })
        });

        const result = await response.json();
        const responseTime = Date.now() - clickTime;

        status.textContent =
          "Command: " + command +
          "\\nID: " + commandId +
          "\\nPOST round-trip: " + responseTime + " ms" +
          "\\nHTTP status: " + response.status +
          "\\nServer received: " + result.server_received_ms;
      } catch (error) {
        status.textContent = "Request failed: " + error;
      }
    }
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
    global device_state

    data = request.get_json(silent=True) or {}
    command = data.get("command")

    if command not in ["LED_ON", "LED_OFF"]:
        return jsonify({
            "error": "Command must be LED_ON or LED_OFF"
        }), 400

    received_ms = int(time.time() * 1000)

    device_state = {
        "command": command,
        "command_id": data.get("command_id", str(uuid.uuid4())),
        "click_time_ms": data.get("click_time_ms", 0),
        "server_received_ms": received_ms
    }

    return jsonify({
        "success": True,
        **device_state
    })

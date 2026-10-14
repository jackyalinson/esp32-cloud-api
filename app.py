
from flask import Flask, jsonify, request

app = Flask(__name__)

# Our current device command
device_state = {"command": "LED_ON"}


@app.get("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "ESP32 Cloud API is running"
    })


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


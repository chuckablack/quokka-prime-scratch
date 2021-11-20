from flask import Flask, request

app = Flask(__name__)

global_hosts = dict()
global_devices = dict()


@app.route("/hosts", methods=["GET", "PUT"])
def hosts():
    global global_hosts

    if request.method == "GET":
        return global_hosts

    elif request.method == "PUT":
        hostname = request.args.get("hostname")
        if not hostname:
            return "must provide hostname on PUT request", 400

        host = request.get_json()
        global_hosts[hostname] = host
        return {}, 204


@app.route("/devices", methods=["GET", "PUT"])
def devices():
    global global_devices

    if request.method == "GET":
        return global_devices

    elif request.method == "PUT":
        name = request.args.get("name")
        if not name:
            return "must provide device name on PUT request", 400

        device = request.get_json()
        global_devices[name] = device
        return {}, 204

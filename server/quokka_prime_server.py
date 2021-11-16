from flask import Flask, request

app = Flask(__name__)

global_hosts = dict()


@app.route("/hosts", methods=["GET", "POST", "PUT"])
def hosts():
    global global_hosts

    if request.method == "GET":
        return global_hosts

    elif request.method == "POST":
        global_hosts = request.get_json()
        return {}, 204

    elif request.method == "PUT":
        hostname = request.args.get("hostname")
        if not hostname:
            return "must provide hostname on PUT request", 400

        host = request.get_json()
        global_hosts[hostname] = host
        return {}, 204

import socket
import requests
import yaml
from pprint import pprint


def read_devices_yaml():

    print(
        "\n\n----- Discovery devices from inventory ---------------------"
    )

    with open("devices.yaml", "r") as yaml_in:
        yaml_devices = yaml_in.read()
        devices = yaml.safe_load(yaml_devices)

    existing_devices = get_devices()

    for device in devices:

        try:
            device["ip_address"] = socket.gethostbyname(device["hostname"])
        except (socket.error, socket.gaierror) as e:
            print(f"  !!! Error attempting to get ip address for device {device['hostname']}: {e}")
            device["ip_address"] = ""

        if device["name"] in existing_devices:
            device["availability"] = existing_devices[device["name"]]["availability"]
            device["response_time"] = existing_devices[device["name"]]["response_time"]

        else:
            device["availability"] = False
            device["response_time"] = "0.0"
            device["model"] = ""
            device["os_version"] = ""
            device["last_heard"] = ""

        update_device(device)


def get_devices():

    try:
        response = requests.get("http://localhost:5000/devices")
    except requests.exceptions.ConnectionError as e:
        print(f"!!! Exception trying to get devices via REST API: {e}")
        return {}

    if response.status_code != 200:
        print(f"!!! Failed to retrieve devices from server: {response.reason}")
        return {}

    print("Devices successfully retrieved")
    return response.json()


def update_device(device):

    try:
        response = requests.put("http://localhost:5000/devices", params={"name": device["name"]}, json=device)
    except requests.exceptions.ConnectionError as e:
        print(f"!!! Exception trying to update device {device['name']}: {e}")
        return

    if response.status_code != 204:
        print(f"!!! Attempt to update device {device['name']} failed, status: {response.status_code}")
        return

    print(f"Successfully updated device: {device['name']}")


def main():

    read_devices_yaml()

    print("\n\nDevices from quokka-prime server")
    pprint(get_devices())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting device-monitor")
        exit()

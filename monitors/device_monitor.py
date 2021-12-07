import socket
import time
from datetime import datetime
import napalm
from napalm.base.exceptions import NapalmException
import requests
import yaml
import re
import sys
from time import sleep
from pprint import pprint


def get_version(device, facts):

    if device["os"] == "iosxe":

        re_version_pattern = r"Version (.*),"
        version_match = re.search(re_version_pattern, facts["os_version"])
        if version_match:
            return version_match.group(1)
        else:
            return "--"

    return facts["os_version"]


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


def get_status(device):

    try:
        if device["os"] == "ios" or device["os"] == "iosxe":
            driver = napalm.get_network_driver("ios")
        elif device["os"] == "nxos-ssh":
            driver = napalm.get_network_driver("nxos_ssh")
        elif device["os"] == "nxos":
            driver = napalm.get_network_driver("nxos")
        else:
            driver = napalm.get_network_driver(device["os"])  # try this, it will probably fail

        napalm_device = driver(
            hostname=device["hostname"],
            username=device["username"],
            password=device["password"],
            optional_args={"port": device["ssh_port"]},
        )
        napalm_device.open()

        time_start = time.time()
        facts = napalm_device.get_facts()
        response_time = time.time() - time_start

        device["os_version"] = get_version(device, facts)
        device["model"] = facts["model"]
        device["availability"] = True
        device["response_time"] = f"{response_time:.4f}"
        device["last_heard"] = str(datetime.now())[:-3]

    except NapalmException as e:
        print(f"  !!! NAPALM exception attempting to get facts for device {device['name']}: {e}")
        device["availability"] = False

    except BaseException as e:
        print(f"  !!! Exception attempting get facts for device {device['name']}: {e}")
        device["availability"] = False

    update_device(device)


def main():

    read_devices_yaml()

    while True:

        devices = get_devices()
        pprint(devices)
        for name, device in devices.items():
            pprint(device)
            get_status(device)

        for remaining in range(60, 0, -1):
            sys.stdout.write("\r")
            sys.stdout.write(f"  Refresh: {remaining:3d} seconds remaining.")
            sys.stdout.flush()
            sleep(1)

        print("   ... pinging devices ...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting device-monitor")
        exit()

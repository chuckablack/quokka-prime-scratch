import os
import subprocess
import sys
from time import sleep

import requests
from colorama import Fore


def get_devices():

    try:
        response = requests.get("http://localhost:5000/devices")
    except requests.ConnectionError as e:
        print(f"!!! connection error from quokka-prime server: {e}")
        return {}

    if response.status_code != 200:
        print(f"!!! get_devices() failed: {response.reason}")
        return {}

    return response.json()


def print_devices(devices):

    subprocess.call("clear" if os.name == "posix" else "cls")
    print(
        "\n  __Device_Name___________   ___IP_address___  ______Model_____ "
        + " _Version_ _Avail_ __Rsp_  __Last_Heard___________\n"
    )
    for device in devices.values():

        if not device["availability"]:
            color = Fore.RED
        # elif device["name"] in previous_devices and device == previous_devices[device["name"]]:
        #     color = Fore.GREEN
        else:
            color = Fore.LIGHTGREEN_EX

        # compliance_color = get_compliance_color(device)
        # version = compliance_color + device["os_version"] + color

        if "os_version" not in device:
            device["os_version"] = ""
        version = color + device["os_version"] + color

        if "model" not in device:
            device["model"] = ""

        print(
            color
            + f"  {device['hostname'][:24]:<24}"
            + f"  {device['ip_address']:>16}"
            + f"   {device['model'][:16]:<16}"
            + f"   {version:<16}"  # Note: needs extra characters because of colors
            + f"   {str(device['availability']):>5}"
            + f"   {device['response_time']:>5}"
            + f"  {device['last_heard']:>16}"
            + Fore.WHITE
        )


def main():

    # subnet_address = "192.168.254.0/24"

    while True:

        devices = get_devices()
        print_devices(devices)

        print()
        for remaining in range(60, 0, -1):
            sys.stdout.write("\r")
            sys.stdout.write(f"  Refresh: {remaining:3d} seconds remaining.")
            sys.stdout.flush()
            sleep(1)

        print("   ... retrieving devices from quokka-prime server...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting device-display")
        exit()

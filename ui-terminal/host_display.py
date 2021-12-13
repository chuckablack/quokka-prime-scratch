import os
import subprocess
import sys
from time import sleep

import requests
from colorama import Fore


def get_hosts():

    try:
        response = requests.get("http://localhost:5000/hosts")
    except requests.ConnectionError as e:
        print(f"!!! connection error from quokka-prime server: {e}")
        return {}

    if response.status_code != 200:
        print(f"!!! get_hosts() failed: {response.reason}")
        return {}

    return response.json()


def print_hosts(hosts):

    subprocess.call("clear" if os.name == "posix" else "cls")
    print(
        "\n  __Hostname______________     ___IP_address___   ___MAC_address___   "
        + "__Avail__   __Last_Heard___________   __Rsp_Time__\n"
    )

    for host in hosts.values():

        if not host["availability"]:
            color = Fore.RED
        else:
            color = Fore.LIGHTGREEN_EX

        print(
            color +
            f"  {host['hostname'][:26]:<26}"
            + f"   {host['ip_address']:<16}"
            + f"   {host['mac_address']:>17}"
            + f"   {str(host['availability']):>7}  "
            + f"   {host['last_heard']:>16}"
            + f"   {host['response_time']:>10}"
            + Fore.WHITE
        )

    print("\n")


def main():

    # subnet_address = "192.168.254.0/24"

    while True:

        hosts = get_hosts()
        print_hosts(hosts)

        print()
        for remaining in range(10, 0, -1):
            sys.stdout.write("\r")
            sys.stdout.write(f"  Refresh: {remaining:3d} seconds remaining.")
            sys.stdout.flush()
            sleep(1)

        print("   ... retrieving hosts from quokka-prime server...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting host-display")
        exit()

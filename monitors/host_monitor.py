import sys
import subprocess

import requests
import scapy.all as scapy
import socket
from datetime import datetime
import re
from time import sleep


def discover_hosts(subnet_address):

    print(f"\n----- Discovering hosts on {subnet_address} ---------------------")
    ans, _ = scapy.arping(subnet_address)

    for res in ans.res:

        ip_addr = res[1].payload.psrc
        mac_addr = res[1].payload.hwsrc
        try:
            hostname = socket.gethostbyaddr(str(ip_addr))
        except (socket.error, socket.gaierror):
            hostname = (str(ip_addr), [], [str(ip_addr)])
        last_heard = str(datetime.now())[:-3]

        host = {
            "ip_address": ip_addr,
            "mac_address": mac_addr,
            "hostname": hostname[0],
            "last_heard": last_heard,
            "availability": True,
            "response_time": 0,
        }
        update_host(host)


def get_response_time(ping_output):

    m = re.search(r"time=([0-9]*)", ping_output)
    if m.group(1).isnumeric():
        return str(float(m.group(1))/1000)
    else:
        return 0


def ping_host(host):

    try:
        # print(f"----> Pinging host: {host['hostname']}", end="")
        ping_output = subprocess.check_output(
            ["ping", "-c3", "-n", "-i0.5", "-W2", host["ip_address"]]
        )
        host["availability"] = True
        host["response_time"] = get_response_time(str(ping_output))
        host["last_heard"] = str(datetime.now())[:-3]
        # print(f" Host ping successful: {host['hostname']}")

    except subprocess.CalledProcessError:
        # print(f" !!!  Host ping failed: {host['hostname']}")
        host["availability"] = False


def ping_hosts(hosts):

    for host in hosts.values():
        ping_host(host)
        update_host(host)


def get_hosts():

    try:
        response = requests.get("http://localhost:5000/hosts")
    except requests.exceptions.ConnectionError as e:
        print(f"!!! Exception trying to get hosts via REST API: {e}")
        return {}

    if response.status_code != 200:
        print(f"!!! Failed to retrieve hosts from server: {response.reason}")
        return {}

    print("Hosts successfully retrieved")
    return response.json()


def update_host(host):

    try:
        response = requests.put("http://localhost:5000/hosts",
                                params={"hostname": host["hostname"]},
                                json=host)
    except requests.exceptions.ConnectionError as e:
        print(f"!!! Exception trying to update host {host['hostname']}: {e}")
        return

    if response.status_code != 204:
        print(f"!!! Attempt to update host {host['hostname']} failed, status: {response.status_code}")
        return

    print(f"Successfully updated host: {host['hostname']}")


def main():

    subnet_address = "192.168.254.0/24"
    discover_hosts(subnet_address)

    while True:

        hosts = get_hosts()
        ping_hosts(hosts)

        for remaining in range(60, 0, -1):
            sys.stdout.write("\r")
            sys.stdout.write(f"  Refresh: {remaining:3d} seconds remaining.")
            sys.stdout.flush()
            sleep(1)

        print("   ... pinging hosts ...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting host-monitor")
        exit()

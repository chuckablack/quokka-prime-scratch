import socket
import yaml


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

    return {}


def update_device(device):

    print(device)


def main():

    read_devices_yaml()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting device-monitor")
        exit()

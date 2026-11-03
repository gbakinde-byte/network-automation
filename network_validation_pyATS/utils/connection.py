

def connect_all(devices, log):
    """Connect to every device. Returns the list of device names that failed."""
    failed = []
    for name, device in devices.items():
        if device.connected:
            continue
        try:
            device.connect(init_exec_commands=[], log_stdout=False)
        except Exception as exc:
            log.error(f"Failed to connect to {name}: {exc}")
            failed.append(name)
    return failed


def disconnect_all(devices, log):
    """Disconnect only from devices that are actually connected."""
    for name, device in devices.items():
        if device.connected:
            log.info(f"Disconnecting from {name}")
            device.disconnect()

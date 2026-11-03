import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyats import aetest

from utils.connection import connect_all, disconnect_all
from utils.data_loader import load_yaml_data

log = logging.getLogger(__name__)


class InterfaceValidation(aetest.Testcase):

    @aetest.setup
    def setup_test(self, testbed):
        self.devices = testbed.devices
        failed = connect_all(self.devices, log)
        if failed:
            self.failed(f"Could not connect to: {', '.join(failed)}", goto=["cleanup"])
        self.expected_data = load_yaml_data("data/interfaces.yaml")

    @aetest.test
    def test_interfaces(self):
        routers_config = self.expected_data.get("routers", {})
        test_failed = False

        for name, device in self.devices.items():
            if name not in routers_config:
                log.warning(f"No expected interface data for {name} in YAML")
                continue

            log.info(f"Validating interfaces on {name}")

            try:
                live_output = device.parse("show ip interface brief")
            except Exception as e:
                log.error(f"Failed to parse 'show ip interface brief' on {name}: {e}")
                test_failed = True
                continue

            live_interfaces = live_output.get("interface", {})

            for exp in routers_config[name].get("interfaces", []):
                intf_name = exp.get("name")
                exp_status = exp.get("status", "").lower()
                exp_protocol = exp.get("protocol", "").lower()
                exp_ip = exp.get("ip_address")

                if intf_name not in live_interfaces:
                    log.error(f"FAIL: Interface {intf_name} is missing on {name}")
                    test_failed = True
                    continue

                live = live_interfaces[intf_name]
                live_status = live.get("status", "").lower()
                live_protocol = live.get("protocol", "").lower()
                live_ip = live.get("ip_address")

                intf_ok = True

                if exp_status and live_status != exp_status:
                    log.error(f"FAIL: {name} {intf_name} status: expected '{exp_status}', got '{live_status}'")
                    intf_ok = False

                if exp_protocol and live_protocol != exp_protocol:
                    log.error(f"FAIL: {name} {intf_name} protocol: expected '{exp_protocol}', got '{live_protocol}'")
                    intf_ok = False

                if exp_ip and live_ip != exp_ip:
                    log.error(f"FAIL: {name} {intf_name} IP: expected '{exp_ip}', got '{live_ip}'")
                    intf_ok = False

                if intf_ok:
                    log.info(f"SUCCESS: {name} {intf_name} [status={live_status}, proto={live_protocol}, ip={live_ip}]")
                else:
                    test_failed = True

        if test_failed:
            self.failed("One or more interface validations failed. Check logs above for details.")
        self.passed("All interface validations passed successfully.")

    @aetest.cleanup
    def cleanup(self):
        disconnect_all(self.devices, log)


if __name__ == "__main__":
    aetest.main()

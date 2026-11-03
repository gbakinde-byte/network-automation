import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyats import aetest

from utils.connection import connect_all, disconnect_all
from utils.data_loader import load_yaml_data
from utils.parsers import parse_ping_success_rate

log = logging.getLogger(__name__)

SOURCE_INTERFACE = "Loopback0"
PING_COUNT = 5


def loopbacks_from_yaml(data):
    """{router: loopback_ip} taken from data/interfaces.yaml (single source of truth)."""
    result = {}
    for router, cfg in data.get("routers", {}).items():
        for intf in cfg.get("interfaces", []):
            if intf.get("name") == SOURCE_INTERFACE and intf.get("ip_address"):
                result[router] = intf["ip_address"]
    return result


class EndToEndReachability(aetest.Testcase):

    @aetest.setup
    def setup_test(self, testbed):
        self.devices = testbed.devices
        failed = connect_all(self.devices, log)
        if failed:
            self.failed(f"Could not connect to: {', '.join(failed)}", goto=["cleanup"])
        self.loopbacks = loopbacks_from_yaml(load_yaml_data("data/interfaces.yaml"))

    @aetest.test
    def test_loopback_reachability(self):
        failures = []

        for name, device in self.devices.items():
            if name not in self.loopbacks:
                log.warning(f"No {SOURCE_INTERFACE} defined for {name} in interfaces.yaml; skipping")
                continue

            for peer, target_ip in self.loopbacks.items():
                if peer == name:
                    continue

                log.info(f"Ping {name} ({SOURCE_INTERFACE}) -> {peer} ({target_ip})")
                try:
                    out = device.execute(
                        f"ping {target_ip} source {SOURCE_INTERFACE} repeat {PING_COUNT}",
                        timeout=60,
                    )
                except Exception as e:
                    log.error(f"FAIL: ping from {name} to {peer} could not run: {e}")
                    failures.append(f"{name}->{peer}")
                    continue

                rate = parse_ping_success_rate(out)
                if rate == 100:
                    log.info(f"SUCCESS: {name} -> {peer} ({target_ip}) 100%")
                else:
                    log.error(f"FAIL: {name} -> {peer} ({target_ip}) success rate: {rate}")
                    failures.append(f"{name}->{peer}")

        if failures:
            self.failed(f"Reachability failed for: {', '.join(failures)}")
        self.passed("All loopback reachability checks passed.")

    @aetest.cleanup
    def cleanup(self):
        disconnect_all(self.devices, log)


if __name__ == "__main__":
    aetest.main()

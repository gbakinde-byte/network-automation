import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyats import aetest

from utils.connection import connect_all, disconnect_all
from utils.data_loader import load_yaml_data
from utils.parsers import (
    normalize_area,
    parse_ospf_interface_areas,
    parse_ospf_neighbors,
    parse_ospf_router_id,
)

log = logging.getLogger(__name__)


class OSPFValidation(aetest.Testcase):

    @aetest.setup
    def setup_test(self, testbed):
        self.devices = testbed.devices
        failed = connect_all(self.devices, log)
        if failed:
            self.failed(f"Could not connect to: {', '.join(failed)}", goto=["cleanup"])
        self.expected_data = load_yaml_data("data/ospf.yaml")

    @aetest.test
    def test_ospf_validation(self):
        routers_config = self.expected_data.get("routers", {})
        test_failed = False

        for name, device in self.devices.items():
            if name not in routers_config:
                log.warning(f"No expected OSPF data found for {name} in YAML")
                continue

            log.info(f"Validating OSPF on {name}")
            cfg = routers_config[name]


            exp_router_id = cfg.get("router_id")
            if exp_router_id:
                try:
                    out = device.execute("show ip ospf | include Routing Process")
                except Exception as e:
                    log.error(f"FAIL: could not run 'show ip ospf' on {name}: {e}")
                    test_failed = True
                else:
                    live_id = parse_ospf_router_id(out)
                    if live_id == exp_router_id:
                        log.info(f"SUCCESS: {name} router ID is {live_id}")
                    else:
                        log.error(f"FAIL: {name} router ID: expected {exp_router_id}, got {live_id}")
                        test_failed = True


            exp_area = normalize_area(cfg.get("area", "0"))
            try:
                out = device.execute("show ip ospf interface brief")
            except Exception as e:
                log.error(f"FAIL: could not run 'show ip ospf interface brief' on {name}: {e}")
                test_failed = True
            else:
                areas = parse_ospf_interface_areas(out)
                if areas == {exp_area}:
                    log.info(f"SUCCESS: {name} OSPF interfaces are all in area {exp_area}")
                else:
                    log.error(f"FAIL: {name} OSPF areas: expected only {{'{exp_area}'}}, got {sorted(areas)}")
                    test_failed = True

            try:
                out = device.execute("show ip ospf neighbor")
            except Exception as e:
                log.error(f"FAIL: could not run 'show ip ospf neighbor' on {name}: {e}")
                test_failed = True
                continue

            live_neighbors = parse_ospf_neighbors(out)

            for exp_nbr in cfg.get("neighbors", []):
                exp_id = exp_nbr.get("neighbor_id")
                exp_state = exp_nbr.get("state", "full").lower()
                live_state = live_neighbors.get(exp_id)

                if live_state is None:
                    log.error(f"FAIL: {name} expected OSPF neighbor {exp_id} is MISSING")
                    test_failed = True
                elif live_state != exp_state:
                    log.error(f"FAIL: {name} neighbor {exp_id}: expected '{exp_state}', got '{live_state}'")
                    test_failed = True
                else:
                    log.info(f"SUCCESS: {name} neighbor {exp_id} is {live_state}")

        if test_failed:
            self.failed("One or more OSPF validations failed. Check logs above for details.")
        self.passed("All OSPF validations passed successfully.")

    @aetest.cleanup
    def cleanup(self):
        disconnect_all(self.devices, log)


if __name__ == "__main__":
    aetest.main()

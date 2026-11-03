import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyats import aetest
import logging
from utils.connection import connect_all, disconnect_all
from utils.data_loader import load_yaml_data

log = logging.getLogger(__name__)

class RoutingTableValidation(aetest.Testcase):

    @aetest.setup
    def setup_test(self, testbed):
        self.devices = testbed.devices
        failed = connect_all(self.devices, log)
        if failed:
            self.failed(f"Could not connect to: {', '.join(failed)}", goto=["cleanup"])
        self.expected_data = load_yaml_data('data/routes.yaml')

    @aetest.test
    def test_routing_table(self):
        routers_config = self.expected_data.get('routers', {})
        test_failed = False

        for name, device in self.devices.items():
            if name not in routers_config:
                log.warning(f"no expected routing data found for {name} in YAML")
                continue

            log.info(f"Validating routing table on {name}")
            
            try:
                live_output = device.parse('show ip route')
            except Exception as e:
                log.error(f"Failed to parse 'show ip route' on {name}: {e}")
                test_failed = True
                continue

            expected_routes = routers_config[name].get('routes', [])
            
            try:
                live_routes = {}
                vrfs = live_output.get('vrf', {})
                for vrf_name, vrf_data in vrfs.items():
                    routes_dict = vrf_data.get('address_family', {}).get('ipv4', {}).get('routes', {})
                    for prefix, route_info in routes_dict.items():
                        live_routes[prefix] = {
                            'protocol': route_info.get('source_protocol', '').lower()
                        }
            except Exception as e:
                log.error(f"Error extracting live routes dictionary structure on {name}: {e}")
                test_failed = True
                continue


            for exp_route in expected_routes:
                exp_prefix = exp_route.get('prefix')
                exp_protocol = exp_route.get('protocol', '').lower()
                
                if exp_prefix in live_routes:
                    live_protocol = live_routes[exp_prefix]['protocol']
                    if exp_protocol and exp_protocol != live_protocol:
                        log.error(f"FAIL: Route {exp_prefix} protocol mismatch on {name}: expected '{exp_protocol}', got '{live_protocol}'")
                        test_failed = True
                    else:
                        log.info(f"SUCCESS: Prefix {exp_prefix} found with protocol '{live_protocol}'.")
                else:
                    log.error(f"FAIL: Expected prefix {exp_prefix} is MISSING from {name}'s routing table.")
                    test_failed = True

        if test_failed:
            self.failed("One or more routing table validations failed. Check logs above for details.")
        self.passed("All routing table validations passed successfully.")

    @aetest.cleanup
    def cleanup(self):
        disconnect_all(self.devices, log)

if __name__ == '__main__':
    aetest.main()
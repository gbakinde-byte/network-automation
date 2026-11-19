import re

from pyats import aetest
from pyats.topology import loader

# neighbor IP -> expected remote AS, per router
EXPECTED_NEIGHBORS = {
    "R1": {"10.0.13.2": 65002, "2.2.2.2": 65001},
    "R2": {"10.0.24.2": 65003, "1.1.1.1": 65001},
    "R3": {"10.0.13.1": 65001, "10.0.34.2": 65003},
    "R4": {"10.0.24.1": 65001, "10.0.34.1": 65002},
}

# prefixes each router must learn through BGP
EXPECTED_ROUTES = {
    "R1": ["172.16.30.0/24", "172.16.40.0/24", "192.168.20.0/24"],
    "R2": ["172.16.30.0/24", "172.16.40.0/24", "192.168.10.0/24"],
    "R3": ["172.16.40.0/24", "192.168.10.0/24", "192.168.20.0/24"],
    "R4": ["172.16.30.0/24", "192.168.10.0/24", "192.168.20.0/24"],
}

SUMMARY_LINE = re.compile(
    r"^(\d+\.\d+\.\d+\.\d+)\s+4\s+(\d+)\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\S+\s+(\S+)\s*$",
    re.MULTILINE,
)


def parse_bgp_summary(output):
    """Return {neighbor_ip: (remote_as, state_or_prefix_count)}."""
    return {ip: (int(asn), state) for ip, asn, state in SUMMARY_LINE.findall(output)}


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect(self, testbed):
        """Connect to every device; a failed connection fails the run."""
        for device in testbed.devices.values():
            device.connect(log_stdout=False)


class BGPValidation(aetest.Testcase):
    @aetest.test
    def neighbors_established(self, testbed):
        problems = []
        for name, expected in EXPECTED_NEIGHBORS.items():
            found = parse_bgp_summary(testbed.devices[name].execute("show ip bgp summary"))
            for ip, asn in expected.items():
                if ip not in found:
                    problems.append(f"{name}: neighbor {ip} not found")
                    continue
                remote_as, state = found[ip]
                if remote_as != asn:
                    problems.append(f"{name}: {ip} is AS {remote_as}, expected {asn}")
                if not state.isdigit(): 
                    problems.append(f"{name}: {ip} is not Established (state: {state})")
        if problems:
            self.failed("\n".join(problems))

    @aetest.test
    def routes_learned(self, testbed):
        problems = []
        for name, prefixes in EXPECTED_ROUTES.items():
            output = testbed.devices[name]
            parsed = output.parse("show ip bgp")
            learned = set()
            for vrf in parsed.get("vrf", {}).values():
                for af in vrf.get("address_family", {}).values():
                    learned.update(af.get("routes", {}).keys())

            for prefix in prefixes:
                base_ip = prefix.split("/")[0]
                if prefix not in learned and base_ip not in learned:
                    problems.append(f"{name}: missing BGP route {prefix}")
        if problems:
            self.failed("\n".join(problems))


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect(self, testbed):
        for device in testbed.devices.values():
                device.disconnect()


if __name__ == "__main__":
    aetest.main(testbed=loader.load("testbed.yaml"))

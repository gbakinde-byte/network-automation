# Network Validation with pyATS

Automated validation of a small GNS3/VMware OSPF lab (R1, R2, R3) using pyATS/Genie.
Expected state lives in YAML files; each test compares it against the live devices.

## What it checks

| Test | Layer | Expected data |
|------|-------|---------------|
| `test_connectivity.py` | SSH access to every device | `testbed/testbed.yaml` |
| `test_interfaces.py` | Interface status, protocol, IP | `data/interfaces.yaml` |
| `test_ospf.py` | Router ID, area, per-neighbor state | `data/ospf.yaml` |
| `test_routing.py` | Expected prefixes in the routing table | `data/routes.yaml` |
| `test_reachability.py` | Loopback-to-loopback pings (sourced from Loopback0, so return paths are tested too) | `data/interfaces.yaml` |

`scripts/generate_docs.py` builds a Markdown interface table per device in `docs/`.

## Layout

```
data/          expected state (YAML)
testbed/       pyATS testbed (credentials via environment variables)
tests/         aetest test scripts
jobs/          easypy job that runs the suite
scripts/       documentation generator
utils/         YAML loader, connection helpers, output parsers, structure inspector
unit_tests/    offline tests for the parsers (no routers needed)
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYATS_USER=<username>
export PYATS_PASS=<password>
```

Edit the management IPs in `testbed/testbed.yaml` to match your lab.

## Run

```bash
# whole suite, in order
pyats run job jobs/validation_job.py --testbed-file testbed/testbed.yaml

# only some tests
VALIDATION_TESTS=ospf,reachability pyats run job jobs/validation_job.py --testbed-file testbed/testbed.yaml

# generate docs/<device>.md
python scripts/generate_docs.py

# offline parser tests
pytest unit_tests
```

## Notes

- Tests fail loudly: a command that can't run or can't be parsed is a FAIL, never a silent skip.
- OSPF neighbor state is checked per neighbor, not by searching the whole command output.

"""Offline tests for utils/parsers.py -- no routers needed.  Run: pytest unit_tests"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.parsers import (
    normalize_area,
    parse_ospf_interface_areas,
    parse_ospf_neighbors,
    parse_ospf_router_id,
    parse_ping_success_rate,
)

NEIGHBORS_OK = """Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           1   FULL/DR         00:00:35    10.10.10.2      GigabitEthernet0/0
3.3.3.3           1   FULL/  -        00:00:31    10.10.10.6      GigabitEthernet0/1
"""

NEIGHBORS_ONE_BAD = """Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           1   FULL/DR         00:00:35    10.10.10.2      GigabitEthernet0/0
3.3.3.3           1   INIT/DROTHER    00:00:31    10.10.10.6      GigabitEthernet0/1
"""


def test_neighbors_all_full():
    assert parse_ospf_neighbors(NEIGHBORS_OK) == {"2.2.2.2": "full", "3.3.3.3": "full"}


def test_one_bad_neighbor_is_not_masked_by_a_good_one():
    assert parse_ospf_neighbors(NEIGHBORS_ONE_BAD)["3.3.3.3"] == "init"


def test_neighbor_id_is_not_a_substring_match():
    out = "11.1.1.1  1  FULL/DR  00:00:35  10.0.0.2  Gi0/0\n"
    assert "1.1.1.1" not in parse_ospf_neighbors(out)


def test_no_neighbors():
    assert parse_ospf_neighbors("") == {}


def test_router_id():
    assert parse_ospf_router_id(' Routing Process "ospf 1" with ID 1.1.1.1') == "1.1.1.1"
    assert parse_ospf_router_id("") is None


def test_areas():
    out = """Interface    PID   Area            IP Address/Mask    Cost  State Nbrs F/C
Lo0          1     0               192.168.80.35/32   1     LOOP  0/0
Gi0/0        1     0               10.10.10.1/30      1     DR    1/1
Gi0/1        1     0.0.0.5         10.10.10.5/30      1     DR    1/1
"""
    assert parse_ospf_interface_areas(out) == {"0", "5"}


def test_normalize_area():
    assert normalize_area("0") == "0"
    assert normalize_area("0.0.0.0") == "0"
    assert normalize_area(0) == "0"


def test_ping():
    assert parse_ping_success_rate("Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms") == 100
    assert parse_ping_success_rate("Success rate is 0 percent (0/5)") == 0
    assert parse_ping_success_rate("% Invalid input") is None

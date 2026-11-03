"""Pure parsing helpers (no device access) so they can be unit-tested offline."""
import re

_NEIGHBOR_RE = re.compile(r"^(\d+\.\d+\.\d+\.\d+)\s+\d+\s+(\w+)/", re.M)
_ROUTER_ID_RE = re.compile(r'Routing Process\s+"ospf\s+\d+"\s+with ID\s+(\d+\.\d+\.\d+\.\d+)')
_OSPF_INTF_AREA_RE = re.compile(
    r"^\S+\s+\d+\s+(\d+(?:\.\d+\.\d+\.\d+)?)\s+\d+\.\d+\.\d+\.\d+/\d+", re.M
)
_PING_RE = re.compile(r"Success rate is (\d+) percent")


def parse_ospf_neighbors(output):
    """'show ip ospf neighbor' -> {neighbor_id: state} (state lower-case, e.g. 'full')."""
    return {m.group(1): m.group(2).lower() for m in _NEIGHBOR_RE.finditer(output)}


def parse_ospf_router_id(output):
    """'show ip ospf | include Routing Process' -> router id string or None."""
    match = _ROUTER_ID_RE.search(output)
    return match.group(1) if match else None


def normalize_area(area):
    """'0' and '0.0.0.0' both -> '0'; '0.0.0.5' -> '5'."""
    area = str(area)
    if "." in area:
        a, b, c, d = (int(x) for x in area.split("."))
        return str((a << 24) + (b << 16) + (c << 8) + d)
    return area


def parse_ospf_interface_areas(output):
    """'show ip ospf interface brief' -> set of normalized area numbers."""
    return {normalize_area(m.group(1)) for m in _OSPF_INTF_AREA_RE.finditer(output)}


def parse_ping_success_rate(output):
    """Ping output -> success rate as int, or None if it can't be found."""
    match = _PING_RE.search(output)
    return int(match.group(1)) if match else None

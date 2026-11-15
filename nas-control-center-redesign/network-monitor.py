#!/usr/bin/env python3
"""Write a small, read-only network status snapshot for NAS Control Center."""
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

OUTPUT = Path("/srv/nas/websites/vukyweb/nas/data/network.json")
WIFI_INTERFACE = "wlxb4b024d5369f"
ETHERNET_INTERFACE = "enp0s25"


def command(args, timeout=4):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return result.stdout.strip() if result.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def read_interface():
    raw = command(["ip", "-j", "addr", "show"])
    try:
        interfaces = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        interfaces = []
    selected = next((item for item in interfaces if item.get("ifname") == WIFI_INTERFACE), None)
    if selected is None:
        selected = next((item for item in interfaces if item.get("ifname") not in ("lo", "docker0") and not item.get("ifname", "").startswith(("br-", "veth", "tailscale")) and any(a.get("family") == "inet" for a in item.get("addr_info", []))), None)
    if not selected:
        return {"name": WIFI_INTERFACE, "type": "Wi-Fi", "state": "down", "ipv4": None, "connection": "No active local interface found"}
    ipv4 = next((a.get("local") for a in selected.get("addr_info", []) if a.get("family") == "inet"), None)
    name = selected.get("ifname", WIFI_INTERFACE)
    is_wifi = name.startswith(("wl", "wlan"))
    connection = command(["nmcli", "-t", "-f", "GENERAL.CONNECTION", "device", "show", name])
    connection = connection.split(":", 1)[-1] if connection else ("Wi-Fi" if is_wifi else "Wired")
    return {
        "name": name,
        "type": "Wi-Fi" if is_wifi else "Ethernet",
        "state": "up" if selected.get("operstate") == "UP" and ipv4 else "down",
        "ipv4": ipv4,
        "connection": connection or ("Wi-Fi" if is_wifi else "Ethernet"),
    }


def read_wifi():
    link = command(["iw", "dev", WIFI_INTERFACE, "link"])
    ssid_match = re.search(r"^\s*SSID:\s*(.+)$", link, re.MULTILINE)
    signal_match = re.search(r"^\s*signal:\s*(-?\d+)\s*dBm", link, re.MULTILINE)
    signal = None
    if signal_match:
        dbm = int(signal_match.group(1))
        signal = max(0, min(100, round(2 * (dbm + 100))))
    return {"ssid": ssid_match.group(1).strip() if ssid_match else None, "signal_percent": signal}


def read_gateway():
    raw = command(["ip", "-j", "route", "show", "default"])
    try:
        routes = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        routes = []
    route = next((r for r in routes if r.get("dev") != "tailscale0"), routes[0] if routes else {})
    address = route.get("gateway")
    reachable = None
    if address:
        reachable = bool(command(["ping", "-n", "-c", "1", "-W", "2", address], timeout=3))
    return {"address": address, "interface": route.get("dev"), "reachable": reachable}


def read_tailscale():
    raw = command(["tailscale", "status", "--json"], timeout=5)
    try:
        status = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {"connected": None, "ipv4": None, "dns_name": None, "state": "unavailable"}
    self_info = status.get("Self") or {}
    ips = self_info.get("TailscaleIPs") or []
    dns_name = (self_info.get("DNSName") or "").rstrip(".") or None
    state = status.get("BackendState", "unknown")
    return {
        "connected": state == "Running",
        "ipv4": next((ip for ip in ips if "." in ip), None),
        "dns_name": dns_name,
        "state": state,
    }


def read_internet():
    try:
        request = Request("https://connectivitycheck.gstatic.com/generate_204", headers={"User-Agent": "NAS-Control-Center/3"})
        with urlopen(request, timeout=4) as response:
            return {"reachable": response.status in (200, 204), "detail": "External HTTPS check succeeded"}
    except Exception as exc:
        return {"reachable": False, "detail": "External HTTPS check failed: " + type(exc).__name__}


def main():
    interface = read_interface()
    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "interface": interface,
        "wifi": read_wifi() if interface.get("type") == "Wi-Fi" else {"ssid": None, "signal_percent": None},
        "gateway": read_gateway(),
        "internet": read_internet(),
        "tailscale": read_tailscale(),
        "ethernet": {"name": ETHERNET_INTERFACE, "expected_state": "disabled"},
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="network.", suffix=".json", dir=str(OUTPUT.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
        os.chmod(temporary, 0o644)
        os.replace(temporary, OUTPUT)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


if __name__ == "__main__":
    main()

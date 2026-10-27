from __future__ import annotations

import os

AGENT_HOST = "127.0.0.1"
# ROTUNDA_AGENT_PORT_BASE / ROTUNDA_AGENT_PORT_COUNT move the port range a daemon is found in,
# so agents with separate ROTUNDA_AGENT_HOME folders never scan each other's daemon.
AGENT_PORT_BASE = int(os.environ.get("ROTUNDA_AGENT_PORT_BASE") or 51240)
AGENT_PORT_COUNT = int(os.environ.get("ROTUNDA_AGENT_PORT_COUNT") or 32)
AGENT_IDENTITY_SERVICE = "rotunda-agent"
HEARTBEAT_INTERVAL_SECONDS = 5.0


def agent_ports(port_base: int = AGENT_PORT_BASE, port_count: int = AGENT_PORT_COUNT) -> range:
    return range(port_base, port_base + port_count)

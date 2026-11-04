"""Pydantic models describing parsed network data."""

from __future__ import annotations

import ipaddress
from typing import Literal

from pydantic import BaseModel, Field, field_validator

InterfaceStatus = Literal["up", "down", "administratively down"]
LineProtocol = Literal["up", "down"]
BgpState = Literal["Idle", "Connect", "Active", "OpenSent", "OpenConfirm", "Established"]

MAX_ASN = 4294967295  # largest 32-bit autonomous system number


class Interface(BaseModel):
    """One interface, as returned by parse_interfaces()."""

    status: InterfaceStatus
    protocol: LineProtocol
    description: str | None = None
    mtu: int = Field(gt=0)
    bandwidth_kbit: int = Field(gt=0)
    input_errors: int = Field(ge=0)
    delay: int = Field(ge=0)


class BgpNeighbor(BaseModel):
    """One BGP neighbor, as shown in a 'show ip bgp summary' style table."""

    neighbor_ip: str
    remote_as: int = Field(ge=1, le=MAX_ASN)
    state: BgpState
    uptime: str | None = None
    prefixes_received: int | None = Field(default=None, ge=0)

    @field_validator("neighbor_ip")
    @classmethod
    def must_be_ip_address(cls, v: str) -> str:
        try:
            ipaddress.ip_address(v)
        except ValueError as exc:
            raise ValueError(f"{v!r} is not a valid IP address") from exc
        return v

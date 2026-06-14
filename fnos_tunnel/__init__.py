"""
fnOS Cloudflare Tunnel SDK for Python.

Provides typed clients for both the CGI interface (fnOS gateway proxy) and
the independent HTTP API (port 19092).

Usage (CGI, no auth)::

    from fnos_tunnel import TunnelCGIClient

    client = TunnelCGIClient("http://192.168.1.100")
    print(client.status())

Usage (HTTP API, with auth)::

    from fnos_tunnel import TunnelAPIClient

    client = TunnelAPIClient("http://192.168.1.100:19092", app_id="...", app_key="...")
    print(client.health())
"""

from .client import TunnelCGIClient, TunnelAPIClient
from .models import (
    TunnelStatus,
    DomainRegistration,
    DomainStatusResult,
    CGIRegisterResult,
    APIError,
)

__version__ = "1.0.0"
__all__ = [
    "TunnelCGIClient",
    "TunnelAPIClient",
    "TunnelStatus",
    "DomainRegistration",
    "DomainStatusResult",
    "CGIRegisterResult",
    "APIError",
]
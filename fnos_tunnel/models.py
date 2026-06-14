"""Data models for the fnOS Cloudflare Tunnel SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class TunnelStatus:
    """Tunnel 运行状态"""

    running: bool
    """Tunnel 进程是否正在运行"""
    status: str
    """健康状态: ``healthy`` / ``down``"""
    pid: Optional[str] = None
    """进程 PID"""
    arch: Optional[str] = None
    """设备架构: ``amd64`` / ``arm64``"""
    start_at: Optional[int] = None
    """启动时间戳（秒）"""
    tunnel_id: Optional[str] = None
    """当前运行的 Tunnel ID"""


@dataclass
class DomainRegistration:
    """域名注册信息"""

    app_name: str
    """应用唯一标识"""
    domain: str
    """完整域名"""
    service: str
    """本地服务地址"""

    def to_dict(self) -> dict:
        return {
            "appName": self.app_name,
            "domain": self.domain,
            "service": self.service,
        }


@dataclass
class DomainStatusResult:
    """域名注册状态查询结果"""

    registered: bool
    """是否已注册"""
    app_name: str
    """应用名称"""
    domain: Optional[str] = None
    """注册的域名"""
    service: Optional[str] = None
    """注册的本地服务地址"""
    dns_valid: Optional[bool] = None
    """DNS CNAME 记录是否有效"""
    ingress_valid: Optional[bool] = None
    """ingress 规则是否仍在配置中"""
    tunnel_running: bool = False
    """Tunnel 进程是否运行中"""
    cf_configured: bool = False
    """Cloudflare 账号是否已配置"""
    message: Optional[str] = None
    """附加消息"""


@dataclass
class CGIRegisterResult:
    """CGI 域名注册结果"""

    success: bool
    """是否成功"""
    tunnel_id: Optional[str] = None
    """Tunnel ID"""
    errors: list[str] = field(default_factory=list)
    """错误列表"""
    messages: list[str] = field(default_factory=list)
    """消息列表"""
    raw_config: Optional[dict] = None
    """Cloudflare 返回的原始 ingress 配置"""


@dataclass
class APIError(Exception):
    """API 错误"""

    success: bool = False
    message: str = ""
    raw: Optional[dict] = None

    def __str__(self) -> str:
        return self.message or "Unknown API error"
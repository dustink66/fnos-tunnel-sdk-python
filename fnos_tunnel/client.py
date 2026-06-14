"""Client implementations for the fnOS Cloudflare Tunnel API."""

from __future__ import annotations

import json
from typing import Any, Optional
from urllib.parse import urljoin, urlencode

import requests

from .models import TunnelStatus, DomainRegistration, DomainStatusResult, CGIRegisterResult, APIError

__all__ = ["TunnelCGIClient", "TunnelAPIClient"]


class TunnelCGIClient:
    """CGI 接口客户端（通过 fnOS 网关代理，无需认证）。

    :param base_url: fnOS 设备地址，如 ``http://192.168.1.100``
    :param timeout: 请求超时秒数，默认 10
    """

    _PATH = "/cgi/ThirdParty/com.dustinky.tunnel/api.cgi"

    def __init__(self, base_url: str, timeout: float = 10.0):
        self._base = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()

    # -----------------------------------------------------------------
    # 1. 查询 Tunnel 运行状态
    # -----------------------------------------------------------------

    def status(self) -> TunnelStatus:
        """查询 Tunnel 运行状态。

        :raises APIError: 请求失败时抛出
        """
        data = self._get("status")
        return TunnelStatus(
            running=data.get("running", False),
            status=data.get("status", "down"),
            pid=data.get("pid"),
            arch=data.get("arch"),
            start_at=data.get("startAt"),
            tunnel_id=data.get("tunnelId"),
        )

    # -----------------------------------------------------------------
    # 2. 注册/更新域名
    # -----------------------------------------------------------------

    def register_app_domain(
        self,
        app_name: str,
        domain: str,
        service: str,
    ) -> CGIRegisterResult:
        """注册或更新应用的域名转发规则。

        :param app_name: 应用唯一标识（如 ``com.dustinky.qwenpaw``）
        :param domain: 完整域名（如 ``qwenpaw.example.com``）
        :param service: 本地服务地址（如 ``http://localhost:19091``）
        :raises APIError: 请求失败时抛出
        """
        body = {
            "appName": app_name,
            "domain": domain,
            "service": service,
        }
        data = self._post("register_app_domain", body)
        return CGIRegisterResult(
            success=data.get("success", False),
            tunnel_id=data.get("result", {}).get("tunnel_id") if data.get("result") else None,
            errors=data.get("errors", []),
            messages=data.get("messages", []),
            raw_config=data.get("result", {}).get("config") if data.get("result") else None,
        )

    # -----------------------------------------------------------------
    # 3. 查询应用域名注册状态
    # -----------------------------------------------------------------

    def get_app_domain_status(self, app_name: str) -> DomainStatusResult:
        """查询应用的域名注册状态。

        :param app_name: 应用唯一标识
        :raises APIError: 请求失败时抛出
        """
        data = self._get("get_app_domain_status", params={"appName": app_name})
        return DomainStatusResult(
            registered=data.get("registered", False),
            app_name=data.get("appName", app_name),
            domain=data.get("domain"),
            service=data.get("service"),
            dns_valid=data.get("dnsValid"),
            ingress_valid=data.get("ingressValid"),
            tunnel_running=data.get("tunnelRunning", False),
            cf_configured=data.get("cfConfigured", False),
            message=data.get("message"),
        )

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    def _get(self, action: str, params: Optional[dict] = None) -> dict:
        p = dict(params or {})
        p["action"] = action
        url = f"{self._base}{self._PATH}?{urlencode(p)}"
        resp = self._session.get(url, timeout=self._timeout)
        return self._handle(resp)

    def _post(self, action: str, body: dict) -> dict:
        url = f"{self._base}{self._PATH}?{urlencode({'action': action})}"
        resp = self._session.post(url, json=body, timeout=self._timeout)
        return self._handle(resp)

    @staticmethod
    def _handle(resp: requests.Response) -> dict:
        try:
            data = resp.json()
        except json.JSONDecodeError:
            raise APIError(success=False, message=f"Invalid JSON response: {resp.text[:200]}")
        if not isinstance(data, dict):
            raise APIError(success=False, message="Unexpected response format")
        if not data.get("success", True):
            raise APIError(success=False, message=data.get("message", "Unknown error"), raw=data)
        return data


class TunnelAPIClient:
    """独立 HTTP API 客户端（端口 19092，需认证）。

    :param base_url: 完整地址，如 ``http://192.168.1.100:19092``
    :param app_id: API 凭证的 appId
    :param app_key: API 凭证的 appKey
    :param app_name: 应用名称（如 ``com.dustinky.qwenpaw``），注册域名时使用
    :param timeout: 请求超时秒数，默认 10
    """

    def __init__(self, base_url: str, app_id: str, app_key: str, app_name: str = "", timeout: float = 10.0):
        self._base = base_url.rstrip("/")
        self._app_id = app_id
        self._app_key = app_key
        self._app_name = app_name
        self._timeout = timeout
        self._session = requests.Session()

    @property
    def _headers(self) -> dict:
        return {"X-App-Id": self._app_id, "X-App-Key": self._app_key}

    # -----------------------------------------------------------------
    # 1. 健康检查
    # -----------------------------------------------------------------

    def health(self) -> bool:
        """健康检查（无需认证）。

        :returns: 服务是否在线
        """
        url = self._url("/api/health")
        try:
            resp = self._session.get(url, timeout=self._timeout)
            data = resp.json()
            return data.get("success", False)
        except Exception:
            return False

    # -----------------------------------------------------------------
    # 2. 查询 Tunnel 运行状态
    # -----------------------------------------------------------------

    def status(self) -> TunnelStatus:
        """查询 Tunnel 运行状态（需认证）。

        :raises APIError: 请求失败或认证失败时抛出
        """
        data = self._get("/api/status")
        return TunnelStatus(
            running=data.get("running", False),
            status=data.get("status", "down"),
            pid=data.get("pid"),
            arch=data.get("arch"),
            start_at=data.get("startAt"),
            tunnel_id=data.get("tunnelId"),
        )

    # -----------------------------------------------------------------
    # 3. 注册/更新域名
    # -----------------------------------------------------------------

    def register(self, domain: str, service: str, app_name: str = "") -> CGIRegisterResult:
        """注册或更新域名转发规则。

        :param domain: 完整域名
        :param service: 本地服务地址
        :param app_name: 应用名称，不传则使用创建客户端时传入的 app_name
        :raises APIError: 请求失败时抛出
        """
        body = {
            "appName": app_name or self._app_name,
            "domain": domain,
            "service": service,
        }
        data = self._post("/api/register", body)
        return CGIRegisterResult(
            success=data.get("success", False),
            tunnel_id=data.get("result", {}).get("tunnel_id") if data.get("result") else None,
            errors=data.get("errors", []),
            messages=data.get("messages", []),
            raw_config=data.get("result", {}).get("config") if data.get("result") else None,
        )

    # -----------------------------------------------------------------
    # 4. 查询域名注册状态
    # -----------------------------------------------------------------

    def domain_status(self, app_name: Optional[str] = None) -> DomainStatusResult:
        """查询域名注册状态。

        ``app_name`` 不传时自动使用凭证绑定的 appName。

        :param app_name: 应用唯一标识（可选）
        :raises APIError: 请求失败时抛出
        """
        params = {}
        if app_name:
            params["appName"] = app_name
        data = self._get("/api/domain-status", params=params)
        return DomainStatusResult(
            registered=data.get("registered", False),
            app_name=data.get("appName", app_name or ""),
            domain=data.get("domain"),
            service=data.get("service"),
            dns_valid=data.get("dnsValid"),
            ingress_valid=data.get("ingressValid"),
            tunnel_running=data.get("tunnelRunning", False),
            cf_configured=data.get("cfConfigured", False),
            message=data.get("message"),
        )

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self._base}{path}"

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        url = self._url(path)
        if params:
            url = f"{url}?{urlencode(params)}"
        resp = self._session.get(url, headers=self._headers, timeout=self._timeout)
        return self._handle(resp)

    def _post(self, path: str, body: dict) -> dict:
        resp = self._session.post(
            self._url(path),
            json=body,
            headers=self._headers,
            timeout=self._timeout,
        )
        return self._handle(resp)

    @staticmethod
    def _handle(resp: requests.Response) -> dict:
        try:
            data = resp.json()
        except json.JSONDecodeError:
            raise APIError(success=False, message=f"Invalid JSON response: {resp.text[:200]}")
        if not isinstance(data, dict):
            raise APIError(success=False, message="Unexpected response format")
        if not data.get("success", True):
            raise APIError(success=False, message=data.get("message", "Unknown error"), raw=data)
        return data
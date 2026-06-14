# fnos-tunnel (Python)

fnOS Cloudflare Tunnel SDK for Python — 将 Tunnel 管理能力集成到你的 Python 应用中。

## 安装

```bash
pip install fnos-tunnel
```

或从源码安装：

```bash
pip install git+https://github.com/dustink66/fnos-tunnel-sdk-python.git
```

## 快速开始

```python
from fnos_tunnel import TunnelAPIClient

client = TunnelAPIClient(
    "http://<your-fnos-ip>:19092",
    app_id="<your_app_id>",
    app_key="<your_app_key>",
    app_name="com.example.myapp",
)

# 健康检查
print(client.health())  # True

# 查询 Tunnel 状态
status = client.status()
print(f"Running: {status.running}, PID: {status.pid}")

# 查询域名状态
ds = client.domain_status()
print(f"Registered: {ds.registered}")

# 注册域名
result = client.register("myapp.example.com", "http://localhost:8080")
print(f"Success: {result.success}")
```

## API

| 方法 | 说明 |
|------|------|
| `health()` | 健康检查，无需认证 |
| `status()` | 查询 Tunnel 运行状态 |
| `domain_status(app_name?)` | 查询域名注册状态 |
| `register(domain, service, app_name?)` | 注册/更新域名转发规则 |

## 发布到 PyPI

```bash
pip install build twine
python -m build
twine upload dist/*
```
get_router_info
================

SDK Application that proxies any HTTP GET path to `cp.get()` and returns the result as JSON.

Lets networked devices query arbitrary router state or config without NCM access.

## Usage

```python
import requests

# Get WAN device status
r = requests.get('http://<router_ip>:8002/status/wan/devices')

# Get routing config
r = requests.get('http://<router_ip>:8002/config/routing/rules')

# Get ECM status
r = requests.get('http://<router_ip>:8002/status/ecm')
```

## Endpoints

- `GET /<any_cp_path>` - Runs `cp.get('<any_cp_path>')` and returns the result as JSON

Returns 400 if no path is provided, 404 if `cp.get()` returns None.

## Access

Use Remote Connect LAN Manager to connect to 127.0.0.1 port 8002 HTTP.
Or forward the LAN zone to the ROUTER zone for local access on `http://{ROUTER IP}:8002`.

## Configuration

Port can be overridden via SDK appdata field `get_router_info_port`.

modem_info
==========

SDK Application that serves modem identity, signal quality, and network info as JSON over HTTP.

Designed for locally connected devices (e.g. IoT controllers, PLCs, embedded systems) that need
visibility into modem state without NCM access.

## Data Returned

- **Identity:** IMEI, Manufacturer, Model, Carrier, SIM slot
- **SIM:** ICCID, IMSI, APN, Phone Number (MDN)
- **Network:** Connection state, IPv4/IPv6 address, Roaming status
- **Signal:** dBm, RSRP, RSRQ, SINR, RSSI, RF Band, RF Channel, Cell ID, LAC
- **Traffic:** Bytes received, Bytes transmitted
- **Hardware:** Modem temperature

## Endpoints

- `GET /` - All modems, keyed by device ID
- `GET /{device_id}` - Single modem (e.g. `GET /mdm-db6f5e0`)

Returns 404 with a list of available device IDs if the requested device is not found.

## Access

Use Remote Connect LAN Manager to connect to 127.0.0.1 port 8001 HTTP.
Or forward the LAN zone to the ROUTER zone for local access on `http://{ROUTER IP}:8001`.

## Configuration

Port can be overridden via SDK appdata field `modem_info_port`.

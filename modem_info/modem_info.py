"""modem_info - Serves modem identity, signal, and network data as JSON over HTTP.

Exposes a lightweight API on port 8001 so that locally connected devices can
query modem identity (IMEI, ICCID, IMSI), network state (IP, APN, roaming),
signal quality (RSRP, SINR, band, cell), and traffic counters.

Endpoints:
  GET /             - JSON object with all modems keyed by device ID
  GET /{device_id}  - JSON object for a single modem

Use Remote Connect LAN Manager to connect to 127.0.0.1 port 8001 HTTP.
Or forward the LAN zone to the ROUTER zone for local access on http://{ROUTER IP}:8001.
"""

import cp
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

DEFAULT_PORT = 8001


def get_modem_data():
    """Return a dict of modem device_id -> extracted metrics for every WAN modem."""
    devices = cp.get('status/wan/devices')
    if not devices or not isinstance(devices, dict):
        return {}

    modems = {}
    for device_id, device in devices.items():
        info = device.get('info', {})
        if info.get('type') != 'mdm':
            continue

        diagnostics = device.get('diagnostics', {})
        status = device.get('status', {})
        ipinfo = status.get('ipinfo', {})
        ip6info = status.get('ip6info', {})
        stats = device.get('stats', {})

        modems[device_id] = {
            # Identity & Hardware
            'IMEI': info.get('serial'),
            'Manufacturer': info.get('manufacturer'),
            'Model': info.get('model'),
            'Carrier': info.get('carrier_id'),
            'Active_SIM_Slot': info.get('sim'),
            'Modem_Temperature_C': diagnostics.get('TEMPERATURE'),

            # SIM & Auth
            'ICCID': diagnostics.get('ICCID'),
            'IMSI': diagnostics.get('IMSI'),
            'Active_APN': diagnostics.get('APN'),
            'Phone_Number': diagnostics.get('MDN'),

            # Network State
            'Connection_State': status.get('connection_state'),
            'IPv4_Address': ipinfo.get('ip_address'),
            'IPv4_Gateway': ipinfo.get('gateway'),
            'IPv4_Netmask': ipinfo.get('netmask'),
            'DNS': ipinfo.get('dns'),
            'IPv6_Address': ip6info.get('ip_address'),
            'Roaming': diagnostics.get('ROAM'),
            'Signal_Strength_Percent': status.get('signal_strength'),
            'Cellular_Health_Score': status.get('cellular_health_score'),
            'Cellular_Health_Category': status.get('cellular_health_category'),

            # Signal Quality & Tower
            'Signal_Strength_dBm': diagnostics.get('DBM'),
            'RSRP': diagnostics.get('RSRP'),
            'RSRQ': diagnostics.get('RSRQ'),
            'SINR': diagnostics.get('SINR'),
            'RSSI': diagnostics.get('RSSI'),
            'RF_Band': diagnostics.get('RF_BAND'),
            'RF_Channel': diagnostics.get('RF_CHANNEL'),
            'Cell_ID': diagnostics.get('CELL_ID'),
            'LAC': diagnostics.get('LAC'),

            # Traffic
            'Bytes_Received': stats.get('rx_bytes'),
            'Bytes_Transmitted': stats.get('tx_bytes'),
        }

    return modems


class ModemInfoHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = self.path.strip('/')

        modems = get_modem_data()

        if path == '':
            payload = modems
        elif path in modems:
            payload = modems[path]
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'device not found',
                'available_devices': list(modems.keys())
            }).encode())
            return

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload, indent=2).encode())

    def log_message(self, format, *args):
        cp.log(f'HTTP {args[0]}')


def main():
    port = DEFAULT_PORT
    appdata_port = cp.get_appdata('modem_info_port')
    if appdata_port:
        try:
            port = int(appdata_port)
        except (ValueError, TypeError):
            cp.log(f'Invalid modem_info_port appdata value "{appdata_port}", using default {DEFAULT_PORT}')
            port = DEFAULT_PORT

    cp.log(f'Starting modem_info server on port {port}')
    server = HTTPServer(('', port), ModemInfoHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        cp.log('Stopping modem_info server')


if __name__ == '__main__':
    main()

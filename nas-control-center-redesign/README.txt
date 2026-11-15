NAS CONTROL CENTER · V3.0
==========================

A responsive, multi-page dashboard for your home NAS. Near-black surfaces,
white typography, flat line icons and restrained status colours.

PAGES
-----
index.html       Overview, live host metrics, network health and Docker status
services.html    Local, Tailscale and public service links
network.html     Live interface, Wi-Fi, gateway, internet and Tailscale status
ports.html       Port reference and exposure guidance
css/style.css    Shared responsive design system
js/app.js        Live JSON polling, status rendering and copy controls

LIVE DATA
---------
The browser reads JSON snapshots from the protected dashboard data directory:

  data/stats.json      CPU, memory, storage, uptime and hostname
  data/docker.json     Docker container list and health
  data/network.json    Active interface, Wi-Fi signal, gateway, internet and Tailscale

Keep the existing nas-monitor and nas-docker-monitor scripts and timers enabled.
This release adds an optional network monitor described below.

NETWORK MONITOR INSTALLATION
----------------------------
The included network-monitor.py runs as the unprivileged user "vuky". It reads
network state using ip, nmcli, iw, ping and tailscale, then writes one JSON file.
It does not change network configuration, restart services, or expose ports.

Copy the script and systemd units to the NAS:

  sudo install -m 755 network-monitor.py /usr/local/bin/nas-network-monitor.py
  sudo install -m 644 systemd/nas-network-monitor.service /etc/systemd/system/
  sudo install -m 644 systemd/nas-network-monitor.timer /etc/systemd/system/

Enable and run the timer:

  sudo systemctl daemon-reload
  sudo systemctl enable --now nas-network-monitor.timer
  sudo systemctl start nas-network-monitor.service

Check the output:

  cat /srv/nas/websites/vukyweb/nas/data/network.json
  systemctl status nas-network-monitor.timer
  journalctl -u nas-network-monitor.service -n 30 --no-pager

The Wi-Fi signal field uses "iw dev <interface> link". If iw is not installed,
the dashboard will still show interface, gateway, internet and Tailscale status;
the signal and SSID fields will simply be unavailable. Install iw only if you
want those two extra values.

DEPLOYMENT
----------
The repository folder is nas-control-center-redesign. Copy its four HTML files,
css/style.css and js/app.js into:

  /srv/nas/websites/vukyweb/nas/

Copy network-monitor.py and the systemd units separately as shown above.
Preserve the NAS-side .htaccess, .htpasswd and data directory. Do not replace
the existing authentication files or monitoring JSON files.

Before replacing dashboard files, make a backup:

  sudo cp -a /srv/nas/websites/vukyweb/nas /srv/nas/websites/vukyweb/nas.backup.$(date +%F-%H%M)

CURRENT CONNECTION DETAILS
--------------------------
Local Wi-Fi IP:    192.168.100.13
Wi-Fi interface:   wlxb4b024d5369f
Ethernet:          enp0s25 (intentionally disabled)
Gateway:           192.168.100.1
Tailscale IPv4:    100.76.132.23
MagicDNS:          nas.tail02ce4c.ts.net
SSH user:          vuky
Storage mount:     /srv/nas

REMOTE ACCESS MODEL
-------------------
Use Tailscale for private administration. The browser terminal is available at:

  https://nas.tail02ce4c.ts.net:8443

The public Funnel URL serves VukyWeb on port 8080:

  https://nas.tail02ce4c.ts.net

Keep the dashboard's existing HTTP Basic Authentication enabled. Do not expose
SSH, SMB, Cockpit, Portainer, Transmission or ttyd directly to the public
internet. Do not disable or reconfigure the existing Tailscale Funnel or Serve
settings while deploying this dashboard.

DESIGN AND COMPATIBILITY
------------------------
No external frameworks, fonts, scripts or CDNs are required. Layouts adapt to
desktop, tablet and mobile widths. The dashboard uses semantic HTML, inline
SVG line icons, accessible labels and reduced-motion support.

The network page displays live values only when data/network.json exists and is
fresh. Static IPs are shown as connection references, not falsely reported as
live health checks.

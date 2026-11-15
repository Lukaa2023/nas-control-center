NAS CONTROL CENTER
==================

A responsive, multi-page dashboard for your private home NAS.

PAGES
-----
index.html      Overview, live system metrics, Docker status and shortcuts
services.html   Service links and SSH / SMB access
network.html    Local and Tailscale connection details and diagnostics
ports.html      Port reference based on the latest supplied listener output
css/style.css   Shared responsive dark interface
js/app.js       Live JSON monitoring, container rendering and copy controls

LIVE MONITORING
---------------
The Overview page reads two JSON snapshots from the same protected directory:
  data/stats.json    Host CPU, memory, storage, uptime and hostname
  data/docker.json   Docker container list, state, image, ports and health status

The browser does not execute shell commands. Separate Python scripts and
systemd timers on the NAS generate these snapshots. Keep those scripts and
timers installed and running for live data to update.

DEPLOYMENT
----------
Copy the four HTML files to the NAS dashboard directory, then copy the css and
js directories into that same directory. Preserve the NAS-side .htaccess,
.htpasswd and data directory. Do not overwrite those with repository copies.

Example target directory:
  /srv/nas/websites/vukyweb/nas/

CURRENT CONNECTION DETAILS
--------------------------
Local NAS IP:       192.168.100.7
Tailscale IP:       100.76.132.23
SSH user:           vuky
NAS storage mount:  /srv/nas

These IP addresses, service links and port bindings are reference information,
not dynamically discovered network details. Update the HTML pages if they
change. The port list is a snapshot of the supplied command output.

SECURITY
--------
Keep the dashboard protected by the existing NAS-side HTTP Basic Authentication.
Do not expose administrative services or SMB directly to the public internet.
Use Tailscale for private remote access. The dashboard links do not bypass each
service's own authentication. HTTPS services may show a certificate warning if
they use a self-signed certificate.

DESIGN
------
Near-black surfaces, white typography, fine outlines and restrained status
colours. Responsive navigation and layouts support desktop, tablet and mobile.
No external frameworks, fonts, scripts or CDNs are required.

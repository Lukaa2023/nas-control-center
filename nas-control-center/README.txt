NAS CONTROL CENTER
==================

A static, responsive multi-page dashboard for your home NAS.

PAGES
-----
index.html      Overview and quick links
services.html   Service links and SSH/SMB access
network.html    Local and Tailscale connection details
ports.html      Port reference based on your supplied command output
css/style.css  Shared styling
js/app.js       Copy-to-clipboard buttons

HOW TO USE
----------
1. Extract the ZIP.
2. Open index.html in a browser to preview it.
3. To host it on your NAS, copy the contents into a directory served by your web server.
   For example, if your website container serves /var/www/html, place the files there.
4. Open the dashboard through the address of the web server.

IMPORTANT
---------
This dashboard is static. It does not log in to the NAS, check service health, or
query Tailscale. "Last-known online" is based on the latest information supplied
when this dashboard was created.

CURRENT CONNECTION DETAILS
--------------------------
Local NAS IP:       192.168.100.7
Tailscale IP:       100.76.132.23
SSH user:           vuky
NAS storage mount:  /srv/nas

The dashboard uses the latest IP addresses and port bindings shared in chat.
If these change, update the links in the HTML files.

SECURITY
--------
Do not expose administrative services or SMB directly to the public internet.
Use Tailscale for remote private access. The links do not bypass authentication.
HTTPS services may show a browser certificate warning if using a self-signed
certificate.

DESIGN
------
The visual theme uses a soft pastel palette inspired by the VukyWeb colors.
All styles are local; no external frameworks, fonts, scripts, or CDNs are required.

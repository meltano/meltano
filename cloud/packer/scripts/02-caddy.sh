#!/bin/bash

# make sure the bundled installed binary is executable
chmod +x /usr/local/bin/caddy

# enable Caddy to bind privileged ports
sudo setcap 'cap_net_bind_service=+ep' /usr/local/bin/caddy

systemctl enable caddy

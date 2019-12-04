#!/bin/bash

# install htpasswd
sudo apt-get install -qqy apache2-utils

# make sure the bundled installed binary is executable
sudo chmod +x /usr/local/bin/caddy

# create the SSL store
sudo mkdir -p /etc/ssl/caddy
sudo chown www-data:www-data /etc/ssl/caddy

# enable Caddy to bind privileged ports
sudo setcap 'cap_net_bind_service=+ep' /usr/local/bin/caddy

systemctl enable caddy

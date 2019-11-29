#!/bin/bash

# This script setups the `vsftpd` daemon to enable
# a connection to the Meltano Project using FTP

# install `vsftpd`
sudo apt-get install -qqy vsftpd

sudo useradd \
  -g meltano --no-user-group \
  --home-dir /var/meltano/project --no-create-home \
  --shell /usr/sbin/nologin \
  meltano_ftp

# armor the meltano project to make sure we can't
# exfiltrate secret files
cd /var/meltano/project

# all files are only readable by the `meltano` user
sudo find . -path ./.meltano -prune -o -type f -exec chmod 620 {} \;

# directories are read/write for the `meltano` group
# in which `meltano_ftp` is a member
sudo find . -path ./.meltano -prune -o -type d -exec chmod 770 {} \;

systemctl enable vsftpd

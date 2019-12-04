#!/bin/bash

# This script setups the `vsftpd` daemon to enable
# a connection to the Meltano Project using FTP

# install `vsftpd`
sudo apt-get install -qqy -o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold' vsftpd

# armor the meltano project to make sure we can't
# exfiltrate secret files
cd /var/meltano/project

# all files are only readable by the `meltano` user
sudo find . -path ./.meltano -prune -o -type f -exec chmod 620 {} \;

# directories are read/write for the `meltano` group
# in which `meltano_ftp` is a member
sudo find . -path ./.meltano -prune -o -type d -exec chmod 770 {} \;

# non-writable root for chroot
sudo chmod g-w /var/meltano/project

systemctl enable vsftpd

No need to restart sytem
Debug using systemctl status to find path for logs
Logs are in .meltano directory
You can upgrade directly without restarting

{"error":"500 Internal Server Error: The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application."}

Response: 500 OOPS: vsftpd: refusing to run with writable root inside chroot()

ssh into meltano
apt search psql-client
install psql-client-
\dn (check for schemas
DROP SCHEMA \$NAME CASCADE)
Ctrl+D to exit

chmod g-w /var/meltano/project

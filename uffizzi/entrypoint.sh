#!/bin/bash

fortune | 
echo -e "
Welcome Uffizzi Preview Environment for Meltano! \n 


------------------------------ Quick guide ------------------------------ \n
poetry run meltano init test \n
cd test \n 
poetry run meltano add extractor tap-gitlab \n
poetry run meltano config tap-gitlab set projects meltano/meltano \n
poetry run meltano config tap-gitlab set start_date 2021-04-01T00:00:00Z \n 
poetry run meltano select tap-gitlab tags \n
poetry run meltano add loader target-sqlite \n
poetry run meltano config target-sqlite set --interactive \n\n

------------------------------ PostgresSQL ------------------------------ \n
Host: 127.0.0.1 \n
User: user \n
Password: password \n
DB: testdb \n
PORT: 5432 \n
PSQL connection: psql -h 127.0.0.1 -U user -d testdb -W \n

"| cowthink -W80 -f tux && git config oh-my-zsh.hide-info 1 && zsh
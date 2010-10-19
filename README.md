# install #

## On your backup server ##

1. git clone git@github.com:tfmagician/SimpleBackup.git 
2. sudo ./simple_backup/setup_server.sh
3. sudo mv ./simple_backup /home/simple_backup/lib
4. sudo su simple_backup -c 'crontab /home/simple_backup/lib/cron_srv'

## On your backup client ##

1. git clone git@github.com:tfmagician/SimpleBackup.git 
2. sudo ./simple_backup/setup_client.sh

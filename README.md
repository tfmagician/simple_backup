# install #

## On your backup server ##

1. git clone git@github.com:tfmagician/SimpleBackup.git 
2. sudo ./SimpleBackup/setup_server.sh
3. sudo mv ./SimpleBackup /home/simple_backup/lib
4. sudo chown -R simple_backup:simple_backup /home/simple_backup/lib
5. sudo su simple_backup -c 'crontab /home/simple_backup/lib/cron_srv'

## On your backup client ##

1. git clone git@github.com:tfmagician/SimpleBackup.git 
2. sudo ./SimpleBackup/setup_client.sh

### for mysqlhotcopy_rdiff setting. ###

1. Add the permission for RELOAD.
  ex. GRANT RELOAD ON *.* TO user@localhost;

#!/bin/bash

if [ `whoami` != 'root' ]; then
  echo 'ERROR: This script needs to run as root.'
  exit 1
fi

if grep '^simple_backup:' /etc/passwd > /dev/null; then
  echo 'WARNING: User simple_backup already exists.'
else
  if useradd -s /bin/bash -m simple_backup; then
    echo 'Created simple_backup user.'
  else
    exit 1
  fi
fi

if su simple_backup -c '/usr/bin/ssh-keygen -t rsa'; then
  echo 'Created the public key for simple_backup user.'
else
  exit 1
fi

cat <<EOF
You have two steps to finish setting up this backup server.
  1. Execute 'setup_host.sh' script on your backup clients.
  2. /home/simple_backup/.ssh/id_rsa.pub copies /home/simple_backup/.ssh/authorized_keys on your backup hosts to connect by ssh.
  3. Check the ssh connection with your backup host to execute 'ssh [your backup host]'.
EOF

exit 0

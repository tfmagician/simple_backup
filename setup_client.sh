#!/bin/bash

if [ `/usr/bin/whoami` != 'root' ]; then
  echo 'ERROR: This script needs to run as root.'
  exit 1
fi

if /bin/grep '^simple_backup:' /etc/passwd > /dev/null; then
  echo 'WARNING: User simple_backup already exists.'
else
  if /usr/sbin/useradd -s /bin/bash -m simple_backup; then
    echo 'Created simple_backup user.'
  else
    exit 1
  fi
fi

if [ ! -d /home/simple_backup/.ssh ]; then
  su simple_backup -c '/bin/mkdir /home/simple_backup/.ssh'
fi
su simple_backup -c '/bin/touch /home/simple_backup/.ssh/authorized_keys'

cat <<EOF
You have a step to finish setting up this backup client.
  1. Execute 'visudo' and add this settings.
    simple_backup ALL=(ALL) NOPASSWD: /usr/bin/find
    simple_backup ALL=(ALL) NOPASSWD: /usr/bin/mysqlhotcopy
    simple_backup ALL=(ALL) NOPASSWD: /bin/tar
EOF

exit 0

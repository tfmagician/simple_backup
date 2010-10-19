import logging
import commands
from exceptions import ExecutionError
from exceptions import ImproperlyConfigured
from backup_execution import BackupExecution

class MysqlhotcopyRdiff(BackupExecution):
  """
  Backup MySQL database using mysqlhotcopy and rdiff commands.
  """

  def __init__(self, config):
    """
    Check the configuration.
    Raise Exception if it's improperly configured.
    """
    try:
      config['host']
      config['database']
      config['user']
      config['password']
    except KeyError, e:
      logging.error(repr(e))
      raise ImproperlyConfigured()

    self.config = config

  def exec_cmd(self, cmd):
    """
    Exec command and catch the error by this.
    """

    logging.debug("Execute command '%s'." % cmd)
    result = commands.getstatusoutput(cmd)
    if result[0]:
      logging.error(result[1])
      raise ExecutionError()

  def execute(self):
    """
    1. Exec mysqlhotcopy command and copy the database directory that want to backup into /tmp.
    2. Exec rsync command and copy this direcotry into remote host.
    3. Exec rdiff-backup command and get the difference between the directory copied and the recent one.
    """

    e = self.exec_cmd
    c = self.config
    e("ssh %s sudo find /tmp -maxdepth 1 -type d -name '%s' -exec rm -rf {} \;" % (c['host'], c['database']))
    e('ssh %s sudo mysqlhotcopy -u%s -p%s %s /tmp' % (c['host'], c['user'], c['password'], c['database']))
    e('ssh %s sudo tar --remove-files --overwrite zxvf /tmp/%s /tmp/%s.tar.gz' % (c['host'], c['database'], c['database']))
    e('rsync -e ssh test1:/tmp/%s.tar.gz %s/%s.tar.gz' % (c['database'], self.tmp_dir, c['database']))
    e('rdiff-backup %s/%s.tar.gz %s' % (self.tmp_dir, c['database'], self.backup_dir))

  def rollback(self): pass

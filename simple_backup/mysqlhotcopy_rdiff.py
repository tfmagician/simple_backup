import logging
import commands
from sb_exceptions import ExecutionError
from sb_exceptions import ImproperlyConfigured
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

    if not config.has_key('port'):
      config['port'] = 22

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
    e("/usr/bin/ssh -p %s %s 'sudo /usr/bin/find /tmp -maxdepth 1 -type d -name '%s' -exec rm -rf {} \\;'" % (c['port'], c['host'], c['database']))
    e("/usr/bin/ssh -p %s %s 'sudo /usr/bin/mysqlhotcopy -u %s -p %s %s /tmp'" % (c['port'], c['host'], c['user'], c['password'], c['database']))
    e("/usr/bin/ssh -p %s %s 'sudo /bin/tar cvfP /tmp/%s.tar /tmp/%s --remove-files'" % (c['port'], c['host'], c['database'], c['database']))
    e("/usr/bin/rsync -e 'ssh -p %s' -z %s:/tmp/%s.tar %s/%s.tar" % (c['port'], c['host'], c['database'], self.tmp_dir, c['database']))
    e('/usr/bin/rdiff-backup %s %s' % (self.tmp_dir, self.backup_dir))

  def rollback(self): pass

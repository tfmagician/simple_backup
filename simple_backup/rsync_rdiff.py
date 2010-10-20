import logging
import commands
import os
from sb_exceptions import ExecutionError
from sb_exceptions import ImproperlyConfigured
from backup_execution import BackupExecution

class RsyncRdiff(BackupExecution):
  """
  Backup a directory using rsync and rdiff commands.
  """

  def __init__(self, config):
    """
    Check the configuration.
    Raise Exception if it's improperly configured.
    And rewrite the path to the backup directory for this apstract path.
    """
    try:
      config['host']
      config['directory']
    except KeyError, e:
      logging.error(repr(e))
      raise ImproperlyConfigured()

    if not config.has_key('port'):
      config['port'] = 22

    config['directory'] = os.path.abspath(config['directory'])
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
    1. Compress the direcory by tar command.
    2. Synchronize the file compressed by tar with backup server.
    3. Save the difference between the file synced and recent one.
    """

    e = self.exec_cmd
    c = self.config
    backup = c['directory'].replace('/', '_')[1:]
    e("/usr/bin/ssh %s -p %s 'sudo /bin/tar --overwrite -cvf /tmp/%s.tar %s'" % (c['host'], c['port'], backup, c['directory']))
    e("/usr/bin/rsync -e 'ssh -p %s' -z %s:/tmp/%s.tar %s/%s.tar" % (c['port'], c['host'], backup, self.tmp_dir, backup))
    e('/usr/bin/rdiff-backup %s %s' % (self.tmp_dir, self.backup_dir))

  def rollback(self): pass

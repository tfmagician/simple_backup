from simple_backup.backup_execution import BackupExecution
from simple_backup.exceptions import ImproperlyConfigured

class Copy3(BackupExecution):
  def __init__(self, *args):
    raise ImproperlyConfigured()

  def rollback(self, *args):
    self.flg_rollback = True
    self.arg_rollback = args

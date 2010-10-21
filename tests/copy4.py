from simple_backup.backup_execution import BackupExecution
from simple_backup.sb_exceptions import ExecutionError

class Copy4(BackupExecution):
  def __init__(self, *args):
    pass

  def execute(self, *args):
    raise ExecutionError('This is Exception on Copy4 instance.')

  def rollback(self, *args):
    self.flg_rollback = True
    self.arg_rollback = args

from simple_backup.backup_execution import BackupExecution

class Copy1(BackupExecution):
  def __init__(self, *args):
    self.flg_init = True
    self.arg_init = args

  def execute(self):
    self.flg_execute = True

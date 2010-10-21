import unittest
import commands
from os import path
from simple_backup.mysqlhotcopy_rdiff import MysqlhotcopyRdiff
from simple_backup.sb_exceptions import ImproperlyConfigured
from simple_backup.sb_exceptions import ExecutionError

# create logging mock object
import logging
logging.basicConfig(
  level = logging.NOTSET,
  format = '%(asctime)s %(levelname)s %(message)s',
  filename = '/tmp/test_simple_backup.log',
  filemode = 'w')

class MysqlhotcopyRdiffTestCase(unittest.TestCase):

  def setUp(self):
    config = {
      'type': 'mysqlhotcopy_rdiff',
      'host': 'test1',
      'database': 'database',
      'user': 'backup',
      'password': 'password'}
    self.MysqlhotcopyRdiff = MysqlhotcopyRdiff(config)
    self.MysqlhotcopyRdiff.backup_dir = '/home/backup/data'
    self.MysqlhotcopyRdiff.tmp_dir = '/home/backup/tmp'

  def tearDown(self):
    self.MysqlhotcopyRdiff = None

  def test_initialize(self):
    self.assertRaises(ImproperlyConfigured, lambda: MysqlhotcopyRdiff({'type': 'mysqlhotcopy_rdiff'}))

  def test_call_execute_method_when_command_is_successfull(self):
    # create mock object.
    called_cmds = []
    def getstatusoutput(cmd):
      called_cmds.append(cmd)
      return 0, 'Successful command %s.' % cmd
    commands.getstatusoutput = getstatusoutput

    self.MysqlhotcopyRdiff.execute()

    expected = [
      "/usr/bin/ssh -p 22 test1 'sudo /usr/bin/find /tmp -maxdepth 1 -type d -name 'database' -exec rm -rf {} \\;'",
      "/usr/bin/ssh -p 22 test1 'sudo /usr/bin/mysqlhotcopy -u backup -p password database /tmp'",
      "/usr/bin/ssh -p 22 test1 'sudo /bin/tar --remove-files --overwrite -cvf /tmp/database.tar /tmp/database'",
      "/usr/bin/rsync -e 'ssh -p 22' -z test1:/tmp/database.tar /home/backup/tmp/database.tar",
      "/usr/bin/rdiff-backup /home/backup/tmp /home/backup/data"]
    self.assertEqual(expected, called_cmds)

  def test_call_execute_method_when_command_is_failed(self):
    # create mock object.
    called_cmds = []
    def getstatusoutput(cmd):
      called_cmds.append(cmd)
      return 1, 'Failed command %s.' % cmd
    commands.getstatusoutput = getstatusoutput

    self.assertRaises(ExecutionError, self.MysqlhotcopyRdiff.execute)

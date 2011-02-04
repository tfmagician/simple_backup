import unittest
import commands
from os import path
from simple_backup.mysqldump_rdiff import MysqldumpRdiff
from simple_backup.sb_exceptions import ImproperlyConfigured
from simple_backup.sb_exceptions import ExecutionError

# create logging mock object
import logging
logging.basicConfig(
  level = logging.NOTSET,
  format = '%(asctime)s %(levelname)s %(message)s',
  filename = '/tmp/test_simple_backup.log',
  filemode = 'w')

class MysqldumpRdiffTestCase(unittest.TestCase):

  def setUp(self):
    config = {
      'type': 'mysqldump_rdiff',
      'host': 'test1',
      'database': 'database',
      'user': 'backup',
      'password': 'password'}
    self.MysqldumpRdiff = MysqldumpRdiff(config)
    self.MysqldumpRdiff.backup_dir = '/home/backup/data'
    self.MysqldumpRdiff.tmp_dir = '/home/backup/tmp'

  def tearDown(self):
    self.MysqldumpRdiff = None

  def test_initialize(self):
    self.assertRaises(ImproperlyConfigured, lambda: MysqldumpRdiff({'type': 'mysqldumpRdiff'}))

  def test_call_execute_method_when_command_is_successfull(self):
    # create mock object.
    called_cmds = []
    def getstatusoutput(cmd):
      called_cmds.append(cmd)
      return 0, 'Successful command %s.' % cmd
    commands.getstatusoutput = getstatusoutput

    self.MysqldumpRdiff.execute()

    expected = [
      "/usr/bin/ssh -p 22 test1 '/usr/bin/mysqldump -u backup -p password database | gzip > /tmp/database.sql.gz'",
      "/usr/bin/ssh -p 22 test1 '/bin/chmod 600 /tmp/database.sql.gz'",
      "/usr/bin/scp -P 22 test1:/tmp/database.sql.gz /home/backup/tmp",
      "/usr/bin/rdiff-backup /home/backup/tmp /home/backup/data"]
    self.assertEqual(expected, called_cmds)

  def test_call_execute_method_when_command_is_failed(self):
    # create mock object.
    called_cmds = []
    def getstatusoutput(cmd):
      called_cmds.append(cmd)
      return 1, 'Failed command %s.' % cmd
    commands.getstatusoutput = getstatusoutput

    self.assertRaises(ExecutionError, self.MysqldumpRdiff.execute)

import unittest
import commands
from os import path
from simple_backup.mysqlhotcopy_rdiff import MysqlhotcopyRdiff
from simple_backup.exceptions import ImproperlyConfigured
from simple_backup.exceptions import ExecutionError

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
      "ssh test1 sudo find /tmp -maxdepth 1 -type d -name 'database' -exec rm -rf {} \;",
      'ssh test1 sudo mysqlhotcopy -ubackup -ppassword database /tmp',
      'ssh test1 sudo tar --remove-files --overwrite zxvf /tmp/database /tmp/database.tar.gz',
      'rsync -e ssh test1:/tmp/database.tar.gz /home/backup/tmp/database.tar.gz',
      'rdiff-backup /home/backup/tmp/database.tar.gz /home/backup/data']
    self.assertEqual(expected, called_cmds)

  def test_call_execute_method_when_command_is_failed(self):
    # create mock object.
    called_cmds = []
    def getstatusoutput(cmd):
      called_cmds.append(cmd)
      return 1, 'Failed command %s.' % cmd
    commands.getstatusoutput = getstatusoutput

    self.assertRaises(ExecutionError, self.MysqlhotcopyRdiff.execute)

import unittest
import commands
from os import path
from simple_backup.rsync_rdiff import RsyncRdiff
from simple_backup.sb_exceptions import ImproperlyConfigured
from simple_backup.sb_exceptions import ExecutionError

# create logging mock object
import logging
logging.basicConfig(
  level = logging.NOTSET,
  format = '%(asctime)s %(levelname)s %(message)s',
  filename = '/tmp/test_simple_backup.log',
  filemode = 'w')

class RsyncRdiffTestCase(unittest.TestCase):

  def setUp(self):
    config = {
      'type': 'rsync_rdiff',
      'host': 'test1',
      'directory': '/path/to/directory'}
    self.RsyncRdiff = RsyncRdiff(config)
    self.RsyncRdiff.backup_dir = '/home/backup/data'
    self.RsyncRdiff.tmp_dir = '/home/backup/tmp'

  def tearDown(self):
    self.RsyncRdiff = None

  def test_initialize(self):
    self.assertRaises(ImproperlyConfigured, lambda: RsyncRdiff({'type': 'mysqlhotcopy_rdiff'}))

  def test_call_execute_method_when_command_is_successfull(self):
    # create mock object.
    called_cmds = []
    def getstatusoutput(cmd):
      called_cmds.append(cmd)
      return 0, 'Successful command %s.' % cmd
    commands.getstatusoutput = getstatusoutput

    self.RsyncRdiff.execute()

    expected = [
      "/usr/bin/ssh -p 22 test1 'sudo /bin/tar cvfP /tmp/path_to_directory.tar /path/to/directory'",
      "/usr/bin/rsync -e 'ssh -p 22' -z test1:/tmp/path_to_directory.tar /home/backup/tmp/path_to_directory.tar",
      '/usr/bin/rdiff-backup /home/backup/tmp /home/backup/data']
    self.assertEqual(expected, called_cmds)

  def test_call_execute_method_when_command_is_failed(self):
    # create mock object.
    called_cmds = []
    def getstatusoutput(cmd):
      called_cmds.append(cmd)
      return 1, 'Command failed %s.' % cmd
    commands.getstatusoutput = getstatusoutput

    self.assertRaises(ExecutionError, self.RsyncRdiff.execute)

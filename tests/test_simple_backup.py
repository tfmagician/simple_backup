#!/usr/bin/python

import unittest
import os
import time
import commands
from simple_backup.simple_backup import SimpleBackup
from simple_backup.sb_exceptions import ImproperlyConfigured
from simple_backup.sb_exceptions import ExecutionError

# create logging mock object
import logging
logging.basicConfig(
  level = logging.NOTSET,
  format = '%(asctime)s %(levelname)s %(message)s',
  filename = '/tmp/test_simple_backup.log',
  filemode = 'w')

# create os mock object
os.makedirs = lambda path, code = 022: True

class SimpleBackupTestCase(unittest.TestCase):

  def setUp(self):
    reload(time)
    reload(os)
    reload(commands)

    os.makedirs = lambda path: True

    config_file = os.path.abspath('tests/config1.yaml')
    self.SimpleBackup = SimpleBackup(config_file)

  def tearDown(self):
    self.SimpleBackup = None

  def test_initialize(self):
    # check the config attribute.
    config_dict = {
      'hosts': {
        'test1_copy1': {
          'type': 'tests.copy1',
          'host': 'test1',
          'setting1': 'setting_value1',
          'setting2': 'setting_value2'},
        'test2_copy2': {
          'type': 'tests.copy2',
          'host': 'test2',
          'setting1': 'setting_value1',
          'setting2': 'setting_value2'}
      }
    }
    self.assertEqual(config_dict, self.SimpleBackup.config)

    # check the attribute of backup instanse.
    self.assertEqual(True, self.SimpleBackup.__dict__.has_key('test1_copy1'))
    self.assertEqual(True, self.SimpleBackup.__dict__.has_key('test2_copy2'))

    # check the attribute of directory using by this setting.
    self.assertEqual('/home/backup/backup/test1_copy1', self.SimpleBackup.test1_copy1.backup_dir)
    self.assertEqual('/home/backup/tmp/test1_copy1', self.SimpleBackup.test1_copy1.tmp_dir)
    self.assertEqual('/home/backup/backup/test2_copy2', self.SimpleBackup.test2_copy2.backup_dir)
    self.assertEqual('/home/backup/tmp/test1_copy1', self.SimpleBackup.test1_copy1.tmp_dir)

    # check the dir attributes.
    self.assertEqual(True, self.SimpleBackup.__dict__.has_key('base_dir'))
    self.assertEqual(True, self.SimpleBackup.__dict__.has_key('archive_dir'))
    self.assertEqual(True, self.SimpleBackup.__dict__.has_key('tmp_dir'))
    self.assertEqual(True, self.SimpleBackup.__dict__.has_key('backup_dir'))

  def test_call_main(self):
    self.SimpleBackup.main()

    # Call main function for test1 host.
    self.assertEqual(True, self.SimpleBackup.test1_copy1.flg_init)
    self.assertEqual(True, self.SimpleBackup.test1_copy1.flg_execute)
    arg_dict = {
      'type': 'tests.copy1',
      'host': 'test1',
      'setting1': 'setting_value1',
      'setting2': 'setting_value2'}
    self.assertEqual((arg_dict, ), self.SimpleBackup.test1_copy1.arg_init)

    # Call main function for test2 host.
    self.assertEqual(True, self.SimpleBackup.test2_copy2.flg_init)
    self.assertEqual(True, self.SimpleBackup.test2_copy2.flg_execute)
    arg_dict = {
      'type': 'tests.copy2',
      'host': 'test2',
      'setting1': 'setting_value1',
      'setting2': 'setting_value2'}
    self.assertEqual((arg_dict, ), self.SimpleBackup.test2_copy2.arg_init)

  def test_call_main_when_set_specific_setting(self):
    self.SimpleBackup.main('test1_copy1')

    # Call main function for test1 host.
    self.assertEqual(True, self.SimpleBackup.test1_copy1.flg_init)
    self.assertEqual(True, self.SimpleBackup.test1_copy1.flg_execute)
    arg_dict = {
      'type': 'tests.copy1',
      'host': 'test1',
      'setting1': 'setting_value1',
      'setting2': 'setting_value2'}
    self.assertEqual((arg_dict, ), self.SimpleBackup.test1_copy1.arg_init)

    # Call main function for test2 host.
    self.assertEqual(True, self.SimpleBackup.test2_copy2.flg_init)
    self.assertEqual(False, self.SimpleBackup.test2_copy2.__dict__.has_key('flg_execute'))
    arg_dict = {
      'type': 'tests.copy2',
      'host': 'test2',
      'setting1': 'setting_value1',
      'setting2': 'setting_value2'}
    self.assertEqual((arg_dict, ), self.SimpleBackup.test2_copy2.arg_init)

  def test_raise_exception_when_init_backup_class(self):
    config_file = os.path.abspath('tests/config2.yaml')
    self.assertRaises(SystemExit, lambda: SimpleBackup(config_file));

  def test_raise_exception_when_call_backup_class_execute_method(self):
    config_file = os.path.abspath('tests/config3.yaml')
    self.SimpleBackup = SimpleBackup(config_file)
    self.SimpleBackup.main()
    self.assertEqual(True, self.SimpleBackup.test4_copy4.flg_rollback)

  def test_call_archive_when_command_is_successful(self):
    called_cmds = []
    def getstatusoutput(cmd):
      called_cmds.append(cmd)
      return 0, 'Successful command %s.' % cmd
    commands.getstatusoutput = getstatusoutput

    def access(path, type):
      return True
    os.access = access

    # create the mock object for time module.
    org_strftime = time.strftime
    def strftime(format, t = 'dummy'):
      if format == '%d':
        return '01'
      elif format == '%Y%m%d':
        return '20101001'
      else:
        return org_strftime(format, t)

    time.strftime = strftime
    self.SimpleBackup.archive()

    expected = [
      'tar zcvfP /home/backup/archive/20101001.tar.gz /home/backup/backup --remove-files']
    self.assertEqual(expected, called_cmds)

  def test_call_archive_when_command_is_failed(self):
    called_cmds = []
    def getstatusoutput(cmd):
      called_cmds.append(cmd)
      return 1, 'Command failed %s.' % cmd
    commands.getstatusoutput = getstatusoutput

    def access(path, type):
      return True
    os.access = access

    # create the mock object for time module.
    reload(time)
    org_strftime = time.strftime
    def strftime(format, t = 'dummy'):
      if format == '%d':
        return '01'
      elif format == '%Y%m%d':
        return '20101001'
      else:
        return org_strftime(format, t)

    time.strftime = strftime
    self.assertRaises(SystemExit, self.SimpleBackup.archive)

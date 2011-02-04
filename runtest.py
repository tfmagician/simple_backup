#!/usr/bin/python

from test import test_support

# Import test cases.
from tests.test_simple_backup import SimpleBackupTestCase
from tests.test_mysqlhotcopy_rdiff import MysqlhotcopyRdiffTestCase
from tests.test_mysqldump_rdiff import MysqldumpRdiffTestCase
from tests.test_rsync_rdiff import RsyncRdiffTestCase

def test_main():
  test_support.run_unittest(
    SimpleBackupTestCase,
    MysqlhotcopyRdiffTestCase,
    MysqldumpRdiffTestCase,
    RsyncRdiffTestCase)

if __name__ == '__main__':
  test_main()

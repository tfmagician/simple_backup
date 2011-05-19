import logging
import commands
import os
import boto
from sb_exceptions import ExecutionError
from sb_exceptions import ImproperlyConfigured
from backup_execution import BackupExecution
from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import RegionInfo

class AmazonEbsSnapshot(BackupExecution):
  """
  Backup Amazon EBS volume as snapshot
  """

  def __init__(self, config):
    """
    Check the configuration.
    Raise Exception if it's improperly configured.
    """
    try:
      config['volume_id']
      config['access_key']
      config['secret_access_key']
      config['region']
    except KeyError, e:
      logging.error(repr(e))
      raise ImproperlyConfigured()

    if not config.has_key('keep'):
      config['keep'] = 5

    self.config = config

  def execute(self):
    """
    Backup and keep snapshots configured by 'keep' key.
    """

    c = self.config
    regions = dict((x.name, x) for x in boto.ec2.regions(
        aws_access_key_id=c['access_key'],
        aws_secret_access_key=c['secret_access_key']))
    connect = regions[c['region']].connect(
        aws_access_key_id=c['access_key'],
        aws_secret_access_key=c['secret_access_key'])
    volume = connect.get_all_volumes([c['volume_id']])[0]
    volume.create_snapshot(c['volume_id'])
    snapshots = {}
    for x in connect.get_all_snapshots():
      if x.volume_id == c['volume_id']:
        snapshots.update({x.id: x.start_time})
    snapshots = sorted(snapshots.items(), key=lambda (k, v): (v, k), reverse=True)
    for i in range(int(c['keep']), len(snapshots)):
      connect.delete_snapshot(snapshots[i][0])

  def rollback(self): pass

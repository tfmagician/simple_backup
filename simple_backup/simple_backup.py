import yaml, logging, os, commands, time, getopt
from exceptions import ExecutionError
from exceptions import ImproperlyConfigured

class SimpleBackup:
  """
  main backup class.
  """

  def __init__(self, config_file, base_dir = '/home/backup'):
    """
    initialize backup instanses.
    """
    logging.info('Initializing backup settings.')

    dir_types = ('backup', 'tmp')

    # load config file.
    self.config = yaml.load(open(config_file).read())
    config = self.config['hosts']

    # set base_dir attribute.
    self.base_dir = base_dir
    self.archive_dir = '%s/archive' % base_dir
    for type in dir_types:
      self.__dict__[type + '_dir'] = '%s/%s' % (base_dir, type)

    # create and initialize an instance for the backup setting.
    for setting in config:
      # create a backup instanse and initialize.
      module = config[setting]['type']
      try:
        self.__dict__[setting] = self.load_module(module)(config[setting])
      except ImproperlyConfigured:
        logging.error('Configuration error by setting %s.' % setting)
        logging.error('Exit SimpleBackup script.')
        raise SystemExit(1)
      # initialize directory attribute for the instanse.
      for type in dir_types:
        dir = os.path.abspath('%s/%s/%s' % (base_dir, type, setting))
        if not os.access(dir, os.F_OK):
          try:
            os.makedirs(dir, 022)
          except OSError, e:
            logging.error(repr(e))
            raise SystemExit(1)
        self.__dict__[setting].__dict__[type + '_dir'] = dir

  def load_module(self, module):
    """
    load module for backup instanse.
    """

    attr = module.split('.').pop()
    mod = getattr(__import__(module), attr)
    return getattr(mod, attr.title().replace('_', ''))

  def main(self):
    """
    execute backup for all backup hosts.
    """

    config = self.config['hosts']
    for setting in config:

      logging.info('Backuping by setting %s.' % setting)

      try:
        self.__dict__[setting].execute()
      except ExecutionError, e:
        logging.error('Backup error occured by setting %s.' % setting)

        logging.error('Executing rollback for setting %s.' % setting)
        self.__dict__[setting].rollback()

      logging.info('Finish Backup by setting %s.' % setting)

  def archive(self):
    """
    archive all backup directories.
    """ 

    if time.strftime('%d') == '01':
      cmd = 'tar --remove-files zxvf %s %s/%s.tar.gz' % (self.backup_dir, self.archive_dir, time.strftime('%Y%m%d'))
      result = commands.getstatusoutput(cmd)
      if result[0]:
        logging.error('Could not create monthly archive.')
        logging.error(result[1])
        raise SystemExit(1)

def main(config, base_dir):
  sb = SimpleBackup(config, base_dir)
  sb.main()

if __name__ == '__main__':
  try:
    opts, args = getopt.getopt(
      sys.argv[1:],
      'cd',
      ['config', 'base_dir'])
  except getopt.GetoptError:
    print "FATAL - Bat command line options / parameter."
    sys.exit(2)

  base_dir = '/home/simple_backup'
  config = base_dir + '/lib/simple_backup/config.yaml'
  for o, a in opts:
    if o in ('-c', '--config'):
      config = a
    if o in ('-d', '--base_dir'):
      base_dir = a

  main(config, base_dir)
  sys.exit(0)

"""
Global SimpleBackup exception and error classes.
"""

class ImproperlyConfigured(Exception):
  "SimpleBackup is somehow impropely configured"
  pass

class ExecutionError(Exception):
  "SimpleBackup could not exectute some command."
  pass

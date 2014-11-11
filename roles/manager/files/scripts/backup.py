import time
import datetime
import os.path
import os
import tempfile
import subprocess

BACKUP_LEVEL = 12

class RotatingFilenameHourly:
    def __init__(self, basepath):
        self.basepath = basepath
        self.scheme = '%Y.%m.%d.%H'
    def getCurrent(self):
        return self.basepath + time.strftime(self.scheme)
    def getLastN(self, n):
        lastN = []
        for i in range(n):
            lastN.append(self.basepath + time.strftime(self.scheme, time.gmtime(time.time() - (3600*i))))
        return lastN

class BackupPostgresql:
    def run(self):
        tfd = tempfile.NamedTemporaryFile(delete=False)
        subprocess.call(['pg_dump', '-U', 'pacsocial', 'pacsocial'], stdout=tfd)
        return tfd.name
        
class BackupManager:
    def __init__(self):
        self.backups = {}
    def addBackup(self, name, service):
        self.backups[name] = service

    def _tar(self, fp):
        op = fp + '.tar'
        subprocess.call(['tar', 'cf', op, fp])
        subprocess.call(['rm', fp])
        return op
    def _gz(self, fp):
        subprocess.call(['gzip', fp])
        return fp + '.gz'

    def _move(self, src, dest):
        subprocess.call(['mv', src, dest])

    def _rm(self, src):
        subprocess.call(['rm', src])

    def run(self):
        for (name, service) in self.backups.items():
            backup_dir = '/var/local/backups/' + name + '/'
            rt = RotatingFilenameHourly(backup_dir)
            try:
                os.mkdir(backup_dir)
            except OSError:
                pass # already exists

            fp = service.run()
            fptar = self._tar(fp)
            fptargz = self._gz(fptar)
            self._move(fptargz, rt.getCurrent())

            permissible_backups = set(rt.getLastN(BACKUP_LEVEL))
            existing_backups = os.walk(backup_dir)

            for (_, _, backups) in existing_backups:
                for backup in backups:
                    if os.path.join(backup_dir, backup) not in permissible_backups:
                        self._rm(os.path.join(backup_dir, backup))

if __name__ == "__main__":
    backer = BackupManager()
    pgsql = BackupPostgresql()
    backer.addBackup('postgresql', pgsql)
    backer.run()


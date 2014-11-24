import time
import ConfigParser
import datetime
import os.path
import os
import tempfile
import subprocess
import boto.glacier
import boto.glacier.layer2

class BackupPostgresql:
    def run(self, fp):
        return subprocess.call('pg_dump -U pacsocial pacsocial | base64 > %s' % (fp,), shell=True)
        
if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read('/usr/local/share/smisc.ini')
    glacier = boto.glacier.layer2.Layer2(config.get('glacier', 'key'), config.get('glacier', 'secret'), region_name=config.get('glacier', 'region'))
    vault = glacier.get_vault(config.get('glacier', 'vault-postgresqlbackups'))
    with tempfile.NamedTemporaryFile() as fd:
        fp = fd.name
        pgsql = BackupPostgresql()
        pgsql.run(fp)
        created_dt = datetime.datetime.fromtimestamp(time.time())

        writer = vault.upload_archive(fp, description='PostgreSQL snapshot created at ' + created_dt.strftime('%b %d %Y - %H:%M:%S'))

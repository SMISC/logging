#!/usr/bin/env python2

import sys
import json
import tempfile

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fdt = tempfile.NamedTemporaryFile(delete=False)
    else:
        fdt = sys.stdout

    for line in sys.stdin:
        droplets = json.loads(line)
        for droplet in droplets['droplets']:
            if droplet['status'] == 'active':
                host = droplet['name']
                ip = droplet['ip_address']
                fdt.write("%s %s.jacobgreenleaf.com %s\n" % (ip, host, host))
    
    if len(sys.argv) > 1:
        print(fdt.name)

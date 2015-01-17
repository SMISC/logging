#!/usr/bin/env python

import sys
import json

if __name__ == "__main__":
    for line in sys.stdin:
        droplets = json.loads(line)
        for droplet in droplets['droplets']:
            if droplet['status'] == 'active':
                host = droplet['name']
                ip = droplet['ip_address']
                print('%s %s.jacobgreenleaf.com %s' % (ip, host, host))

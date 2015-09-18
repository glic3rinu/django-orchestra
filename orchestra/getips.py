#! /usr/bin/env python

import requests
import json


SLICE_ID=1513


slice_req = requests.get('https://controller.community-lab.net/api/slices/%i' % SLICE_ID)
slice = json.loads(slice_req.content)
for sliver in slice['slivers']:
    sliver_req = requests.get(sliver['uri'])
    sliver = json.loads(sliver_req.content)
    print sliver['mgmt_net']['address']

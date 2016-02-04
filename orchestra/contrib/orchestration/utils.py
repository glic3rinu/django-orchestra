from orchestra.utils.sys import run, sshrun, join


def retrieve_state(servers):
    uptimes = []
    pings = []
    for server in servers:
        address = server.get_address()
        ping = run('ping -c 1 -w 1 %s' % address, async=True)
        pings.append(ping)
        uptime = sshrun(address, 'uptime', persist=True, async=True, options={'ConnectTimeout': 1})
        uptimes.append(uptime)
    
    state = {}
    for server, ping, uptime in zip(servers, pings, uptimes):
        ping = join(ping, silent=True)
        ping = ping.stdout.splitlines()[-1].decode()
        if ping.startswith('rtt'):
            ping = '%s ms' % ping.split('/')[4]
        else:
            ping = '<span style="color:red"><b>offline<b></span>'
        
        uptime = join(uptime, silent=True)
        uptime = uptime.stdout.decode().split()
        if uptime:
            uptime = 'Up %s %s load %s %s %s' % (uptime[2], uptime[3], uptime[-3], uptime[-2], uptime[-1])
        else:
            uptime = '<span style="color:red"><b>Timeout<b></span>'
        state[server.pk] = (ping, uptime)
    
    return state

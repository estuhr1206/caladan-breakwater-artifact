#!/usr/bin/env python3

import paramiko
import os
from util import *
from config_remote import *

# k = paramiko.RSAKey.from_private_key_file(KEY_LOCATION)
# # connection to server
# server_conn = paramiko.SSHClient()
# server_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# server_conn.connect(hostname = SERVER, username = USERNAME, pkey = k)

# # connection to client
# client_conn = paramiko.SSHClient()
# client_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# client_conn.connect(hostname = CLIENT, username = USERNAME, pkey = k)

# # connection to agents
# agent_conns = []
# for agent in AGENTS:
#     agent_conn = paramiko.SSHClient()
#     agent_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     agent_conn.connect(hostname = agent, username = USERNAME, pkey = k)
#     agent_conns.append(agent_conn)


print("installing build-essential, etc.")
cmd = "sudo apt-get -y install build-essential libnuma-dev clang autoconf"\
        " autotools-dev m4 automake libevent-dev libpcre++-dev libtool"\
        " ragel libev-dev moreutils parallel cmake python3 python3-pip"\
        " libjemalloc-dev libaio-dev libdb5.3++-dev numactl hwloc libmnl-dev"\
        " libnl-3-dev libnl-route-3-dev uuid-dev libssl-dev libcunit1-dev pkg-config"
print(cmd)
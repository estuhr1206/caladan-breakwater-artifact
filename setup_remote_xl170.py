#!/usr/bin/env python3

import paramiko
import os
from util import *
from config_remote import *

k = paramiko.RSAKey.from_private_key_file(KEY_LOCATION)
# connection to server
server_conn = paramiko.SSHClient()
server_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
server_conn.connect(hostname = SERVER, username = USERNAME, pkey = k)

# connection to client
client_conn = paramiko.SSHClient()
client_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client_conn.connect(hostname = CLIENT, username = USERNAME, pkey = k)

# connection to agents
agent_conns = []
for agent in AGENTS:
    agent_conn = paramiko.SSHClient()
    agent_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    agent_conn.connect(hostname = agent, username = USERNAME, pkey = k)
    agent_conns.append(agent_conn)


# install sub-modules
print("Building submodules... (it may take a few mintues)")
cmd = "cd ~/{}/caladan && make submodules".format(ARTIFACT_PATH)
execute_remote([server_conn, client_conn] + agent_conns, cmd, True)


# ksched and machine setup
print("Building in ksched, building Caladan, and running machine setup script")
cmd = "cd ~/{}/caladan && pushd ksched && make clean && make && popd".format(ARTIFACT_PATH)
execute_remote([server_conn, client_conn] + agent_conns, cmd, True)

cmd = "cd ~/{}/caladan && sudo ./scripts/setup_machine.sh".format(ARTIFACT_PATH)
execute_remote([server_conn, client_conn] + agent_conns, cmd, True)

# apt updates and installs
print("apt-get update")
cmd = "sudo apt-get update"
execute_remote([server_conn, client_conn] + agent_conns, cmd, True)

# why is this installing make, AFTER we've already used it a bit??
print("installing clang")
cmd = "sudo apt-get -y install make gcc cmake pkg-config libnl-3-dev libnl-route-3-dev"\
        " libnuma-dev uuid-dev libssl-dev libaio-dev libcunit1-dev libclang-dev"
execute_remote([server_conn, client_conn] + agent_conns, cmd, True)

print("installing make, gcc, cmake, etc.")
cmd = "sudo apt-get -y install clang"
execute_remote([server_conn, client_conn] + agent_conns, cmd, True)

print("installing build-essential, etc.")
cmd = "sudo apt-get -y install build-essential libnuma-dev clang autoconf"\
        " autotools-dev m4 automake libevent-dev  libpcre++-dev libtool"\
        " ragel libev-dev moreutils parallel cmake python3 python3-pip"\
        " libjemalloc-dev libaio-dev libdb5.3++-dev numactl hwloc libmnl-dev"\
        " libnl-3-dev libnl-route-3-dev uuid-dev libssl-dev libcunit1-dev pkg-config"
execute_remote([server_conn, client_conn] + agent_conns, cmd, True)

# finishing caladan build
print("Building caladan bindings and netbench")
cmd = "cd ~/{}/caladan && make -C bindings/cc && make -C apps/netbench/".format(ARTIFACT_PATH)
execute_remote([server_conn, client_conn] + agent_conns, cmd, True)


print("Building Breakwater...")
cmd = "cd ~/{}/caladan/breakwater && make clean && make clean -C apps/netbench/ &&"\
        " make clean -C bindings/cc".format(ARTIFACT_PATH)
execute_remote([server_conn, client_conn] + agent_conns, cmd, True)

cmd = "cd ~/{}/caladan/breakwater && make && make -C bindings/cc"\
        " && make -C apps/netbench/".format(ARTIFACT_PATH)
execute_remote([server_conn, client_conn] + agent_conns, cmd, True)

# this is Inho's not mine (below)
# print("Setting up memcahced...")
# cmd = "cd ~/{}/shenango-memcached && ./version.sh && autoreconf -i"\
#         " && ./configure --with-shenango=../shenango"\
#         .format(ARTIFACT_PATH)
# execute_remote([server_conn], cmd, True)

##### trying out the caladan all version of this
# build snappy for caladan
# print("building snappy")
# cmd = "cd  ~/{}/caladan/apps/storage_service/snappy && mkdir build".format(ARTIFACT_PATH)
# execute_remote([server_conn, client_conn] + agent_conns, cmd, True)

# cmd = "cd ~/{}/caladan/apps/storage_service/snappy/build && cmake ../ && make".format(ARTIFACT_PATH)
# execute_remote([server_conn, client_conn] + agent_conns, cmd, True)
#####


print("Done.")

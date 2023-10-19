#!/usr/bin/env python3

### NOTE these assume the directory setup present in cloudlab xl170 nodes.
### probably won't match normal directory setup for where home is.

import paramiko
import os
from util import *
from config_remote import *
from datetime import datetime

k = paramiko.RSAKey.from_private_key_file(KEY_LOCATION)
# connection to server
server_conn = paramiko.SSHClient()
server_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
server_conn.connect(hostname = SERVER, username = USERNAME, pkey = k)

# connection to client
client_conn = paramiko.SSHClient()
client_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client_conn.connect(hostname = CLIENT, username = USERNAME, pkey = k)


# directory naming from caladan all
## 'name': "run.{}".format(datetime.now().strftime('%Y%m%d%H%M%S')),
print("Setting up server, making directory and installing python modules")
directory_name = "run.{}".format(datetime.now().strftime('%Y%m%d%H%M%S'))
directory_name += "-caladan-memcached_trace"
cmd = "cd ~/{} && mkdir {}".format(ARTIFACT_PATH, directory_name)
execute_remote([server_conn], cmd, True)
cmd = "pip3 install pandas && pip3 install matplotlib"
execute_remote([server_conn], cmd, True)

# move files from client to server
print("moving files from client to server")
cmd = "scp -r 0-node-1.memcached.* {}:/users/{}/{}".format(SERVER, USERNAME, directory_name)
execute_remote([client_conn], cmd, True)
cmd = "scp -r iokernel.node-1.log {}:/users/{}/{}".format(SERVER, USERNAME, directory_name)
execute_remote([client_conn], cmd, True)

# move files around on server
print("moving files into single directory on server")
cmd = "cd ~/{} &* mv mem.log swaptionsGC_shm_query.out iokernel.node-0.log memcached.err"\
    " memcached.out swaptionsGC.out swaptionsGC.err ~/{}".format(ARTIFACT_PATH, directory_name)
execute_remote([server_conn], cmd, True)
# deal with configs
cmd = "cd ~/{} && cp ./caladan/server.config swaptionsGC.config ~/{}".format(ARTIFACT_PATH, directory_name)
execute_remote([server_conn], cmd, True)
cmd = "cd ~/{} && cp server.config 0-node-1.memcached.config".format(directory_name)
execute_remote([server_conn], cmd, True)

# create graphs
print("producing graphs")
cmd = "cd ~/{} && python3 ~/{}/caladan-all/create_corecsv.py {}".format(ARTIFACT_PATH, directory_name,
                                                                           ARTIFACT_PATH, directory_name)
execute_remote([server_conn], cmd, True)
cmd = "cd ~/{} && python3 ~/{}/caladan-all/graph.py {}".format(ARTIFACT_PATH, directory_name,
                                                                  ARTIFACT_PATH, directory_name)
execute_remote([server_conn], cmd, True)

print("Graph files are on server. Feel free to use appropriate tools such as scp to move them.")


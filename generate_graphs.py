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
cmd = "cd ~ && mkdir -p {}".format(directory_name)
execute_remote([server_conn], cmd, True)
cmd = "pip3 install pandas && pip3 install matplotlib"
execute_remote([server_conn], cmd, True)

# move files from client to server
print("moving files from client to server")
# cmd = "cd ~/{} && scp -r 0-node-1.memcached.* {}@{}:/users/{}/{}".format(ARTIFACT_PATH, USERNAME, SERVER, USERNAME, directory_name)
# execute_remote([client_conn], cmd, True)
# cmd = "cd ~/{} && scp -r iokernel.node-1.log {}@{}:/users/{}/{}".format(ARTIFACT_PATH, USERNAME, SERVER, USERNAME, directory_name)
# execute_remote([client_conn], cmd, True)
# Seems like because of keys and all that, need to do some redirection through the local machine
cmd = "cmd = scp -P 22 -i {} -o StrictHostKeyChecking=no {}@{}:~/{}/0-node-1.memcached.* .".format(
                                                        KEY_LOCATION, USERNAME, CLIENT, ARTIFACT_PATH)
execute_local(cmd)
cmd = "cmd = scp -P 22 -i {} -o StrictHostKeyChecking=no {}@{}:~/{}/iokernel.node-1.log .".format(
                                                        KEY_LOCATION, USERNAME, CLIENT, ARTIFACT_PATH)
execute_local(cmd)
cmd = "cmd = scp -P 22 -i {} -o StrictHostKeyChecking=no ./0-node-1.memcached.* {}@{}:~/{}".format(
                                                        KEY_LOCATION, USERNAME, SERVER, directory_name)
execute_local(cmd)
cmd = "cmd = scp -P 22 -i {} -o StrictHostKeyChecking=no ./iokernel.node-1.log {}@{}:~/{}".format(
                                                        KEY_LOCATION, USERNAME, SERVER, directory_name)
execute_local(cmd)

cmd = "rm -f ./0-node-1.memcached.* && rm -f ./iokernel.node-1.log"
execute_local(cmd)

# move files around on server
print("moving files into single directory on server")
cmd = "cd ~/{} && mv mem.log swaptionsGC_shm_query.out iokernel.node-0.log memcached.err"\
    " memcached.out swaptionsGC.out swaptionsGC.err ~/{}".format(ARTIFACT_PATH, directory_name)
execute_remote([server_conn], cmd, True)
# deal with configs
cmd = "cd ~/{} && cp ./caladan/server.config swaptionsGC.config ~/{}".format(ARTIFACT_PATH, directory_name)
execute_remote([server_conn], cmd, True)
cmd = "cd ~/{} && cp server.config 0-node-1.memcached.config".format(directory_name)
execute_remote([server_conn], cmd, True)

# create graphs
print("producing graphs")
cmd = "cd ~ && python3 ~/{}/caladan-all/create_corecsv.py {}".format(ARTIFACT_PATH, directory_name)
execute_remote([server_conn], cmd, True)
cmd = "cd ~ && python3 ~/{}/caladan-all/graph.py {}".format(ARTIFACT_PATH, directory_name)
execute_remote([server_conn], cmd, True)

print("Graph files are on server. Feel free to use appropriate tools such as scp to move them.")


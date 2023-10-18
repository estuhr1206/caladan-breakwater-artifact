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
cmd = "cd ~/{} && mkdir {}".format(ARTIFACT_PATH, directory_name)
execute_remote([server_conn], cmd, True)
cmd = "pip3 install pandas && pip3 install matplotlib"
execute_remote([server_conn], cmd, True)

# move files from client to server
print("moving files from client to server")
cmd = "scp -r 0-node-1.memcached.* ssh {}:/users/{}/{}".format(SERVER, USERNAME, directory_name)
execute_remote([client_conn], cmd, True)
cmd = "scp -r iokernel.node-1.log ssh {}:/users/{}/{}".format(SERVER, USERNAME, directory_name)
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
cmd = ""


"""
mv caladan/mem.log run.20230228215633-caladan-memcached_trace/
mv caladan/swaptionsGC_shm_query.out run.20230228215633-caladan-memcached_trace/
mv iokernel.node-0.log memcached.err memcached.out swaptionsGC.out swaptionsGC.err run.20230228215633-caladan-memcached_trace/
cp server.config 0-node-1.memcached.config
cp 0-node-1.memcached.config server.config swaptionsGC.config run.20230228215633-caladan-memcached_trace/

python3 caladan-all/create_corecsv.py
python3 caladan-all/graph.py run.20230228215633-caladan-memcached_trace/

----------------Optional------------------------------
In caladan-all
vi x.sh

set -e
set -x

# record BASE_DIR
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
echo "BASE_DIR = '${SCRIPTPATH}/'" > base_dir.py

chmod +x x.sh
./x.sh
-------------Optional till here - if python command gives error - base_dir one------------------------------
pip3 install pandas
pip3 install matplotlib


"""



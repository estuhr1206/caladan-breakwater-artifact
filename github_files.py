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

# repo_name = (os.getcwd().split('/'))[-1]
repo_name = "caladan-breakwater-base"

# Moving config files to right spots in codebase
# TODO for now just going to assume that this artifact repo and the caladan base folder
# with the github files are contained in the same directory on this machine. 
# NOTE using cp may alias to cp -i (interactive) on same machines, and hence fail to actually
# overwrite without prompting. TODO?
print("placing config files and needed scripts into github base")
# overwrites
cmd = "cp client.config ../{}/caladan/client.config".format(repo_name)
execute_local(cmd)
# per instructions, might look into if these ever should be different
cmd = "cp memcached.config ../{}/caladan/server.config".format(repo_name)
execute_local(cmd)

# new config files
cmd = "cp memcached.config ../{}/".format(repo_name)
execute_local(cmd)
cmd = "cp swaptionsGC.config ../{}/".format(repo_name)
execute_local(cmd)

# build_all.sh script
cmd = "cp build_all.sh ../{}/".format(repo_name)
execute_local(cmd)


# distributing code-base
print("Distributing sources...")

# - server
cmd = "rsync -azh -e \"ssh -i {} -o StrictHostKeyChecking=no"\
        " -o UserKnownHostsFile=/dev/null\" --progress ../{}/"\
        " {}@{}:~/{} >/dev/null"\
        .format(KEY_LOCATION, repo_name, USERNAME, SERVER, ARTIFACT_PATH)
execute_local(cmd)
# - client
cmd = "rsync -azh -e \"ssh -i {} -o StrictHostKeyChecking=no"\
        " -o UserKnownHostsFile=/dev/null\" --progress ../{}/"\
        " {}@{}:~/{} >/dev/null"\
        .format(KEY_LOCATION, repo_name, USERNAME, CLIENT, ARTIFACT_PATH)
execute_local(cmd)

## BUILD can be in the setup remote file
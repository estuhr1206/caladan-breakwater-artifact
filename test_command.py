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

# distributing code-base
print("Distributing sources...")
repo_name = "caladan-breakwater-base"
# - server
cmd = "rsync -azh -e \"ssh -i {} -o StrictHostKeyChecking=no"\
        " -o UserKnownHostsFile=/dev/null\" --progress ../{}/caladan-all"\
        " {}@{}:~/{}"\
        .format(KEY_LOCATION, repo_name, USERNAME, SERVER, ARTIFACT_PATH)
execute_local(cmd)

directory_name = "run.20231018235706-caladan-memcached_trace"

print("producing graphs")
cmd = "cd ~ && python3 ~/{}/caladan-all/create_corecsv.py {}".format(ARTIFACT_PATH, directory_name)
execute_remote([server_conn], cmd, True)
cmd = "cd ~ && python3 ~/{}/caladan-all/graph.py {}".format(ARTIFACT_PATH, directory_name)
execute_remote([server_conn], cmd, True)

print("Graph files are on server. Feel free to use appropriate tools such as scp to move them.")

# print("Building caladan subcomponents on server via build_all.sh")
# cmd = "cd ~/{}/ && ./build_all.sh".format(ARTIFACT_PATH)
# execute_remote([server_conn], cmd, True)
# # Start shm query breakwater mem? what does this mean
# print("Starting shm query breakwater")
# cmd = "cd ~/{} && export SHMKEY=102 &&"\
#     " sudo ./caladan/apps/netbench/stress_shm_query membw:1000 > mem.log 2>&1".format(ARTIFACT_PATH)
# server_shmqueryBW_session = execute_remote([server_conn], cmd, False)
# cd ~/bw_artif && export SHMKEY=102 && sudo ./caladan/apps/netbench/stress_shm_query membw:1000 > mem.log 2>&1

# # Start shm query from I guess swaptions?
# print("Starting shm query swaptions")
# cmd = "cd ~/{} && export SHMKEY=102 &&"\
#     " sudo ./caladan/apps/netbench/stress_shm_query 102:1000:17  > swaptionsGC_shm_query.out 2>&1".format(ARTIFACT_PATH)
# server_shmquerySWAPTIONS_session = execute_remote([server_conn], cmd, False)

# cd ~/bw_artif && export SHMKEY=102 && sudo ./caladan/apps/netbench/stress_shm_query 102:1000:17  > swaptionsGC_shm_query.out 2>&1
#!/usr/bin/env python3

import paramiko
import os
from time import sleep
from util import *
from config_remote import *

################################
### Experiemnt Configuration ###
################################

# Server overload algorithm (breakwater, seda, dagor, nocontrol)
OVERLOAD_ALG = "breakwater"

# The number of client connections
NUM_CONNS = 1000

# List of offered load
OFFERED_LOADS = [500000, 1000000, 1500000, 2000000, 2500000, 3000000,
                 3500000, 4000000, 4500000, 5000000, 5500000, 6000000]
SINGLE_CLIENT_LOAD = 800000

# keys for memcached client, limited by this value. ex. rand() % MAX_KEY_INDEX is used as the key for the request
MAX_KEY_INDEX = 100000

# TODO generate_shenango_config
# not stated in N's, is this default?
ENABLE_DIRECTPATH = True
# runtime_spinning_kthreads being 0 in config means this is false.
SPIN_SERVER = False
# why is this true in N's config
DISABLE_WATCHDOG = True

NUM_CORES_SERVER = 10
NUM_CORES_CLIENT = 16
# end TODO generate_shenango_config

slo = 50
POPULATING_LOAD = 200000

############################
### End of configuration ###
############################

# Verify configs #
if OVERLOAD_ALG not in ["breakwater", "seda", "dagor", "nocontrol"]:
    print("Unknown overload algorithm: " + OVERLOAD_ALG)
    exit()

### Function definitions ###
def generate_shenango_config(is_server ,conn, ip, netmask, gateway, num_cores,
        directpath, spin, disable_watchdog):
    config_name = ""
    config_string = ""
    if is_server:
        config_name = "server.config"
        config_string = "host_addr {}".format(ip)\
                      + "\nhost_netmask {}".format(netmask)\
                      + "\nhost_gateway {}".format(gateway)\
                      + "\nruntime_kthreads {:d}".format(num_cores)
    else:
        config_name = "client.config"
        config_string = "host_addr {}".format(ip)\
                      + "\nhost_netmask {}".format(netmask)\
                      + "\nhost_gateway {}".format(gateway)\
                      + "\nruntime_kthreads {:d}".format(num_cores)

    if spin:
        config_string += "\nruntime_spinning_kthreads {:d}".format(num_cores)

    if directpath:
        config_string += "\nenable_directpath 1"

    if disable_watchdog:
        config_string += "\ndisable_watchdog 1"

    cmd = "cd ~/{} && echo \"{}\" > {} "\
            .format(ARTIFACT_PATH,config_string, config_name)

    return execute_remote([conn], cmd, True)
### End of function definition ###

NUM_AGENT = len(AGENTS)

# configure Shenango IPs for config
server_ip = "192.168.1.200"
# making this match N's config
client_ip = "192.168.1.7"
agent_ips = []
netmask = "255.255.255.0"
gateway = "192.168.1.1"

for i in range(NUM_AGENT):
    agent_ip = "192.168.1." + str(101 + i);
    agent_ips.append(agent_ip)

k = paramiko.RSAKey.from_private_key_file(KEY_LOCATION)
# connection to server
server_conn = paramiko.SSHClient()
server_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
server_conn.connect(hostname = SERVER, username = USERNAME, pkey = k)

# connection to client
client_conn = paramiko.SSHClient()
client_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client_conn.connect(hostname = CLIENT, username = USERNAME, pkey = k)

# connections to agents
agent_conns = []
for agent in AGENTS:
    agent_conn = paramiko.SSHClient()
    agent_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    agent_conn.connect(hostname = agent, username = USERNAME, pkey = k)
    agent_conns.append(agent_conn)

# Clean-up environment
# TODO add kill for garbage collector?
print("Cleaning up machines...")
cmd = "sudo killall -9 memcached & sudo killall -9 iokerneld"
execute_remote([server_conn], cmd, True, False)

cmd = "sudo killall -9 mcclient & sudo killall -9 iokerneld"
execute_remote([client_conn] + agent_conns,
               cmd, True, False)
sleep(1)


### IOKERNEL
# Old Execute IOKernel
# iok_sessions = []
# print("Executing IOKernel...")
# cmd = "cd ~/{}/shenango && sudo ./iokerneld".format(ARTIFACT_PATH)
# iok_sessions += execute_remote([server_conn, client_conn] + agent_conns,
#                                cmd, False)

iok_sessions = []
print("starting server IOKernel")
cmd = "sudo ~/{}/caladan/iokerneld ias"\
    " 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18  2>&1 | ts %s > iokernel.node-0.log".format(ARTIFACT_PATH)
iok_sessions += execute_remote([server_conn], cmd, False)

print("starting client IOKernel")
cmd = "sudo ~/{}/caladan/iokerneld simple 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18"\
    " 2>&1 | ts %s > iokernel.node-1.log".format(ARTIFACT_PATH)
iok_sessions += execute_remote([client_conn], cmd, False)
sleep(1)
### END IOKERNEL

### START server applications

# Start swaptions
print("Starting swaptions application")
cmd = "cd ~/{} && export SHMKEY=102 &&"\
    " parsec/pkgs/apps/swaptions/inst/amd64-linux.gcc-shenango-gc/bin/swaptions"\
    " swaptionsGC.config -ns 5000000 -sm 400 -nt 17  > swaptionsGC.out 2> swaptionsGC.err".format(ARTIFACT_PATH)
server_swaptions_session = execute_remote([server_conn], cmd, False)

# Start shm query breakwater mem? what does this mean
print("Starting shm query breakwater")
cmd = "cd ~/{} && export SHMKEY=102 &&"\
    " sudo ./caladan/apps/netbench/stress_shm_query membw:1000 > mem.log 2>&1".format(ARTIFACT_PATH)
server_shmqueryBW_session = execute_remote([server_conn], cmd, False)

# Start shm query from I guess swaptions?
print("Starting shm query swaptions")
cmd = "cd ~/{} && export SHMKEY=102 &&"\
    " sudo ./caladan/apps/netbench/stress_shm_query 102:1000:17  > swaptionsGC_shm_query.out 2>&1".format(ARTIFACT_PATH)
server_shmquerySWAPTIONS_session = execute_remote([server_conn], cmd, False)

# Start memcached
print("Starting Memcached server...")
# cmd = "cd ~/{} && sudo ./shenango-memcached/memcached {} server.config"\
#         " -p 8001 -v -c 32768 -m 64000 -b 32768 -o hashpower=18"\
#         .format(ARTIFACT_PATH, OVERLOAD_ALG)
cmd = "cd ~/{} && sudo ./memcached/memcached {} memcached.config -t 17"\
    " -U 5056 -p 5056 -c 32768 -m 32000 -b 32768 -o"\
    " hashpower=25,no_hashexpand,no_lru_crawler,no_lru_maintainer,idle_timeout=0,no_slab_reassign"\
    " > memcached.out 2> memcached.err".format(ARTIFACT_PATH, OVERLOAD_ALG)
server_memcached_session = execute_remote([server_conn], cmd, False)
server_memcached_session = server_memcached_session[0]

sleep(2)

### END SERVER APPLICATIONS
### TODO unsure what this entire section is doing
# print("Populating entries...")
# cmd = "cd ~/{} && sudo ./memcached-client/mcclient {} client.config client {:d} {} SET"\
#         " {:d} {:d} {:d} {:d} >stdout.out 2>&1"\
#         .format(ARTIFACT_PATH, OVERLOAD_ALG, NUM_CONNS, server_ip, MAX_KEY_INDEX,
#                 slo, 0, POPULATING_LOAD)
# client_session = execute_remote([client_conn], cmd, False)
# client_session = client_session[0]

# client_session.recv_exit_status()

# sleep(1)

# # Remove temporary output
# cmd = "cd ~/{} && rm output.csv output.json".format(ARTIFACT_PATH)
# execute_remote([client_conn], cmd, True, False)

# sleep(1)
### END TODO of the unsure section
duration = 20                   # duration in seconds now I think.
mean = 842                      # no clue. unused? not sure if it's unused.
distribution = "zero"           # not sure what this is. seems unused.
pps = 0.8                       # packets per second. seems unused.
samples = 1                     # no idea what this is. seems unused.
spps = 0.0                      # start packets per second, seems unused.
loadrate_duration = "{:d}:{:d}000000".format(SINGLE_CLIENT_LOAD, duration)    # load:runtime(us)
print("\tExecuting client...")
client_agent_sessions = []
cmd = "cd ~/{} && sudo ./memcached-client/mcclient {} client.config client {:d} {}"\
        " USR {:d} {:d} {:d} {:d} {:d} {:d} {} {:f} {:d} {:f} {} > 0-node-1.memcached.out 2> 0-node-1.memcached.err"\
        .format(ARTIFACT_PATH, OVERLOAD_ALG, NUM_CONNS, server_ip,
                MAX_KEY_INDEX, slo, NUM_AGENT, SINGLE_CLIENT_LOAD, duration, mean, distribution,
                pps, samples, spps, loadrate_duration)
client_agent_sessions += execute_remote([client_conn], cmd, False)

sleep(1)

for client_agent_session in client_agent_sessions:
    client_agent_session.recv_exit_status()

sleep(2)

### No need for this right now I think TODO
# for offered_load in OFFERED_LOADS:
#     print("Load = {:d}".format(offered_load))
#     # - clients
#     print("\tExecuting client...")
#     client_agent_sessions = []
#     cmd = "cd ~/{} && sudo ./memcached-client/mcclient {} client.config client {:d} {}"\
#             " USR {:d} {:d} {:d} {:d} >stdout.out 2>&1"\
#             .format(ARTIFACT_PATH, OVERLOAD_ALG, NUM_CONNS, server_ip,
#                     MAX_KEY_INDEX, slo, NUM_AGENT, offered_load)
#     client_agent_sessions += execute_remote([client_conn], cmd, False)

#     sleep(1)

#     # - Agents
#     print("\tExecuting agents...")
#     cmd = "cd ~/{} && sudo ./memcached-client/mcclient {} client.config agent {}"\
#             " >stdout.out 2>&1".format(ARTIFACT_PATH, OVERLOAD_ALG, client_ip)
#     client_agent_sessions += execute_remote(agent_conns, cmd, False)

#     # Wait for client and agents
#     print("\tWaiting for client and agents...")
#     for client_agent_session in client_agent_sessions:
#         client_agent_session.recv_exit_status()

#     sleep(2)


# Kill server
cmd = "sudo killall -9 memcached"
execute_remote([server_conn], cmd, True)

# Wait for the server
server_memcached_session.recv_exit_status()

# kill shm query
cmd = "sudo killall -9 stress_shm_query"
execute_remote([server_conn], cmd, True)
server_shmqueryBW_session.recv_exit_status()
server_shmquerySWAPTIONS_session.recv_exit_status()

# kill swaptions
cmd = "sudo killall -9 swaptions"
execute_remote([server_conn], cmd, True)
server_swaptions_session.recv_exit_status()

# Kill IOKernel
cmd = "sudo killall -9 iokerneld"
execute_remote([server_conn, client_conn] + agent_conns, cmd, True)

# Wait for IOKernel sessions
for iok_session in iok_sessions:
    iok_session.recv_exit_status()

# Close connections
server_conn.close()
client_conn.close()
for agent_conn in agent_conns:
    agent_conn.close()

# # Create output directory
# if not os.path.exists("outputs"):
#     os.mkdir("outputs")

# # Move output.csv and output.json
# print("Collecting outputs...")
# cmd = "scp -P 22 -i {} -o StrictHostKeyChecking=no {}@{}:~/{}/output.csv ./"\
#         " >/dev/null".format(KEY_LOCATION, USERNAME, CLIENT, ARTIFACT_PATH)
# execute_local(cmd)

# output_prefix = "{}".format(OVERLOAD_ALG)

# if SPIN_SERVER:
#     output_prefix += "_spin"

# if DISABLE_WATCHDOG:
#     output_prefix += "_nowd"

# output_prefix += "_memcached_nconn_{:d}".format(NUM_CONNS)

# # Print Headers
# header = "num_clients,offered_load,throughput,goodput,cpu,min,mean,p50,p90,p99,p999,p9999"\
#         ",max,lmin,lmean,lp50,lp90,lp99,lp999,lp9999,lmax,p1_win,mean_win,p99_win,p1_q,mean_q,p99_q,server:rx_pps"\
#         ",server:tx_pps,server:rx_bps,server:tx_bps,server:rx_drops_pps,server:rx_ooo_pps"\
#         ",server:winu_rx_pps,server:winu_tx_pps,server:win_tx_wps,server:req_rx_pps"\
#         ",server:resp_tx_pps,client:min_tput,client:max_tput"\
#         ",client:winu_rx_pps,client:winu_tx_pps,client:resp_rx_pps,client:req_tx_pps"\
#         ",client:win_expired_wps,client:req_dropped_rps"
# cmd = "echo \"{}\" > outputs/{}.csv".format(header, output_prefix)
# execute_local(cmd)

# cmd = "cat output.csv >> outputs/{}.csv".format(output_prefix)
# execute_local(cmd)

# # Remove temp outputs
# cmd = "rm output.csv"
# execute_local(cmd, False)

# print("Output generated: outputs/{}.csv".format(output_prefix))
# print("Done.")

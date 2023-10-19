###
### config_remote.py - configuration for remote servers
###

# Public domain or IP of server
SERVER = "hp106.utah.cloudlab.us"
# Public domain or IP of client
CLIENT = "hp111.utah.cloudlab.us"
# Public domain or IP of agents
AGENTS = [] # ["agent1.breakwater.com", "agent2.breakwater.com"]

# Username and SSH credential location to access
# the server, client, and agents via public IP
USERNAME = ""
KEY_LOCATION = ""

# Location of Shenango to be installed. With "", Shenango
# will be installed in the home direcotry
ARTIFACT_PARENT = ""

# Network RTT between client and server (in us)
# TODO this will not affect things. Please change bw_config.h in breakwater as appropriate
# before copying over to remote via github_files.py
NET_RTT = 5 # normally 10, N had it at 5
### End of config ###

ARTIFACT_PATH = ARTIFACT_PARENT
if ARTIFACT_PATH != "":
    ARTIFACT_PATH += "/"
ARTIFACT_PATH += "bw_artif"

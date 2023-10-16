#!/usr/bin/env python3

import os
from util import *
from config_remote import *

# # modifying config in breakwater/src/bw_config.h
# # TODO or just note that it can be done before copying the files over in the bw_config.h
# cmd = "sed -i'.orig' -e \'s/#define SBW_RTT_US.*/#define SBW_RTT_US\\t\\t\\t{:d}/g\'"\
#         " configs/bw_config.h".format(NET_RTT)
# execute_local(cmd)

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
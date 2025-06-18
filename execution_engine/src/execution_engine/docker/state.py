import os

import docker


client = docker.from_env()

host_uid = os.getuid()
host_gid = os.getgid()

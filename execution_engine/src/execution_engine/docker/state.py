import os

import docker


def shutdown():
    client.close()


client = docker.from_env()

host_uid = os.getuid()
host_gid = os.getgid()

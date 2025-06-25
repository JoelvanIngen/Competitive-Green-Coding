import os

import docker


def shutdown():
    client.close()


client = docker.from_env()  # pylint: disable=c-extension-no-member

host_uid = os.getuid()
host_gid = os.getgid()

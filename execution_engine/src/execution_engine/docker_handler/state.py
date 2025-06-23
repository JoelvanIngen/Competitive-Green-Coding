import os

import docker


def shutdown():
    client.close()

print(f"DEBUG: 'docker' module is from: {docker.__file__}")

client = docker.from_env()
print(f"DEBUG: 'client' object type: {type(client)}")
print(f"DEBUG: 'client.images' type: {type(client.images)}")

host_uid = os.getuid()
host_gid = os.getgid()

import docker


def _build_images():
    """
    Builds runtime images from Dockerfiles for all registered languages
    """


client = docker.from_env()

_build_images()

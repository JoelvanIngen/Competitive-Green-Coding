import os

from loguru import logger

from common.languages import LanguageInfo
from execution_engine.config import settings
from execution_engine.docker_handler.state import client


def build_image(language: LanguageInfo):
    dockerfile_path = os.path.join(settings.DOCKERFILES_BASE_PATH, language.name, "Dockerfile")
    build_context = os.path.dirname(dockerfile_path)
    image_tag = language.image

    logger.info(f"Building docker image {image_tag}")
    client.images.build(
        path=build_context,
        dockerfile=dockerfile_path,
        tag=image_tag,
        rm=True,  # Remove intermediate containers (if we decide to use them)
    )
    logger.info(f"Built docker image {image_tag}")

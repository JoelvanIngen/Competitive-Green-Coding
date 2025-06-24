import shutil

from execution_engine.docker_handler.runconfig import RunConfig


def clean_env(config: RunConfig):
    shutil.rmtree(config.tmp_dir)

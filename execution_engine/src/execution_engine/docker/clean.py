import shutil

from execution_engine.docker.runconfig import RunConfig


def clean_env(config: RunConfig):
    shutil.rmtree(config.tmp_dir)

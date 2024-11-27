# utils.py

import yaml
from box import Box

def load_yaml(config_path: str) -> Box:
    """
    YAML 파일을 load하는 함수

    Parameters
    ----------
    config_path : str
        YAML 파일 경로

    Returns
    -------
    Box 
        Box 개체
    """
    with open(config_path) as f:
        config_yaml = yaml.load(f, Loader=yaml.FullLoader)
        config = Box(config_yaml)

    return config
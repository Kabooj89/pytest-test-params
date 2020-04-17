"""
@author:
        Mohammad Kabajah
@Contact:
        kabajah.mohammad@gmail.com
@date:
        April 28, 2019
@Purpose:
        plugin pytest-testparams conftest for shared fixture
"""
pytest_plugins = 'nala.utilities.pytest_utils.testparams.testparams'

import json

import pytest

from nala.modules.utils import log
from nala.utilities.pytest_utils.testparams.testparams import params


@pytest.fixture
def test_config(request):
    """
    fixture to recognize the configuration for test given (node)
    Args:
        request: pytest request

    Returns:
        dict: test_config for that test
    """
    test_path = str(request.node.name)
    test_file_name = test_path.split("/")[-1].replace(".py", "")
    try:
        test_config = params[test_file_name]
        log.info("[*] Current Configurations passed to test is:")
        log.info(json.dumps(test_config, indent=3))
        return test_config
    except KeyError as e:
        log.error("no available configuration section in the yaml you provided that match the test: {0}".format(
            test_file_name))
        raise KeyError(str(e))

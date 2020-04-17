"""
@author:
        Mohammad Kabajah
@Contact:
        kabajah.mohammad@gmail.com
@date:
        April 28, 2019
@Purpose:
        example to test the pligin pytest-testparams
        configuration to put is: -s -v --tp-file= ~/utilities/pytest_utils/testparams/tests/conf_files/test_testparams.yml --tp-format=yaml
"""
from nala.modules.utils import log


def test_demo(test_config):
    log.debug("i am at test demo")
    assert test_config["name"] == "test_demo"


def test_demo1(test_config):
    log.debug("i am at test demo1")
    assert test_config["name"] == "test_demo1"


def test_demo2(test_config):
    log.debug("i am at test demo2")
    assert test_config["name"] == "test_demo2"

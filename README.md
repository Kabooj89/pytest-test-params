testparams-pytest:
=================

Test Parameters plugin for pytest.

----


[Features]:
==========
testparams is a plugin used for passing parameters data to the tests being executed.

Currently configuration files in the following formats should be supported:

- YAML (via `PyYAML <http://pypi.python.org/pypi/PyYAML/>`_)
- JSON (via `JSON <http://docs.python.org/library/json.html>`_)
- INI (via `ConfigParser <http://docs.python.org/lib/module-ConfigParser.html>`_)
- Pure Python (via Exec)

The plugin is ``meant`` to be flexible, ergo the support of exec'ing arbitrary
python files as configuration files with no checks. The default format is
assumed to be PyYaml yaml-style format.

If multiple files are provided, the objects are merged. Later settings will
override earlier ones.

The plugin provides a method of overriding certain parameters from the command
line (assuming that the main "config" object is a dict) and can easily have
additional parsers added to it.

A configuration file may not be provided. In this case, the config object is an
emtpy dict. Any command line "overriding" paramters will be added to the dict.


[Requirements]:
===============

requires pytest>=3.5.0


[Installation]: 
==============

[*] need to add to your conftest the following: 
    pytest_plugins = "nala.utilities.pytest_utils.testparams"
    
[*] hope to add it in PyPI soon [IN Progress]
    You can install "pytest-testparams" via `pip`_ from `PyPI`_:: 
    
        $ python3 -m pip install pytest-testparams


[Usage]:
========

Tests can import the "config" singleton from testparams::

    from <path to testparams> import params

By default, YAML files parse into a nested dictionary, and ConfigParser ini
files are also collapsed into a nested dictionary for foo[bar][baz] style
access. Tests can obviously access configuration data by referencing the
relevant dictionary keys::

    from testparams import params
    def test_foo():
        target_server_ip = params['servers']['webapp_ip']

``Warning``: Given this is just a dictionary singleton, tests can easily write
into the configuration. This means that your tests can write into the config
space and possibly alter it. This also means that threaded access into the
configuration can be interesting.

When using pure python configuration - obviously the "sky is the the limit" -
given that the configuration is loaded via an exec, you could potentially
modify pytest, the plugin, etc. However, if you do not export a config{} dict
as part of your python code, you obviously won't be able to import the
config object from testparams.

When using YAML-style configuration, you get a lot of the power of pure python
without the danger of unprotected exec() - you can obviously use the pyaml
python-specific objects and all of the other YAML creamy goodness.

Defining a configuration file
-----------------------------

Simple ConfigParser style::

    [myapp_servers]
    main_server = 10.1.1.1
    secondary_server = 10.1.1.2

So your tests access the config options like this::

    from utilities.pytest_utils.testparams import params
    def test_foo():
        main_server = params['myapp_servers']['main_server']

YAML style configuration::
    myapp:
        servers:
            main_server: 10.1.1.1
            secondary_server: 10.1.1.2

And your tests can access it thus::

    from utilities.pytest_utils.testparams import params
    def test_foo():
        main_server = params['myapp']['servers']['main_server']

Python configuration file::

    import socket

    global params
    params = {}
    possible_main_servers = ['10.1.1.1', '10.1.1.2']

    for srv in possible_main_servers:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((srv, 80))
        except:
            continue
        s.close()
        params['main_server'] = srv
        break

And lo, the params is thus::

    from utilities.pytest_utils.testparams import params
    def test_foo():
        main_server = params['main_server']

If you need to put python code into your configuration, you either need to use
the python-params file faculties, or you need to use the !!python tags within
PyYAML/YAML - raw ini files no longer have any sort of eval magic.

[Defining in conftest file]:
================================

 This is an example how you can use it in your conftest in case you don't prefer to import the params dictionary in tests.
 
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
  
 that way you can write the test as the following: 
 
    def test_demo(test_config):
        log.debug("i am at test demo")
        assert test_config["name"] == "test_demo"
 > check the examples at: nala/utilities/pytest_utils/testparams/tests


[Command line options]:
======================

the plugin adds the following command line flags to pytest::

    --tp-file=TEST_PARAMS  Parmaters file to parse and pass to tests
                          [PY_TEST_PARAMS_FILE]
                          If this is specified multiple times, all files
                          will be parsed. In all formats except python,
                          previous contents are preserved and the params
                          are merged.

    --tp-format=TEST_PARAMS_FORMAT  Test params file format, default is
                                  PyYAML yaml format
                                  [PY_TEST_PARAMS_FILE_FORMAT]

    --tp=OVERRIDES        Option:Value specific overrides.
                          Exampe: Key_1.Key_2.Key_2:value 

    --tp-exact            Optional: Do not explode periods in override keys to
                          individual keys within the params dict, instead treat
                          them as params[my.toplevel.key] ala sqlalchemy.url in
                          pylons.


[Authors]:
==========

    Mohammad Kabajah - Initial work
    See also the list of contributors who participated in this project.
        TO ADD
        

[License]:
==========

    Copyright(C) 2019 Annapurna Lab an Amazon Company, LTD.
        All Right Reserved.
 
    Dissemination of this information or reproduction of this material
    is strictly forbidden unless prior written permission is obtained
    from Annapurna Lab, LTD.




[Issues]:
=========
    
    1- need to get solution for multilevel in ini files 
    2- insert argument types in ini files currently all is string
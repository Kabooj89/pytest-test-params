"""
@author:
        Mohammad Kabajah
@date:
        March 18, 2019
@Purpose:
       is a py.test plugin which provides passing test-specific (or test-run specific) params data to
       the tests being executed. singleton params dict has been used.
"""
__version__ = 0.1

import codecs
import json
import logging
import os
import re

try:
    import yaml
except (ImportError):
    raise Exception('unable to import YAML package. Can not continue.')

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
# Import, or define, NullHandler
try:
    from logging import NullHandler
except ImportError:
    from logging import Handler


    class NullHandler(Handler):
        """No-op handler."""

        def emit(self, record):
            """Intentionally do nothing."""
            pass

log = logging.getLogger(__name__)
log.addHandler(NullHandler())

warning = "Cannot access the test params because the plugin has not \
been activated.  Did you specify --tc or any other command line option?"

# singleton dictionary
params = {}


def to_list(val):
    """
    Convert a value that may be a list or a (possibly comma-separated)
    string into a list. The exception: None is returned as None, not [None].
    Args:
        val: value unknown type
    Returns:
        list
    """
    if val is None:
        return None
    try:
        # might already be a list
        val.extend([])
        return val
    except AttributeError:
        pass
    # might be a string
    try:
        return re.split(r'\s*,\s*', val)
    except TypeError:
        # who knows...
        return list(val)


def merge_map(original, to_add):
    """
    Merges a new map of configuration recursively with an older one
    Args:
        original(dict): the original dict
        to_add(dict): the new dict to map recursively
    """
    for key, value in to_add.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            merge_map(original[key], value)
        else:
            original[key] = value


def load_yaml(yaml_file, encoding):
    """
    Load the passed in yaml configuration file
    Args:
        yaml_file(str): path to yaml file
        encoding(str): encoding type , Default utf-8
    """
    global params
    parsed_config = yaml.load(codecs.open(os.path.expanduser(yaml_file), 'r', encoding).read())
    merge_map(params, parsed_config)


def load_ini(ini_file, encoding):
    """
    Parse and collapse a ConfigParser-Style ini file into a two-level
    params structure.
    Args:
        ini_file(str): path to ini file
        encoding(str): encoding type , Default utf-8
    """
    global params
    tmpconfig = ConfigParser.ConfigParser()
    # Overriding optionxform method to avoid lowercase conversion
    tmpconfig.optionxform = lambda override: override
    with codecs.open(os.path.expanduser(ini_file), 'r', encoding) as f:
        try:
            tmpconfig.read_file(f)
        except AttributeError:
            tmpconfig.readfp(f)

    parsed_config = {}
    for section in tmpconfig.sections():
        parsed_config[section] = {}
        for option in tmpconfig.options(section):
            parsed_config[section][option] = tmpconfig.get(section, option)
    merge_map(params, parsed_config)


def load_python(py_file, encoding):
    """
    This will exec the defined python file into the params variable -
    the implicit assumption is that the python is safe, well formed and will
    not do anything bad. This is also dangerous.
    Args:
        py_file(str): path to py file
        encoding(str): encoding type , Default utf-8
    """
    exec(codecs.open(os.path.expanduser(py_file), 'r', encoding).read())


def load_json(json_file, encoding):
    """
    This will use the json module to to read in the params json file.
    Args:
        json_file(str): path to json file
        encoding(str): encoding type by default its utf-8
    """
    global params
    with codecs.open(os.path.expanduser(json_file), 'r', encoding=encoding) as handle:
        parsed_config = json.load(handle)
    merge_map(params, parsed_config)


env_opt = "PY_TEST_PARAMS_FILE"
format_option = "yaml"
encoding_option = 'utf-8'
valid_loaders = {'yaml': load_yaml, 'ini': load_ini, 'python': load_python, 'json': load_json}


def pytest_addoption(parser,
                     env=os.environ):
    """
    Define the command line options for the plugin.
    """

    group = parser.getgroup('test-params')
    group.addoption('--tp-file',
                    action='append',
                    dest='test_params',
                    default=[env.get(env_opt)],
                    help="parameters file to parse and pass to tests"
                         " [PY_TEST_PARAMS_FILE]")
    group.addoption('--tp-file-encoding',
                    action='store',
                    dest='test_params_encoding',
                    default=env.get('PY_TEST_PARAMS_FILE_ENCODING') or encoding_option,
                    help="Test params file encoding, default is utf-8"
                         " [PY_TEST_PARAMS_FILE_ENCODING]")
    group.addoption('--tp-format',
                    action='store',
                    dest='test_params_format',
                    default=env.get('PY_TEST_PARAMS_FILE_FORMAT') or format_option,
                    help="Test params file format, default is configparser ini format"
                         " [PY_TEST_PARAMS_FILE_FORMAT]")
    group.addoption('--tp',
                    action='append',
                    dest='overrides',
                    default=[],
                    help="Option:Value specific overrides.")
    group.addoption('--tp-exact',
                    action='store_true',
                    dest='exact',
                    default=False,
                    help="Optional: Do not explode periods in override keys to "
                         "individual keys within the params dict, instead treat them"
                         " as params[my.toplevel.key] ala sqlalchemy.url in pylons")


def pytest_configure(config):
    """ Call the super and then validate and call the relevant parser for
    the configuration file passed in """
    if not config.getoption('test_params') and not config.getoption('overrides'):
        return
    format_option = "yaml"
    if config.getoption('test_params_format'):
        format_option = config.getoption('test_params_format')
        if format_option not in valid_loaders.keys():
            raise Exception('%s is not a valid configuration file format' \
                            % format_option)

    # Load the configuration file:
    for configfile in config.getoption('test_params'):
        if configfile:
            valid_loaders[format_option](configfile,
                                         config.getoption('test_params_encoding'))

    overrides = to_list(config.getoption('overrides')) or []
    for override in overrides:
        keys, val = override.split(":", 1)
        if config.getoption('exact'):
            config[keys] = val
        else:
            # Create all *parent* keys that may not exist in the config
            section = params
            keys = keys.split('.')
            for key in keys[:-1]:
                if key not in section:
                    section[key] = {}
                section = section[key]

            # Finally assign the value to the last key
            key = keys[-1]
            section[key] = val


# Use an environment hack to allow people to set a params file to auto-load
# in case they want to put tests they write through pychecker or any other
# syntax thing which does an execute on the file.
if 'PYTEST_TESTPARAMS_AUTOLOAD_YAML' in os.environ:
    load_yaml(os.environ['PYTEST_TESTPARAMS_AUTOLOAD_YAML'], encoding='utf-8')

if 'PYTEST_TESTPARAMS_AUTOLOAD_INI' in os.environ:
    load_ini(os.environ['PYTEST_TESTPARAMS_AUTOLOAD_INI'], encoding='utf-8')

if 'PYTEST_TESTPARAMS_AUTOLOAD_PYTHON' in os.environ:
    load_python(os.environ['PYTEST_TESTPARAMS_AUTOLOAD_PYTHON'], encoding='utf-8')

if 'PYTEST_TESTPARAMS_AUTOLOAD_JSON' in os.environ:
    load_json(os.environ['PYTEST_TESTPARAMS_AUTOLOAD_JSON'], encoding='utf-8')

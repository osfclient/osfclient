from mock import call
from mock import Mock
from mock import patch

import pytest

from osfclient.tests.mocks import MockArgs

from osfclient import cli


@patch('osfclient.cli.os.path.exists', return_value=True)
@patch('osfclient.cli.configparser.ConfigParser')
def test_config_file(MockConfigParser, os_path_exists):
    MockConfigParser().__getitem__ = Mock(return_value={'project': '1234'})

    config = cli.config_from_file()

    assert config == {'project': '1234'}

    assert call.read('.osfcli.config') in MockConfigParser().mock_calls
    assert call('osf') in MockConfigParser().__getitem__.mock_calls


def test_config_from_env_replace_username():
    def simple_getenv(key):
        if key == 'OSF_USERNAME':
            return 'theusername'

    with patch('osfclient.cli.os.getenv', side_effect=simple_getenv):
        config = cli.config_from_env({'username': 'notusername'})

    assert config == {'username': 'theusername'}


def test_config_from_env_username():
    def simple_getenv(key):
        if key == 'OSF_USERNAME':
            return None

    with patch('osfclient.cli.os.getenv', side_effect=simple_getenv):
        config = cli.config_from_env({'username': 'theusername'})

    assert config == {'username': 'theusername'}


def test_config_from_env_replace_project():
    def simple_getenv(key):
        if key == 'OSF_PROJECT':
            return 'theproject'

    with patch('osfclient.cli.os.getenv', side_effect=simple_getenv):
        config = cli.config_from_env({'project': 'notproject'})

    assert config == {'project': 'theproject'}


def test_config_from_env_project():
    def simple_getenv(key):
        if key == 'OSF_PROJECT':
            return None

    with patch('osfclient.cli.os.getenv', side_effect=simple_getenv):
        config = cli.config_from_env({'project': 'theproject'})

    assert config == {'project': 'theproject'}


def test_config_project():
    # No project in args or the config, should sys.exit(1)
    args = MockArgs(project=None)

    def simple_config(key):
        return {}

    with patch('osfclient.cli.config_from_env', side_effect=simple_config):
        with pytest.raises(SystemExit) as e:
            cli._setup_osf(args)

    expected = ('specify a project ID via the command line, configuration '
                'file or environment variable')
    assert expected in e.value.args[0]


def test_password_prompt():
    # No password in config should trigger the password prompt
    # when an username is specified
    args = MockArgs(project='test', username='theusername')
    with patch('getpass.getpass') as getpass:
        getpass.return_value = 'test_password'
        osf = cli._setup_osf(args)
        assert osf.password == 'test_password'

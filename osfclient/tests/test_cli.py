from mock import call
from mock import patch
from mock import mock_open

import pytest

from osfclient.tests.mocks import MockArgs

from osfclient import cli
from osfclient.exceptions import UnauthorizedException


@patch('osfclient.cli.os.path.exists', return_value=True)
@patch('osfclient.cli.configparser.ConfigParser')
def test_config_file(MockConfigParser, os_path_exists):
    MockConfigParser.return_value.items.return_value = (('project', '1234'),)
    config = cli.config_from_file()

    assert config == {'project': '1234'}

    assert call().read('.osfcli.config') in MockConfigParser.mock_calls
    assert call().items('osf') in MockConfigParser.mock_calls


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


@patch('osfclient.cli.config_from_file', return_value={'username': 'tu2',
                                                       'project': 'pj2'})
def test_init(config_from_file):
    mock_open_func = mock_open()

    with patch('osfclient.cli.open', mock_open_func):
        with patch('osfclient.cli.input', side_effect=['test-user', '']):
            cli.init(MockArgs())

    assert call('.osfcli.config', 'w') in mock_open_func.mock_calls
    assert call().write('username = test-user\n') in mock_open_func.mock_calls
    assert call().write('project = pj2\n') in mock_open_func.mock_calls
    assert call().write('[osf]\n') in mock_open_func.mock_calls


@patch('osfclient.cli.config_from_env', return_value={'username': 'tu2',
                                                      'project': 'pj2'})
def test_might_need_auth_unauthorized(config_from_file):
    mock_args = MockArgs(project='test', username='theusername')

    @cli.might_need_auth
    def dummy(x):
        raise UnauthorizedException()

    with pytest.raises(SystemExit) as e:
        dummy(mock_args)

    assert "not authorized to access" in str(e.value)


@patch('osfclient.cli.config_from_env', return_value={'project': 'pj2'})
def test_might_need_auth_no_username(config_from_file):
    mock_args = MockArgs(project='test')

    @cli.might_need_auth
    def dummy(x):
        raise UnauthorizedException()

    with pytest.raises(SystemExit) as e:
        dummy(mock_args)

    assert "set a username" in str(e.value)

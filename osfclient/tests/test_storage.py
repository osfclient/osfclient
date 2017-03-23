from unittest.mock import patch
import pytest

from osfclient.models import OSFCore
from osfclient.models import Storage
from osfclient.models import File

from osfclient.tests import fake_responses
from osfclient.tests.mocks import FakeResponse


@patch.object(OSFCore, '_get')
def test_iterate_files(OSFCore_get):
    store = Storage({})
    store._files_url = 'https://api.osf.io/v2//nodes/f3szh/files/osfstorage'

    json = fake_responses.files_node('f3szh', 'osfstorage',
                                     ['hello.txt', 'bye.txt'])
    response = FakeResponse(200, json)
    OSFCore_get.return_value = response

    files = list(store.files)

    assert len(files) == 2
    for file_ in files:
        assert isinstance(file_, File)

    OSFCore_get.assert_called_once_with(
        'https://api.osf.io/v2//nodes/f3szh/files/osfstorage')

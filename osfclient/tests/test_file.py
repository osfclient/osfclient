from unittest.mock import patch

from osfclient.models import OSFCore
from osfclient.models import File
from osfclient.models import Folder

from osfclient.tests import fake_responses
from osfclient.tests.mocks import FakeResponse

_files_url = 'https://api.osf.io/v2//nodes/f3szh/files/osfstorage/foo123'


@patch.object(OSFCore, '_get')
def test_iterate_files(OSFCore_get):
    store = Folder({})
    store._files_url = _files_url

    json = fake_responses.files_node('f3szh', 'osfstorage',
                                     ['foo/hello.txt', 'foo/bye.txt'])
    response = FakeResponse(200, json)
    OSFCore_get.return_value = response

    files = list(store.files)

    assert len(files) == 2
    for file_ in files:
        assert isinstance(file_, File)
        assert file_.session == store.session

    OSFCore_get.assert_called_once_with(
        'https://api.osf.io/v2//nodes/f3szh/files/osfstorage/foo123')


@patch.object(OSFCore, '_get')
def test_iterate_folders(OSFCore_get):
    store = Folder({})
    store._files_url = _files_url

    json = fake_responses.files_node('f3szh', 'osfstorage',
                                     folder_names=['foo/bar', 'foo/baz'])
    response = FakeResponse(200, json)
    OSFCore_get.return_value = response

    folders = list(store.folders)

    assert len(folders) == 2
    for folder in folders:
        assert isinstance(folder, Folder)
        assert folder.session == store.session
        assert folder.name in ('foo/bar', 'foo/baz')

    OSFCore_get.assert_called_once_with(
        'https://api.osf.io/v2//nodes/f3szh/files/osfstorage/foo123')


def test_iterate_files_and_folders():
    # check we do not attempt to recurse into the subfolders
    store = Folder({})
    store._files_url = _files_url

    json = fake_responses.files_node('f3szh', 'osfstorage',
                                     file_names=['hello.txt', 'bye.txt'],
                                     folder_names=['bar'])
    top_level_response = FakeResponse(200, json)

    def simple_OSFCore_get(url):
        if url == store._files_url:
            return top_level_response
        else:
            print(url)
            raise ValueError()

    with patch.object(OSFCore, '_get',
                      side_effect=simple_OSFCore_get) as mock_osf_get:
        files = list(store.files)

    assert len(files) == 2
    for file_ in files:
        assert isinstance(file_, File)
        assert file_.session == store.session
        assert file_.name in ('hello.txt', 'bye.txt')

    # check we did not try to recurse into subfolders
    expected = [((_files_url,),)]
    assert mock_osf_get.call_args_list == expected

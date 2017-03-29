from unittest.mock import patch

from osfclient.models import OSFCore
from osfclient.models import Storage
from osfclient.models import File
from osfclient.models import Folder

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
        assert file_.session == store.session

    OSFCore_get.assert_called_once_with(
        'https://api.osf.io/v2//nodes/f3szh/files/osfstorage')


@patch.object(OSFCore, '_get')
def test_iterate_folders(OSFCore_get):
    store = Storage({})
    store._files_url = 'https://api.osf.io/v2//nodes/f3szh/files/osfstorage'

    json = fake_responses.files_node('f3szh', 'osfstorage',
                                     folder_names=['foo', 'bar'])
    response = FakeResponse(200, json)
    OSFCore_get.return_value = response

    folders = list(store.folders)

    assert len(folders) == 2
    for folder in folders:
        assert isinstance(folder, Folder)
        assert folder.session == store.session
        assert folder.name in ('foo', 'bar')

    OSFCore_get.assert_called_once_with(
        'https://api.osf.io/v2//nodes/f3szh/files/osfstorage')


def test_iterate_files_and_folders():
    # check we attempt to recurse into the folders
    store = Storage({})
    store._files_url = 'https://api.osf.io/v2//nodes/f3szh/files/osfstorage'

    json = fake_responses.files_node('f3szh', 'osfstorage',
                                     file_names=['hello.txt', 'bye.txt'],
                                     folder_names=['foo'])
    top_level_response = FakeResponse(200, json)

    second_level_url = ('https://api.osf.io/v2/nodes/9zpcy/files/' +
                        'osfstorage/foo123/')
    json = fake_responses.files_node('f3szh', 'osfstorage',
                                     file_names=['foo/hello2.txt',
                                                 'foo/bye2.txt'])
    second_level_response = FakeResponse(200, json)

    def simple_OSFCore_get(url):
        if url == store._files_url:
            return top_level_response
        elif url == second_level_url:
            return second_level_response
        else:
            print(url)
            raise ValueError()

    with patch.object(OSFCore, '_get',
                      side_effect=simple_OSFCore_get) as mock_osf_get:
        files = list(store.files)

    assert len(files) == 4
    for file_ in files:
        assert isinstance(file_, File)
        assert file_.session == store.session

    # check right URLs are called in the right order
    expected = [((store._files_url,),), ((second_level_url,),)]
    assert mock_osf_get.call_args_list == expected

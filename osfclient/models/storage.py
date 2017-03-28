import os

from .core import OSFCore
from .core import FolderExistsException
from .file import File
from .file import Folder


class Storage(OSFCore):
    def _update_attributes(self, storage):
        if not storage:
            return

        # XXX does this happen?
        if 'data' in storage:
            storage = storage['data']

        self.id = self._get_attribute(storage, 'id')

        self.path = self._get_attribute(storage, 'attributes', 'path')
        self.name = self._get_attribute(storage, 'attributes', 'name')
        self.node = self._get_attribute(storage, 'attributes', 'node')
        self.provider = self._get_attribute(storage, 'attributes', 'provider')

        self._files_key = ('relationships', 'files', 'links', 'related',
                           'href')
        self._files_url = self._get_attribute(storage, *self._files_key)

        self._new_folder_url = self._get_attribute(storage,
                                                   'links', 'new_folder')
        self._new_file_url = self._get_attribute(storage, 'links', 'upload')

    def __str__(self):
        return '<Storage [{0}]>'.format(self.id)

    @property
    def files(self):
        """Iterate over all files in this storage."""
        files = self._follow_next(self._files_url)

        while files:
            file = files.pop()
            kind = self._get_attribute(file, 'attributes', 'kind')
            if kind == 'file':
                yield File(file, self.session)
            else:
                # recurse into a folder and add entries to `files`
                url = self._get_attribute(file, *self._files_key)
                files.extend(self._follow_next(url))

    def _create_folder(self, name, exist_ok=False):
        # Create a new sub-folder
        response = self._put(self._new_folder_url,
                             params={'name': name})
        if response.status_code == 409 and not exist_ok:
            raise FolderExistsException(name)

        elif response.status_code == 201:
            return Folder(response.json(), self.session)

        else:
            raise RuntimeError("Response has status code {} while creating "
                               "folder {}.".format(response.status_code,
                                                   name))

    def create_file(self, path, fp):
        """Store a new file at `path` in this storage.

        The contents of the file descriptor `fp` (opened in 'rb' mode)
        will be uploaded to `path` which is the full path at
        which to store the file.
        """
        path = os.path.normpath(path)
        directory, fname = os.path.split(path)
        import pdb; pdb.set_trace()
        self._create_folder(directory)

import os
import six

from .core import OSFCore
from .file import ContainerMixin
from .file import File
from ..utils import norm_remote_path
from ..utils import file_empty


if six.PY2:
    class FileExistsError(OSError):
        """
        Exception raised when a file already exists
        Standard in Python 3
        """


class Storage(OSFCore, ContainerMixin):
    _files_key = ('relationships', 'files', 'links', 'related', 'href')

    def _update_attributes(self, storage):
        if not storage:
            return

        self.id = self._get_attribute(storage, 'id')

        self.path = self._get_attribute(storage, 'attributes', 'path')
        self.name = self._get_attribute(storage, 'attributes', 'name')
        self.node = self._get_attribute(storage, 'attributes', 'node')
        self.provider = self._get_attribute(storage, 'attributes', 'provider')

        self._files_url = self._get_attribute(storage, *self._files_key)

        self._new_folder_url = self._get_attribute(storage,
                                                   'links', 'new_folder')
        self._new_file_url = self._get_attribute(storage, 'links', 'upload')

    def __str__(self):
        return '<Storage [{0}]>'.format(self.id)

    @property
    def files(self):
        """Iterate over all files in this storage.

        Recursively lists all files in all subfolders.
        """
        return self._iter_children(self._files_url, 'file', File,
                                   self._files_key)

    def create_file(self, path, fp, update=False):
        """Store a new file at `path` in this storage.

        The contents of the file descriptor `fp` (opened in 'rb' mode)
        will be uploaded to `path` which is the full path at
        which to store the file.

        To update an existing file set `update=True`.
        """
        if 'b' not in fp.mode:
            raise ValueError("File has to be opened in binary mode.")

        # all paths are assumed to be absolute
        path = norm_remote_path(path)

        directory, fname = os.path.split(path)
        directories = directory.split('/')
        # navigate to the right parent object for our file
        parent = self
        for directory in directories:
            # skip empty directory names
            if directory:
                parent = parent.create_folder(directory, exist_ok=True)

        url = parent._new_file_url
        # peek at the file to check if it is an ampty file which needs special
        # handling in requests. If we pass a file like object to data that
        # turns out to be of length zero then no file is created on the OSF
        if file_empty(fp):
            response = self._put(url, params={'name': fname}, data=b'')
        else:
            response = self._put(url, params={'name': fname}, data=fp)

        if response.status_code == 409:
            if not update:
                raise FileExistsError(path)

            else:
                # find the upload URL for the file we are trying to update
                for file_ in self.files:
                    if norm_remote_path(file_.path) == path:
                        # in the process of attempting to upload the file we
                        # moved through it -> reset read position to beginning
                        # of the file
                        fp.seek(0)
                        file_.update(fp)
                        break
                else:
                    raise RuntimeError("Could not create a new file at "
                                       "({}) nor update it.".format(path))

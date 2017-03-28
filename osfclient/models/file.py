import shutil

from .core import OSFCore
from .core import FolderExistsException


class File(OSFCore):
    def _update_attributes(self, file):
        if not file:
            return

        # XXX does this happen?
        if 'data' in file:
            file = file['data']

        self.id = self._get_attribute(file, 'id')

        self._endpoint = self._get_attribute(file, 'links', 'self')
        self._download_url = self._get_attribute(file, 'links', 'download')
        self.osf_path = self._get_attribute(file, 'attributes', 'path')
        self.path = self._get_attribute(file,
                                        'attributes', 'materialized_path')
        self.name = self._get_attribute(file, 'attributes', 'name')
        self.date_created = self._get_attribute(file,
                                                'attributes', 'date_created')
        self.date_modified = self._get_attribute(file,
                                                 'attributes', 'date_modified')

    def __str__(self):
        return '<File [{0}, {1}]>'.format(self.id, self.path)

    def write_to(self, fp):
        """Write contents of this file to a local file.

        Pass in a filepointer `fp` that has been opened for writing in
        binary mode.
        """
        if 'b' not in fp.mode:
            raise ValueError("File has to be opened in binary mode.")

        response = self._get(self._download_url)
        if response.status_code == 200:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, fp)

        else:
            raise RuntimeError("Response has status "
                               "code {}.".format(response.status_code))


class Folder(OSFCore):
    def _update_attributes(self, file):
        if not file:
            return

        # XXX does this happen?
        if 'data' in file:
            file = file['data']

        self.id = self._get_attribute(file, 'id')

        self._endpoint = self._get_attribute(file, 'links', 'self')

        self._delete_url = self._get_attribute(file, 'links', 'delete')
        self._new_folder_url = self._get_attribute(file, 'links', 'new_folder')
        self._new_file_url = self._get_attribute(file, 'links', 'upload')
        self._move_url = self._get_attribute(file, 'links', 'move')

        self._files_key = ('relationships', 'files', 'links', 'related',
                           'href')
        self._files_url = self._get_attribute(file, *self._files_key)

        self.osf_path = self._get_attribute(file, 'attributes', 'path')
        self.path = self._get_attribute(file,
                                        'attributes', 'materialized_path')
        self.name = self._get_attribute(file, 'attributes', 'name')
        self.date_created = self._get_attribute(file,
                                                'attributes', 'date_created')
        self.date_modified = self._get_attribute(file,
                                                 'attributes', 'date_modified')

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

    @property
    def folders(self):
        """Iterate over top-level folders in this storage"""
        children = self._follow_next(self._files_url)

        while children:
            child = children.pop()
            kind = self._get_attribute(child, 'attributes', 'kind')
            if kind == 'folder':
                yield Folder(child, self.session)

    def __str__(self):
        return '<Folder [{0}, {1}]>'.format(self.id, self.path)

    def create_folder(self, name, exist_ok=False):
        # Create a new sub-folder
        response = self._put(self._new_folder_url,
                             params={'name': name})
        if response.status_code == 409 and not exist_ok:
            raise FolderExistsException(name)

        elif response.status_code == 409 and exist_ok:
            for folder in self.folders:
                if folder.name == name:
                    return folder

        elif response.status_code == 201:
            return _WaterButlerFolder(response.json(), self.session)

        else:
            raise RuntimeError("Response has status code {} while creating "
                               "folder {}.".format(response.status_code,
                                                   name))


class _WaterButlerFolder(OSFCore):
    """A slimmed down `Folder` built from a WaterButler response

    This representation is enough to navigate the folder structure
    and create new, rename and delete sub-folders.

    Users should never see this, always show them a full `Folder`.
    """
    def _update_attributes(self, file):
        if not file:
            return

        # XXX does this happen?
        if 'data' in file:
            file = file['data']

        self.id = self._get_attribute(file, 'id')

        self.osf_path = self._get_attribute(file, 'attributes', 'path')

        self._delete_url = self._get_attribute(file, 'links', 'delete')
        self._new_folder_url = self._get_attribute(file, 'links', 'new_folder')
        self._new_file_url = self._get_attribute(file, 'links', 'upload')
        self._move_url = self._get_attribute(file, 'links', 'move')

    @property
    def full_folder(self):
        base_url = "https://api.osf.io/v2/files"
        folder = self._json(self._get(base_url % self.osf_path), 200)
        return Folder(folder, self.session)

    def create_folder(self, name, exist_ok=False):
        # Create a new sub-folder
        response = self._put(self._new_folder_url,
                             params={'name': name})
        if response.status_code == 409 and not exist_ok:
            raise FolderExistsException(name)

        elif response.status_code == 201:
            return _WaterButlerFolder(response.json(), self.session)

        else:
            raise RuntimeError("Response has status code {} while creating "
                               "folder {}.".format(response.status_code,
                                                   name))

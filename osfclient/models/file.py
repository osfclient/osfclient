import shutil

from .core import OSFCore


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
        return '<Folder [{0}, {1}]>'.format(self.id, self.path)

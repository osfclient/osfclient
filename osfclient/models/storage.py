from .core import OSFCore
from .file import File


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
                yield File(file)
            else:
                # recurse into a folder and add entries to `files`
                url = self._get_attribute(file, *self._files_key)
                files.extend(self._follow_next(url))

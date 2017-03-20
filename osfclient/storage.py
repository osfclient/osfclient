from .api import OSFCore


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

        files = ['relationships', 'files', 'links', 'related', 'href']
        self._files_url = self._get_attribute(storage, *files)

    def __str__(self):
        return '<Storage [{0}]>'.format(self.id)

from .client.osf import OSFClient, NodeStorage


class FileOrFolder(object):
    def __init__(self, obj, storage, oo):
        attr = obj.raw['attributes']
        self.storage = storage
        self.path = storage.name + attr['materialized_path']

        self.is_file = False
        if attr['kind'] == 'file':
            self.is_file = True
            size = attr['size']
            if size is None:
                self.size = 0             # some 3rd party storage sol'ns?
            else:
                self.size = int(attr['size'])

        else:
            assert attr['kind'] == 'folder'
            self.size = None

        self.obj = obj
        self.oo = oo

    def get_download(self):
        download_url = self.obj.raw['links']['download']
        return self.oo.request_session.get(download_url)


def get_project_files(project_id, oo=None):
    """
    project_id -- OSF project ID, e.g. '7g6vu'.
    oo -- OSFClient object (optional). If 'None', can work with public projs.
    """
    if oo is None:
        oo = OSFClient()

    storages = NodeStorage.load(oo.request_session, project_id)

    for storage in storages:
        for o in get_files(storage.get_children(), storage, oo):
            yield o


def get_files(children, storage, oo):
    for c in children:
        o = FileOrFolder(c, storage, oo)
        yield o

        if not o.is_file:
            for x in get_files(c.get_children(), storage, oo):
                yield x

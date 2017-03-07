from .client.osf import OSFClient


class FileOrFolder(object):
    def __init__(self, obj, oo):
        attr = obj.raw['attributes']
        self.path = attr['materialized_path'].lstrip('/')

        self.is_file = False
        if attr['kind'] == 'file':
            self.is_file = True
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

    project_top = oo.get_node(project_id)

    print('looking at: {}'.format(project_top.title))

    storage = project_top.get_storage()
    return get_files(storage.get_children(), oo)

    
def get_files(children, oo):
    for c in children:
        o = FileOrFolder(c, oo)
        yield o

        if not o.is_file:
            for x in get_files(c.get_children(), oo):
                yield x

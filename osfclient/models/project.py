from .core import OSFCore
from .storage import Storage


class Project(OSFCore):
    _types = [
        'nodes',
        'registrations'
    ]

    def _update_attributes(self, project):
        if not project:
            return

        project = project['data']
        self._endpoint = self._get_attribute(project, 'links', 'self')
        self.id = self._get_attribute(project, 'id')
        attrs = self._get_attribute(project, 'attributes')
        self.title = self._get_attribute(attrs, 'title')
        self.date_created = self._get_attribute(attrs, 'date_created')
        self.date_modified = self._get_attribute(attrs, 'date_modified')
        self.description = self._get_attribute(attrs, 'description')

        storages = ['relationships', 'files', 'links', 'related', 'href']
        self._storages_url = self._get_attribute(project, *storages)

        self._wikis_node_url = self.session.build_url('nodes/%s/wikis/' % self.id)

    def __str__(self):
        return '<Project [{0}]>'.format(self.id)

    def storage(self, provider='osfstorage'):
        """Return storage `provider`."""
        stores = self._json(self._get(self._storages_url), 200)
        stores = stores['data']
        for store in stores:
            provides = self._get_attribute(store, 'attributes', 'provider')
            if provides == provider:
                return Storage(store, self.session)

        raise RuntimeError("Project has no storage "
                           "provider '{}'".format(provider))

    @property
    def wikis(self):
        """Return wiki pages for this project/component

        Returns
        -------
        list
            List of tuples. One element per wiki page,
            containing (ID, name, view_url, download_url)
        """
        wiks = self._json(self._get(self._wikis_node_url), 200)
        wiki_data = wiks['data']

        wiki_page_info = []

        # print('Fetching %s wiki pages' % wiks['meta'])

        next = wiks['links']['next']
        print(next)

        while next is not None:
            wiks = self._json(self._get(next), 200)
            wiki_data.extend(wiks['data'])
            next = wiks['links']['next']

        for wik in wiki_data:
            wiki_id = wik['id']
            name = wik['attributes']['name']
            view = 'https://osf.io/' + self.id + '/wiki/' + name + '/'
            download = wik['links']['download']
            wiki_page_info.append((wiki_id, name, view, download))
        
        return wiki_page_info
    
    @property
    def storages(self):
        """Iterate over all storages for this projects."""
        stores = self._json(self._get(self._storages_url), 200)
        stores = stores['data']
        for store in stores:
            yield Storage(store, self.session)

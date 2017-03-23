import json


project_node = json.loads("""
{
  "data": {
    "relationships": {
      "files": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/files/",
            "meta": {}
          }
        }
      },
      "view_only_links": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/view_only_links/",
            "meta": {}
          }
        }
      },
      "citation": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/citation/",
            "meta": {}
          }
        }
      },
      "license": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/licenses/563c1ffbda3e240129e72c03/",
            "meta": {}
          }
        }
      },
      "contributors": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/contributors/",
            "meta": {}
          }
        }
      },
      "forks": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/forks/",
            "meta": {}
          }
        }
      },
      "root": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/",
            "meta": {}
          }
        }
      },
      "identifiers": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/identifiers/",
            "meta": {}
          }
        }
      },
      "comments": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/comments/?filter%5Btarget%5D=f3szh",
            "meta": {}
          }
        }
      },
      "registrations": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/registrations/",
            "meta": {}
          }
        }
      },
      "logs": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/logs/",
            "meta": {}
          }
        }
      },
      "node_links": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/node_links/",
            "meta": {}
          }
        }
      },
      "linked_nodes": {
        "links": {
          "self": {
            "href": "https://api.osf.io/v2/nodes/f3szh/relationships/linked_nodes/",
            "meta": {}
          },
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/linked_nodes/",
            "meta": {}
          }
        }
      },
      "wikis": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/wikis/",
            "meta": {}
          }
        }
      },
      "affiliated_institutions": {
        "links": {
          "self": {
            "href": "https://api.osf.io/v2/nodes/f3szh/relationships/institutions/",
            "meta": {}
          },
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/institutions/",
            "meta": {}
          }
        }
      },
      "children": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/children/",
            "meta": {}
          }
        }
      },
      "preprints": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/preprints/",
            "meta": {}
          }
        }
      },
      "draft_registrations": {
        "links": {
          "related": {
            "href": "https://api.osf.io/v2/nodes/f3szh/draft_registrations/",
            "meta": {}
          }
        }
      }
    },
    "links": {
      "self": "https://api.osf.io/v2/nodes/f3szh/",
      "html": "https://osf.io/f3szh/"
    },
    "attributes": {
      "category": "project",
      "fork": false,
      "preprint": true,
      "description": "this is a test for preprint citations",
      "current_user_permissions": [
        "read"
      ],
      "date_modified": "2017-03-17T16:11:35.721000",
      "title": "Preprint Citations Test",
      "collection": false,
      "registration": false,
      "date_created": "2017-03-17T16:09:14.864000",
      "current_user_can_comment": false,
      "node_license": {
        "copyright_holders": [],
        "year": "2017"
      },
      "public": true,
      "tags": [
        "qatest"
      ]
    },
    "type": "nodes",
    "id": "f3szh"
  }
}
""")


def storage_node(project_id, storages=['osfstorage']):
    storage = """
    {
        "relationships": {
            "files": {
                "links": {
                    "related": {
                        "href": "https://api.osf.io/v2/nodes/%(project_id)s/files/%(name)s/",
                        "meta": {}
                    }
                }
            }
        },
        "links": {
            "storage_addons": "https://api.osf.io/v2/addons/?filter%%5Bcategories%%5D=storage",
            "upload": "https://files.osf.io/v1/resources/%(project_id)s/providers/%(name)s/",
            "new_folder": "https://files.osf.io/v1/resources/%(project_id)s/providers/%(name)s/?kind=folder"
        },
        "attributes": {
            "node": "%(project_id)s",
            "path": "/",
            "kind": "folder",
            "name": "%(name)s",
            "provider": "%(name)s"
        },
        "type": "files",
        "id": "%(project_id)s:%(name)s"
    }"""
    used_storages = []
    for store in storages:
        used_storages.append(json.loads(storage % {'project_id': project_id,
                                                   'name': store}))

    files = """{
    "data": %(storages)s,
    "links": {
        "first": null,
        "last": null,
        "prev": null,
        "next": null,
        "meta": {
            "total": %(n_storages)s,
            "per_page": 10
        }
    }
    }"""
    return json.loads(files % {'storages': json.dumps(used_storages),
                               'n_storages': len(used_storages)})

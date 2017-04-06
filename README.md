# osfclient

A python client for the Open Science Framework. This is a very new project,
it has some rough edges.


# Installing

To use `osfclient` install its dependencies with
`pip install -r requirements.txt`. Install the library itself in development
mode with:
```
pip install -e .
```

To participate in the development install the development requirements from
`devRequirements.txt`. Run the tests by executing `pytest` in the top level
directory.


# Usage

This project provides two things: a python library and a command-line program
for interacting with files stored in the [OSF](https://osf.io/).

The python library forms the basis for the command-line program. If you want
programmatic access to your files use the library, otherwise try out the
command-line program.

```
# list all files for a public project
$ osf ls <projectid>

# list all files for a private project
$ osf -u yourOSFacount@example.com ls <projectid>

# fetch all files from a project and store them in `output_directory`
$ osf fetch <projectid> [output_directory]

# create a new file in a OSF project
$ osf -u yourOSFacount@example.com upload <projectid> local/file.txt remote/path.txt
```

If the project is private you will need to provide authentication details.
You can provide your OSF account name as command-line argument or set
the `OSF_USERNAME` environment variable. The password will be retrieved from
the `OSF_PASSWORD` environment variable.


# Contributing

Contributions from everyone and anyone are welcome. Fork this repository,
make your changes, add a test to cover them and create a Pull Request.
Then one of the maintainers will review your changes. When all comments
have been addressed and all tests pass your changes will be merged.

# osfclient

A python client for the [Open Science Framework](//osf.io) (OSF). `osfcli` is a
python library and a command-line client for up- and downloading files for
your [osf.io](//osf.io) projects.

Currently people are using it to store and retrieve large datasets associated
to their scientific projects and papers on the OSF.

This is a very new project, it has some rough edges.


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

Below some examples on how to use it:
```
# list all files for a public project
$ osf -p <projectid> ls

# list all files for a private project
# set $OSF_PASSWORD to provide the password
$ osf -p <projectid> -u yourOSFacount@example.com ls

# fetch all files from a project and store them in `output_directory`
$ osf -p <projectid> clone [output_directory]

# create a new file in an OSF project
$ osf -p <projectid> -u yourOSFacount@example.com upload local/file.txt remote/path.txt

# download a single file from an OSF project
$ osf -p <projectid> fetch remote/path.txt local/file.txt

# upload a single file to an OSF project
$ osf -p <projectid> upload local/path.txt remote/file.txt

# remove a single file from an OSF project
$ osf -p <projectid> remove remote/file.txt
```

If the project is private you will need to provide authentication details.
You can provide your OSF account name as command-line argument (see the
`osf upload` example) or set the `OSF_USERNAME` environment variable. The
password will be retrieved from the `OSF_PASSWORD` environment variable.

You can set a default values by using a configuration file in the current
directory. To set the username and project ID create `.osfcli.config`:
```
[osf]
username = yourOSFaccount@example.com
project = 9zpcy
```
after which you can simply run `osf ls` to list the contents of the project.


# Contributing

Contributions from everyone and anyone are welcome. Fork this repository,
make your changes, add a test to cover them and create a Pull Request.
Then one of the maintainers will review your changes. When all comments
have been addressed and all tests pass your changes will be merged.

For details: [CONTRIBUTING.md](CONTRIBUTING.md)

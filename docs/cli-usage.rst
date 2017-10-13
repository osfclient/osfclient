User's Guide
============

This project provides two things: a python library and a command-line program
for interacting with files stored in the `OSF`_.

The python library forms the basis for the command-line program. If you want
programmatic access to your files use the library, otherwise try out the
command-line program.

Below some examples on how to use the command-line program:
::

    # getting help
    $ osf -h
    $ osf <command> -h

    # list all files for a public project
    $ osf -p <projectid> list

    # setup a local folder for an existing project
    $ osf init

    # list all files for a private project
    # set $OSF_PASSWORD to provide the password
    $ osf -p <projectid> -u yourOSFacount@example.com list

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

If you're using python 3+, you can also use the aliases `ls` in place of `list`, and `rm` in place of `remove`.


If the project is private you will need to provide authentication
details. You can provide your OSF account name as command-line argument
(see the ``osf upload`` example) or set the ``OSF_USERNAME`` environment
variable. The password will be retrieved from the ``OSF_PASSWORD``
environment variable or asked directly by the tool.

You can set a default values by using a configuration file in the
current directory. To set the username and project ID create
``.osfcli.config``:

::

    [osf]
    username = yourOSFaccount@example.com
    project = 9zpcy


after which you can simply run `osf list` to list the contents of the project.


.. _OSF: https://osf.io

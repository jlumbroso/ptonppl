# ptonppl — Princeton People

This provides a Python package and a command-line tool to lookup the
campus directory of any member of the Princeton community. The package
provides a unified search function that queries the following fields:
- PUID, *e.g.*, `902312554`
- NetID, *e.g.*, `lumbroso`
- Alias, when the user has defined one, *e.g.*, `jeremie.lumbroso`
- Email, *e.g.*, `lumbroso@princeton.edu`

This information is hard to come by consistently, and this tool seeks
to provide a robust interface to the information.

## Installation

The package is distributed on PyPI and can be installed using the usual
tools, such as `pip` or `pipenv`:
```shell
$ pip install --user ptonppl
```

## Help Message

```
$ ptonppl --help

Usage: ptonppl [OPTIONS] [QUERY]...

  Lookup the directory information (PUID, NetID, email, name) of any
  Princeton campus person, using whichever of LDAP, web directory or proxy
  server is available.

Options:
  -t, --type TYPE               Output type (e.g.: term, json, csv, emails).
  -u, --uniq / -nu, --not-uniq  Filter out duplicate records from the output.
  -s, --stats                   Display statistics once processing is done.
  -i, --input FILENAME          Read input from a file stream.
  -f, --fields FIELDS           Fields to keep (e.g.: 'puid,netid,email').
  --header / -nh, --no-header   Include or remove header in output.
  --version                     Show the version and exit.
  --help                        Show this message and exit.

```

## License

This project is licensed under the LGPLv3 license, with the understanding
that importing a Python modular is similar in spirit to dynamically linking
against it.

- You can use the library `ptonppl` in any project, for any purpose, as long
  as you provide some acknowledgement to this original project for use of
  the library.

- If you make improvements to `ptonppl`, you are required to make those
  changes publicly available.
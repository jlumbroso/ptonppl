
import sys
import time
import typing

import click
import click_help_colors

import ptonppl
import ptonppl.abstract
import ptonppl.constants
import ptonppl.control


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"


cli_opt_version = click.version_option(version=ptonppl.__version__)

try:
    OutputFormatType = typing.Union[
        typing.Literal["term"],
        typing.Literal["json"],
        typing.Literal["csv"],
    ]
except AttributeError:
    OutputFormatType = str

cli_opt_output_format = click.option(
    "--format", "-f",
    type=click.Choice(["term", "json", "csv"], case_sensitive=False),
    default="term", metavar="FORMAT",
    help="Output format (e.g.: term, json, csv, ...)"
)


@click.command(
    cls=click_help_colors.HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='bright_yellow'
)
@click.argument("query", nargs=-1, required=True)
@cli_opt_output_format
@click.option(
    "--unique", "-u",
    is_flag=True, default=True,
    help="Filter out duplicate records from the output."
)
@cli_opt_version
def cli(
        query: typing.Tuple[str],
        format: OutputFormatType,
        unique: bool,
):
    """
    Lookup the directory information (PUID, NetID, email, name) of any
    Princeton campus person, using whichever of LDAP, web directory or
    proxy server is available.
    """

    # Initial statistics

    count_total: int = len(query)
    count_success: int = 0
    count_error: int = 0
    count_duplicate: int = 0

    time_start: float = time.time()

    # NetIDs should be a unique, and fairly available piece of data to
    # check whether we've seen an object before

    seen_netids: typing.Set[str] = set()
    results: typing.List[ptonppl.abstract.AbstractPtonPerson] = list()

    if format == "json":
        print("{")

    elif format == "csv":
        print(",".join(ptonppl.constants.OUTPUT_CSV_HEADER))

    for q in query:

        # lookup object
        obj = ptonppl.control.search(value=q)

        # may not have been found
        if obj is None:
            count_error += 1
            continue

        count_success += 1

        if obj.netid in seen_netids:
            count_duplicate += 1
            if unique:
                continue

        # save new results
        seen_netids.add(obj.netid)
        results.append(obj)

        if format == "json":
            print("    {},".format(obj.as_dict.__repr__()))

        elif format == "csv":
            print(",".join(
                list(map(
                    lambda field: '"{}"'.format(obj.as_dict.get(field, "").replace('"', '\"')),
                    ptonppl.constants.OUTPUT_CSV_HEADER))))

        elif format == "term":
            print(obj.common_name)
            print("  {}".format(obj.puid))
            print("  {}".format(obj.netid))
            print("  {}".format(obj.email))
            print()

    if format == "json":
        print("}")

    # End statistics

    count_results = len(results)
    time_end: float = time.time()
    time_elapsed: float = time_end - time_start


def main():
    return sys.exit(cli())


if __name__ == "__main__":
    main()


import io
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
        typing.Literal["emails"],
    ]
except AttributeError:
    OutputFormatType = str


@click.command(
    cls=click_help_colors.HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='bright_yellow'
)
@click.argument("query", nargs=-1)
@click.option(
    "--type", "-t",
    type=click.Choice(["term", "json", "csv", "emails"], case_sensitive=False),
    default="term", metavar="TYPE",
    help="Output type (e.g.: term, json, csv, emails)."
)
@click.option(
    "--uniq/--not-uniq", "-u/-nu",
    is_flag=True, default=True,
    help="Filter out duplicate records from the output."
)
@click.option(
    "--stats", "-s",
    is_flag=True, default=False,
    help="Display statistics once processing is done."
)
@click.option(
    "--input", "-i",
    type=click.File("r"),
    help="Read input from a file stream."
)
@click.option(
    "--fields", "-f",
    type=str,
    default=",".join(ptonppl.constants.OUTPUT_CSV_HEADER), metavar="FIELDS",
    help="Fields to keep (e.g.: 'puid,netid,email')."
)
@click.option(
    "--header/--no-header", " /-nh",
    is_flag=True, default=True,
    help="Include or remove header in output."
)
@cli_opt_version
def cli(
        query: typing.Tuple[str],
        type: OutputFormatType,
        uniq: bool,
        stats: bool,
        input: typing.Optional[io.TextIOWrapper],
        fields: typing.Optional[str],
        header: bool,
):
    """
    Lookup the directory information (PUID, NetID, email, name) of any
    Princeton campus person, using whichever of LDAP, web directory or
    proxy server is available.
    """

    # Check for input file

    if input is not None:
        try:
            input.seek(0)
        except io.UnsupportedOperation:
            pass

        input_string = input.read()
        input_tokens = input_string.split()

        query = (*query, *input_tokens)

    if fields is None:
        fields = ptonppl.constants.OUTPUT_CSV_HEADER[:]

    else:
        fields = [
            field
            for field in fields.lower().split(",")
            if field in ptonppl.constants.OUTPUT_CSV_HEADER
        ]

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

    if type == "json":
        print("{")

    elif type == "csv" and header:
        print(",".join(fields))

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
            if uniq:
                continue

        # save new results
        seen_netids.add(obj.netid)
        results.append(obj)

        if type == "json":
            print("    {},".format(obj.as_dict.__repr__()))

        elif type == "csv":
            def quote_csv_cell(s):
                if ',' in s:
                    return '"{}"'.format(s.replace('"', '\"'))
                return s
            print(",".join(
                list(map(
                    lambda field: quote_csv_cell(obj.as_dict.get(field, "")),
                    fields))))

        elif type == "term":
            pattern = "{}"
            if header:
                print(obj.common_name)
                pattern = "  {}"
            if "netid" in fields:
                print(pattern.format(obj.netid))
            if "puid" in fields:
                print(pattern.format(obj.puid))
            if "email" in fields:
                print(pattern.format(obj.email))
            if header:
                print()

        elif type == "emails":
            print(
                '"{name}" <{email}>,'.format(
                    name=obj.common_name,
                    email=obj.email.lower(),
                )
            )

    if type == "json":
        print("}")

    # End statistics

    count_results = len(results)
    time_end: float = time.time()
    time_elapsed: float = time_end - time_start

    if stats:
        print(
            "# counts: {success} success, {error} errors, {duplicate} duplicates, {results} output, {total} total".format(
                success=count_success,
                error=count_error,
                duplicate=count_duplicate,
                results=count_results,
                total=count_total,
            ),
            file=sys.stderr,
        )
        print(
            "# timing: {elapsed:.2}s".format(
                elapsed=time_elapsed,
                start=time_start,
                stop=time_end,
            ),
            file=sys.stderr,
        )


def main():
    return sys.exit(cli())


if __name__ == "__main__":
    main()

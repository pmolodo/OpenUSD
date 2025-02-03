#!/usr/bin/env python

"""Render /proposals/usdlux-clarification/README.md.template to README.md"""

import argparse
import functools
import inspect
import os
import re
import sys
import textwrap
import traceback

import pxr.Sdf

###############################################################################
# Constants
###############################################################################

THIS_FILE = os.path.abspath(inspect.getsourcefile(lambda: None) or __file__)
THIS_DIR = os.path.dirname(THIS_FILE)

TEMPLATE_DEFAULT = os.path.join(THIS_DIR, "README.md.template")
PROPOSALS_DIR = os.path.dirname(os.path.dirname(THIS_DIR))
USD_CI_DIR = os.path.join(os.path.dirname(PROPOSALS_DIR), "usd-ci")
OUTPUT_DEFAULT = os.path.join(THIS_DIR, "README.md")
LUX_SCHEMA_PATH = os.path.join(USD_CI_DIR, "USD", "pxr", "usd", "usdLux", "schema.usda")

PLACEHOLDER_RE = re.compile(r"""<~(.*)~>""")
TRAILING_WHITESPACE_RE = re.compile(r"""[ \t]+(?=\n|$)""")
FORMULA_RE = re.compile(r"""(?P<prefix><center><b>)(?P<contents>.*?)(?P<suffix>\n+</b></center>)""", re.DOTALL)
NON_EMPTY_LINE_RE = re.compile(
    r"""^(?P<lead_space>[ \t]*)(?P<non_space>\S+([ \t]+\S+)*)(?P<trail_space>[ \t]*)$""", re.MULTILINE
)

###############################################################################
# Utilities
###############################################################################


def is_ipython():
    try:
        __IPYTHON__  # type: ignore
    except NameError:
        return False
    return True


def make_abs(path):
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(THIS_DIR, path))


###############################################################################
# Core functions
###############################################################################


@functools.cache
def get_usdlux_schema(lux_schema_path: str) -> pxr.Sdf.Layer:
    if not os.path.isfile(lux_schema_path):
        raise RuntimeError(f"could not find the UsdLux schema file at: {lux_schema_path}")

    return pxr.Sdf.Layer.FindOrOpen(lux_schema_path)


def format_doc(doc: str) -> str:
    """Quote, indent, etc the given documentation string"""
    formatted = doc.rstrip()
    formatted = trim_trailing_whitespace(doc)
    formatted = dedent_doc(formatted)
    formatted = format_formulas(formatted)
    formatted = quote_doc(formatted)
    formatted = formatted.rstrip("\n")
    return formatted


def quote_doc(doc: str) -> str:
    return textwrap.indent(doc, "  > ", predicate=lambda x: True)


def dedent_doc(doc: str) -> str:
    match doc.split("\n", 1):
        case (first, rest):
            dedented_rest = textwrap.dedent(rest)
            return f"{first}\n{dedented_rest}"
        case (first,):
            return first
        case _:
            raise RuntimeError("Unexpected condition - .split(x, 1) should result in 1 or 2 elements")


def replace_formula_match(match: re.Match) -> str:
    contents = match.group("contents")
    contents = NON_EMPTY_LINE_RE.sub("\g<lead_space><b>\g<non_space></b>", contents)
    match contents.split("\n", 1):
        case (first, rest):
            rest = rest.replace("\n\n", "\n<p>\n")
            contents = f"{first}\n{rest}"

    return f'<div align="center">{contents}\n<p>\n</div>'


def format_formulas(doc: str) -> str:
    return FORMULA_RE.sub(replace_formula_match, doc)


def trim_trailing_whitespace(new_text: str) -> str:
    return TRAILING_WHITESPACE_RE.sub("", new_text)


def replace_template_match(match: re.Match) -> str:
    lux_schema = get_usdlux_schema(LUX_SCHEMA_PATH)

    find_name = match.group(1)
    section_name: str | None = None

    match find_name.split("#"):
        case (prim_or_attr_path,):
            pass
        case (prim_or_attr_path, section_name):
            pass
        case _:
            raise ValueError("template replacement name had more than one #: {find_name}")
    prim_or_attr = lux_schema.GetObjectAtPath(prim_or_attr_path)
    if not prim_or_attr:
        raise RuntimeError(f"unable to find path in UsdLux schema: {prim_or_attr_path}")
    doc = prim_or_attr.documentation

    if section_name:
        section_re_pattern = rf"""(<b>[ \t]*{re.escape(section_name)}[ \t]*</b>.*?)(?:[ \t]*\n)+[ \t]*<b>"""
        match = re.search(section_re_pattern, doc, re.DOTALL)
        doc = match.group(1)

    return format_doc(doc)


def render_usdlux_proposal_template(template_path: str, output_path: str):
    template_path = make_abs(template_path)
    output_path = make_abs(output_path)

    if not os.path.exists(template_path):
        raise ValueError(f"template_path did not exist: {template_path}")

    print(f"Reading: {template_path}")
    with open(template_path, "r", encoding="utf8") as reader:
        text = reader.read()

    new_text = PLACEHOLDER_RE.sub(replace_template_match, text)
    new_text = trim_trailing_whitespace(new_text)

    print(f"Outputting: {output_path}")

    with open(output_path, "w", encoding="utf8") as writer:
        writer.write(new_text)


###############################################################################
# CLI
###############################################################################


def get_parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--template",
        default=TEMPLATE_DEFAULT,
        help="Path the .template file",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_DEFAULT,
        help="Path at which to write the rendered file",
    )

    return parser


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = get_parser()
    args = parser.parse_args(argv)
    try:
        render_usdlux_proposal_template(args.template, args.output)
    except Exception:  # pylint: disable=broad-except

        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__" and not is_ipython():
    sys.exit(main())

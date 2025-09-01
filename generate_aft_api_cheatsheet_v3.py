#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AFT API Cheat Sheet Generator (v3)
- Groups operations into categories for readability
- Optional split output: one Markdown file per category + an index
- Still document/literal aware and crawls imported XSDs for enums (v2 features)

Usage:
  pip install zeep lxml requests
  python generate_aft_api_cheatsheet_v3.py \
      --wsdl http://localhost:8801/AFTControl?singleWsdl \
      --out AFT_API_Cheat_Sheet.md \
      --split-dir ./aft_api_cheatsheet_parts \
      --dump-json AFT_API_Cheat_Sheet.json

If --split-dir is provided, the script writes:
  - <split-dir>/00_Index.md (with links to all parts)
  - One file per category, e.g. <split-dir>/10_Model_And_Files.md, etc.
"""

import argparse
import json
import os
import re
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin

import requests
from lxml import etree
from zeep import Client

XS = "{http://www.w3.org/2001/XMLSchema}"

ENUM_SIMPLETYPES = [
    "AFTAPI.ObjectType",
    "AFTAPI.GetParameters",
    "AFTAPI.SetParameters",
    "AFTAPI.SetType",
    "AFTAPI.AFTStandardFluids",
    "AFTAPI.ActionErrorEnum",
    "AFTAPI.SolverStatus",
    "GlobalDeclarations.JunctionTypeEnum",
]

DEFAULTS = [
    "http://localhost:8801/AFTControl?singleWsdl",
    "http://localhost:8888/AFTControl?singleWsdl",
]

# --------- Helpers for I/O and WSDL crawling ---------

def resolve_wsdl(cli_wsdl: Optional[str]) -> str:
    if cli_wsdl:
        return cli_wsdl
    env = os.environ.get("AFT_WSDL_URL")
    if env:
        return env
    for url in DEFAULTS:
        try:
            r = requests.get(url, timeout=3)
            if r.ok and b"definitions" in r.content.lower():
                return url
        except Exception:
            pass
    return DEFAULTS[0]

def http_get_xml(url: str) -> etree._Element:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    parser = etree.XMLParser(remove_comments=False, recover=True)
    return etree.fromstring(r.content, parser=parser)

def crawl_schemas(doc: etree._Element, base_url: str, visited: Set[str]) -> List[etree._Element]:
    schemas = []
    for s in doc.findall(".//" + XS + "schema"):
        schemas.append(s)
    for imp in doc.findall(".//" + XS + "import"):
        loc = imp.get("schemaLocation")
        if loc:
            url = urljoin(base_url, loc)
            if url not in visited:
                visited.add(url)
                try:
                    sub = http_get_xml(url)
                    schemas.extend(crawl_schemas(sub, url, visited))
                except Exception:
                    pass
    for inc in doc.findall(".//" + XS + "include"):
        loc = inc.get("schemaLocation")
        if loc:
            url = urljoin(base_url, loc)
            if url not in visited:
                visited.add(url)
                try:
                    sub = http_get_xml(url)
                    schemas.extend(crawl_schemas(sub, url, visited))
                except Exception:
                    pass
    return schemas

def extract_enums_from_schemas(schemas: List[etree._Element], wanted: List[str]) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for s in schemas:
        for st in s.findall("./" + XS + "simpleType"):
            name = st.get("name")
            if not name or name not in wanted:
                continue
            vals: List[str] = []
            for enum in st.findall(".//" + XS + "enumeration"):
                v = enum.get("value")
                if v is not None:
                    vals.append(v)
            if vals:
                out[name] = vals
    return out

def get_operations_document_literal(client: Client) -> List[Dict]:
    ops: List[Dict] = []
    for service in client.wsdl.services.values():
        for port in service.ports.values():
            binding = port.binding
            for op in sorted(binding._operations.values(), key=lambda o: o.name.lower()):
                item = {"name": op.name, "inputs": [], "outputs": []}
                try:
                    if op.input and op.input.body and op.input.body.type:
                        for (fname, ftype) in op.input.body.type.elements:
                            item["inputs"].append((fname, str(ftype)))
                except Exception:
                    pass
                try:
                    if op.output and op.output.body and op.output.body.type:
                        for (fname, ftype) in op.output.body.type.elements:
                            item["outputs"].append((fname, str(ftype)))
                except Exception:
                    pass
                ops.append(item)
    return ops

# --------- Grouping / Formatting ---------

def md_h1(title: str) -> str:
    return f"# {title}\n\n"

def md_h2(title: str) -> str:
    return f"\n## {title}\n\n"

def md_h3(title: str) -> str:
    return f"\n### {title}\n\n"

def table(headers: List[str], rows: List[List[str]]) -> str:
    head = "| " + " | ".join(headers) + " |\n"
    sep  = "| " + " | ".join(["---"] * len(headers)) + " |\n"
    body = "".join("| " + " | ".join(r) + " |\n" for r in rows)
    return head + sep + body + "\n"

# Category order and matching rules (simple heuristics by operation name)
CATEGORY_RULES: List[Tuple[str, List[re.Pattern]]] = [
    ("Model & Files", [
        re.compile(r"^AFTAPICreateNewModel$", re.I),
        re.compile(r"^AFTAPIOpenExistingModel$", re.I),
        re.compile(r"^AFTAPISaveModel$", re.I),
        re.compile(r"^AFTAPIOverwriteModel$", re.I),
        re.compile(r"^AFTAPIFormIsOpen$", re.I),
        re.compile(r"^AFTAPIModelIsDefined$", re.I),
    ]),
    ("Scenarios", [
        re.compile(r"^AFTAPICreateScenario$", re.I),
        re.compile(r"^AFTAPIDeleteScenario$", re.I),
        re.compile(r"^AFTAPIPromoteScenario$", re.I),
        re.compile(r"^AFTAPICloneScenario$", re.I),
        re.compile(r"^AFTAPIRenameScenario$", re.I),
        re.compile(r"^AFTAPISetScenario$", re.I),
        re.compile(r"^AFTAPIGetCurrentModelAndScenario$", re.I),
    ]),
    ("Run Control", [
        re.compile(r"^AFTAPIStartRun$", re.I),
        re.compile(r"^AFTAPIPauseRun$", re.I),
        re.compile(r"^AFTAPIUnpauseRun$", re.I),
        re.compile(r"^AFTAPICancelRun$", re.I),
        re.compile(r"^AFTAPIModelRunStatus$", re.I),
        re.compile(r"^AFTAPILockModel$", re.I),
        re.compile(r"^AFTAPIUnlockModel$", re.I),
    ]),
    ("Topology (Add/Remove)", [
        re.compile(r"^AFTAPIAddJct(ByCoords)?$", re.I),
        re.compile(r"^AFTAPIAddPipe(ByCoords)?$", re.I),
        re.compile(r"^AFTAPIRemoveObject$", re.I),
        re.compile(r"^AFTAPIGetAllObjects$", re.I),
        re.compile(r"^AFTAPIGetPipeTagsForJunction$", re.I),
        re.compile(r"^AFTAPIPipeOrJunctionNotes$", re.I),
        re.compile(r"^AFTAPISetPipeOrJunctionNotes$", re.I),
    ]),
    ("Fluid & Materials", [
        re.compile(r"^AFTAPISetFluid$", re.I),
        re.compile(r"^AFTAPISetPipeMaterialInfo$", re.I),
        re.compile(r"^AFTAPIGetFluidPropertiesValue$", re.I),
        re.compile(r"^AFTAPISetFluidPropertiesValue$", re.I),
    ]),
    ("Get Values (Inputs/Outputs/Results)", [
        re.compile(r"^AFTAPIGet.+Value$", re.I),
        re.compile(r"^AFTAPIGetAllMessages$", re.I),
        re.compile(r"^AFTAPIGetGlobalResultsValue$", re.I),
    ]),
    ("Set Values (Inputs/Transient)", [
        re.compile(r"^AFTAPISet.+Value$", re.I),
        re.compile(r"^AFTAPISetTransientDataPoint$", re.I),
    ]),
]

def categorize_operation(op_name: str) -> str:
    for cat, patterns in CATEGORY_RULES:
        for p in patterns:
            if p.search(op_name):
                return cat
    return "Other"

def build_operation_rows(ops: List[Dict]) -> List[List[str]]:
    rows = []
    for op in ops:
        in_str = ", ".join(f"{n}:{t}" for (n,t) in op["inputs"]) if op["inputs"] else "—"
        out_str = ", ".join(f"{n}:{t}" for (n,t) in op["outputs"]) if op["outputs"] else "—"
        rows.append([op["name"], in_str, out_str])
    return rows

def render_operations_grouped(ops: List[Dict]) -> Tuple[str, Dict[str, str]]:
    """
    Returns:
      full_md: a single Markdown string with grouped sections
      per_cat_md: dict[category] = markdown table only for that category
    """
    # Group
    grouped: Dict[str, List[Dict]] = {}
    for op in ops:
        cat = categorize_operation(op["name"])
        grouped.setdefault(cat, []).append(op)

    # Keep deterministic order by CATEGORY_RULES, then "Other"
    ordered_cats = [c[0] for c in CATEGORY_RULES] + ["Other"]
    per_cat_md: Dict[str, str] = {}
    parts: List[str] = []
    parts.append(md_h2("Operations (Grouped)"))
    for cat in ordered_cats:
        if cat not in grouped:
            continue
        cat_ops = sorted(grouped[cat], key=lambda o: o["name"].lower())
        rows = build_operation_rows(cat_ops)
        section_md = md_h3(cat) + table(["Operation", "Input (name:type)", "Output (name:type)"], rows)
        parts.append(section_md)
        per_cat_md[cat] = section_md
    return "".join(parts), per_cat_md

# --------- Main ---------

def main() -> int:
    ap = argparse.ArgumentParser(description="Generate an AFT API Cheat Sheet with grouping and split output (v3).")
    ap.add_argument("--wsdl", type=str, help="WSDL URL (e.g., http://localhost:8801/AFTControl?singleWsdl)")
    ap.add_argument("--out", type=str, default="AFT_API_Cheat_Sheet.md", help="Output Markdown path")
    ap.add_argument("--split-dir", type=str, default="", help="Directory to write per-category Markdown files")
    ap.add_argument("--dump-json", type=str, default="", help="Also write JSON dump (operations, enums)")
    args = ap.parse_args()

    wsdl_url = resolve_wsdl(args.wsdl)
    print(f"[info] Using WSDL: {wsdl_url}")

    # Build client and fetch ops
    try:
        client = Client(wsdl_url)
    except Exception as e:
        print(f"[error] Zeep Client failed: {e}")
        return 1

    ops = get_operations_document_literal(client)

    # Enums
    try:
        wsdl_xml = http_get_xml(wsdl_url)
    except Exception as e:
        print(f"[error] Fetching WSDL failed: {e}")
        return 1
    schemas = crawl_schemas(wsdl_xml, wsdl_url, visited=set([wsdl_url]))
    enums = extract_enums_from_schemas(schemas, ENUM_SIMPLETYPES)

    # ---------- Compose unified Markdown ----------
    top: List[str] = []
    top.append(md_h1("AFT API Cheat Sheet"))
    top.append(f"_Source WSDL_: `{wsdl_url}`\n")
    top.append("\n---\n")

    # Operations (Grouped)
    ops_grouped_md, per_cat_md = render_operations_grouped(ops)
    top.append(ops_grouped_md)

    # Enums sections
    def emit_enum(title: str, key: str):
        vals = enums.get(key, [])
        top.append(md_h2(title))
        if vals:
            top.append(table(["Value"], [[v] for v in vals]))
        else:
            top.append("_Not found in WSDL/XSDs._\n\n")

    emit_enum("Object Types", "AFTAPI.ObjectType")
    emit_enum("GetParameters", "AFTAPI.GetParameters")
    emit_enum("SetParameters", "AFTAPI.SetParameters")
    emit_enum("SetType (Change Modes)", "AFTAPI.SetType")
    emit_enum("Junction Types", "GlobalDeclarations.JunctionTypeEnum")
    emit_enum("Standard Fluids", "AFTAPI.AFTStandardFluids")
    emit_enum("Action Error Enum", "AFTAPI.ActionErrorEnum")
    emit_enum("Solver Status", "AFTAPI.SolverStatus")

    # Write unified Markdown
    out_path = os.path.abspath(args.out)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(top))
    print(f"[ok] Cheat sheet written to: {out_path}")

    # ---------- Optional split output ----------
    if args.split_dir:
        split_dir = os.path.abspath(args.split_dir)
        os.makedirs(split_dir, exist_ok=True)

        # Write per-category files
        index_lines: List[str] = []
        index_lines.append(md_h1("AFT API Cheat Sheet — Index"))
        index_lines.append(f"_Source WSDL_: `{wsdl_url}`\n")
        index_lines.append("\n---\n")
        index_lines.append("## Parts\n\n")

        # Number categories for predictable ordering
        ordered_cats = [c[0] for c in CATEGORY_RULES] + ["Other"]
        for i, cat in enumerate(ordered_cats):
            if cat not in per_cat_md:
                continue
            filename = f"{i:02d}_{cat.replace(' ', '_')}.md"
            cat_path = os.path.join(split_dir, filename)
            with open(cat_path, "w", encoding="utf-8") as cf:
                cf.write(md_h1(f"AFT API — {cat}"))
                cf.write(per_cat_md[cat])
            index_lines.append(f"- [{cat}]({filename})\n")

        # Write enums into their own file too
        enums_name = f"{len(ordered_cats):02d}_Enums.md"
        enums_path = os.path.join(split_dir, enums_name)
        with open(enums_path, "w", encoding="utf-8") as ef:
            ef.write(md_h1("AFT API — Enums"))
            # Repeat same enum blocks
            def write_enum_block(title: str, key: str):
                ef.write(md_h2(title))
                vals = enums.get(key, [])
                if vals:
                    ef.write(table(["Value"], [[v] for v in vals]))
                else:
                    ef.write("_Not found in WSDL/XSDs._\n\n")
            write_enum_block("Object Types", "AFTAPI.ObjectType")
            write_enum_block("GetParameters", "AFTAPI.GetParameters")
            write_enum_block("SetParameters", "AFTAPI.SetParameters")
            write_enum_block("SetType (Change Modes)", "AFTAPI.SetType")
            write_enum_block("Junction Types", "GlobalDeclarations.JunctionTypeEnum")
            write_enum_block("Standard Fluids", "AFTAPI.AFTStandardFluids")
            write_enum_block("Action Error Enum", "AFTAPI.ActionErrorEnum")
            write_enum_block("Solver Status", "AFTAPI.SolverStatus")

        # Write index
        index_path = os.path.join(split_dir, "00_Index.md")
        with open(index_path, "w", encoding="utf-8") as idx:
            idx.write("".join(index_lines))

        print(f"[ok] Split files written under: {split_dir}")
        print(f"[ok] Open index: {index_path}")

    # ---------- Optional JSON dump ----------
    if args.dump_json:
        j = {
            "wsdl": wsdl_url,
            "operations": ops,
            "enums": enums,
            "categories": list(per_cat_md.keys()),
        }
        with open(os.path.abspath(args.dump_json), "w", encoding="utf-8") as jf:
            json.dump(j, jf, indent=2)
        print(f"[ok] JSON dump written to: {os.path.abspath(args.dump_json)}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

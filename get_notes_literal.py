#!/usr/bin/env python3
# get_notes_literal.py (fixed)
# Reads Junction 145 notes without letting zeep/lxml parse the inner XML.

import re
import html
from zeep import Client, Settings

WSDL_URL = "http://localhost:8801/AFTControl?singleWsdl"
JUNCTION_TAG = 145

def extract_inner_xml(soap_text: str) -> str:
    m = re.search(
        r"<AFTAPIPipeOrJunctionNotesResult>(.*?)</AFTAPIPipeOrJunctionNotesResult>",
        soap_text, flags=re.DOTALL | re.IGNORECASE
    )
    if not m:
        raise RuntimeError("Could not find AFTAPIPipeOrJunctionNotesResult in SOAP body.")
    return html.unescape(m.group(1))  # unescape &lt; &gt; &#xD; etc.

def extract_value_from_inner(inner_xml: str) -> str:
    m = re.search(r"<Value>(.*?)</Value>", inner_xml, flags=re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else inner_xml

def main():
    # This is the key change: enable raw_response on the Client
    settings = Settings(strict=False, raw_response=True)
    client = Client(WSDL_URL, settings=settings)
    ObjectTypeEnum = client.get_type("{http://schemas.datacontract.org/2004/07/CodeBase}AFTAPI.ObjectType")

    # Regular call (no special kwargs). Returns requests.Response because raw_response=True
    resp = client.service.AFTAPIPipeOrJunctionNotes(
        ObjectType=ObjectTypeEnum("Junction"),
        ObjectTag=JUNCTION_TAG
    )

    soap_text = resp.content.decode("utf-8", errors="replace")
    inner_xml = extract_inner_xml(soap_text)
    raw_value = extract_value_from_inner(inner_xml)

    print("=== Raw <Value> text (may include \\x15) ===")
    print(raw_value)

    cleaned = raw_value.replace("\x15", "\n")
    print("\n=== Cleaned (\\x15 -> newline) ===")
    print(cleaned)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
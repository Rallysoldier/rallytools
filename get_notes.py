#!/usr/bin/env python3
"""
get_junction_notes_145.py
Fetches the Notes field for junction 145 from a running AFT instance via SOAP.

Prereqs:
- AFT Fathom/Arrow is open with a model loaded
- API service is running (e.g., http://localhost:8801/AFTControl?singleWsdl)
- pip install zeep

Usage:
  python get_junction_notes_145.py
"""

from zeep import Client

WSDL_URL = "http://localhost:8801/AFTControl?singleWsdl"
JUNCTION_TAG = 145

def get_junction_notes(wsdl_url: str, junction_tag: int) -> str:
    client = Client(wsdl_url)
    # Optional: sanity checks to give clearer errors
    try:
        model_defined = client.service.AFTAPIModelIsDefined()
        form_open = client.service.AFTAPIFormIsOpen()
        if not form_open or not model_defined:
            raise RuntimeError(
                "AFT is not open with a model loaded. "
                "Open Fathom/Arrow, load your model, and ensure the API is enabled."
            )
    except Exception:
        # Older/variant builds may not expose these checks; continue to the call.
        pass

    ObjectTypeEnum = client.get_type("{http://schemas.datacontract.org/2004/07/CodeBase}AFTAPI.ObjectType")

    notes = client.service.AFTAPIPipeOrJunctionNotes(
        ObjectType=ObjectTypeEnum("Junction"),
        ObjectTag=junction_tag
    )

    # Ensure it's a str (zeep returns strings but be defensive)
    if notes is None:
        notes = ""

    return str(notes)

def main():
    try:
        notes = get_junction_notes(WSDL_URL, JUNCTION_TAG)
        print("=== Raw Notes (as returned) ===")
        print(notes)

        # Helpful view: replace AFT's internal delimiter \x15 with newlines
        cleaned = notes.replace("\x15", "\n")
        print("\n=== Cleaned Notes (\\x15 -> newline) ===")
        print(cleaned)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

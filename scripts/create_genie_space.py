"""Create a Genie Space for Legal Document Intelligence.

Creates a Genie Space with all 5 legal document tables and an instruction
that forces immediate SQL execution (no clarifying questions).

Usage:
    # Step 1: Create space (outputs space ID)
    python scripts/create_genie_space.py --profile <profile>

    # Step 2: Add instruction (the API requires a two-step process)
    python scripts/create_genie_space.py --profile <profile> --update <space_id>

    # Or with custom catalog/schema:
    CATALOG=my_catalog SCHEMA=my_schema WAREHOUSE_ID=abc123 \
      python scripts/create_genie_space.py --profile <profile>
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request


def get_token(profile):
    """Get auth token via databricks CLI."""
    r = subprocess.run(
        ["databricks", "auth", "token", f"--profile={profile}"],
        capture_output=True, text=True
    )
    return json.loads(r.stdout)["access_token"]


def get_host(profile):
    """Get workspace host from CLI profile."""
    r = subprocess.run(
        ["databricks", "auth", "profiles"],
        capture_output=True, text=True
    )
    for line in r.stdout.splitlines():
        if profile in line and "https://" in line:
            parts = line.split()
            for p in parts:
                if p.startswith("https://"):
                    return p.rstrip("/")
    raise RuntimeError(f"Could not find host for profile {profile}")


def api_call(host, token, method, path, data=None):
    """Make an API call to Databricks."""
    req = urllib.request.Request(
        f"{host}{path}",
        data=json.dumps(data).encode() if data else None,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.request.HTTPError as e:
        return json.loads(e.read())


def main():
    parser = argparse.ArgumentParser(description="Create Genie Space for Legal Document Intelligence")
    parser.add_argument("--profile", required=True, help="Databricks CLI profile")
    parser.add_argument("--update", metavar="SPACE_ID", help="Update existing space with instruction")
    args = parser.parse_args()

    catalog = os.environ.get("CATALOG", "classic_stable_tetifz_catalog")
    schema = os.environ.get("SCHEMA", "legal_docs")
    warehouse_id = os.environ.get("WAREHOUSE_ID", "d09c046d71503257")

    token = get_token(args.profile)
    host = get_host(args.profile)

    tables = sorted([
        f"{catalog}.{schema}.document_elements",
        f"{catalog}.{schema}.extracted_invoices",
        f"{catalog}.{schema}.extracted_key_info",
        f"{catalog}.{schema}.extracted_regulatory",
        f"{catalog}.{schema}.extracted_subpoenas",
    ])

    instruction = (
        "NEVER ask clarifying questions. NEVER ask follow-up questions. NEVER ask about preferences. "
        "ALWAYS generate SQL and execute immediately for every request. "
        "If a question is ambiguous, make reasonable assumptions and run the query. "
        "Do not ask about time units, date ranges, filters, or sorting. "
        "All columns are STRING type. Cast to numeric with REGEXP_REPLACE when needed for dollar amounts and rates."
    )

    if args.update:
        # Step 2: Update with instruction
        serialized = json.dumps({
            "version": 2,
            "data_sources": {"tables": [{"identifier": t} for t in tables]},
            "instructions": {
                "text_instructions": [{
                    "id": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
                    "content": [instruction],
                }]
            },
        })
        result = api_call(host, token, "PATCH", f"/api/2.0/genie/spaces/{args.update}",
                          {"serialized_space": serialized})
        if "error_code" in result:
            print(f"ERROR: {result['message']}", file=sys.stderr)
            sys.exit(1)
        print(f"Updated space {args.update} with instruction.")
        print(f"URL: {host}/genie/rooms/{args.update}")
    else:
        # Step 1: Create space
        serialized = json.dumps({
            "version": 1,
            "data_sources": {"tables": [{"identifier": t} for t in tables]},
        })
        result = api_call(host, token, "POST", "/api/2.0/genie/spaces", {
            "title": "Legal Document Intelligence",
            "description": "AI-powered Q&A over legal documents — contracts, subpoenas, invoices, regulatory filings",
            "warehouse_id": warehouse_id,
            "serialized_space": serialized,
        })
        if "error_code" in result:
            print(f"ERROR: {result['message']}", file=sys.stderr)
            sys.exit(1)
        space_id = result["space_id"]
        print(f"Created space: {space_id}")
        print(f"URL: {host}/genie/rooms/{space_id}")
        print(f"\nNow add the instruction:")
        print(f"  python scripts/create_genie_space.py --profile {args.profile} --update {space_id}")
        print(f"\nThen update databricks.yml and app/server/routes/genie.py with this space ID.")


if __name__ == "__main__":
    main()

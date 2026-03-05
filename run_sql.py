"""Helper to run SQL statements via Databricks API."""
import json
import subprocess
import sys
import time

PROFILE = "fe-vm-classic"
WAREHOUSE_ID = "d09c046d71503257"


def run_sql(sql: str, wait=True, timeout=120):
    payload = json.dumps({
        "warehouse_id": WAREHOUSE_ID,
        "statement": sql,
        "wait_timeout": "0s"
    })
    result = subprocess.run(
        ["databricks", "api", "post", "/api/2.0/sql/statements",
         "--profile", PROFILE, "--json", payload],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    stmt_id = data["statement_id"]
    state = data["status"]["state"]

    if wait:
        start = time.time()
        while state in ("PENDING", "RUNNING") and time.time() - start < timeout:
            time.sleep(5)
            r = subprocess.run(
                ["databricks", "api", "get", f"/api/2.0/sql/statements/{stmt_id}",
                 "--profile", PROFILE],
                capture_output=True, text=True
            )
            data = json.loads(r.stdout)
            state = data["status"]["state"]

    return data


if __name__ == "__main__":
    sql_file = sys.argv[1]
    with open(sql_file) as f:
        sql = f.read()
    print(f"Running SQL from {sql_file}...")
    result = run_sql(sql)
    state = result["status"]["state"]
    print(f"Status: {state}")
    if state == "SUCCEEDED" and "result" in result:
        cols = [c["name"] for c in result["manifest"]["schema"]["columns"]]
        print("\t".join(cols))
        for row in result["result"]["data_array"]:
            print("\t".join(str(v) for v in row))
    elif state == "FAILED":
        print(json.dumps(result["status"], indent=2))

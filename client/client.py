# client/client.py
import argparse
import json
import sys
import time

import requests


def fetch(
    host: str,
    rows: int,
    parallel: bool,
    concurrency: int,
) -> tuple[float, dict]:
    """Call the /games endpoint and return (client_elapsed, json)."""
    start = time.perf_counter()

    response = requests.get(
        f"{host}/games",
        params={
            "rows": rows,
            "parallel": str(parallel).lower(),
            "concurrency": concurrency,
        },
        timeout=60,
    )
    response.raise_for_status()
    client_elapsed = round(time.perf_counter() - start, 3)
    return client_elapsed, response.json()


def main() -> None:
    parser = argparse.ArgumentParser("SteamScraper client")

    parser.add_argument("--rows", type=int, help="N (1-100) games")
    parser.add_argument("--host", default="http://127.0.0.1:8000")
    parser.add_argument(
        "--concurrency",
        type=int,
        default=20,
        help="# of concurrent requests",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare client and server time",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Show JSON response (no timing)",
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--parallel",
        action="store_true",
        help="Parallel mode (default)",
    )
    mode_group.add_argument(
        "--serial",
        action="store_true",
        help="Serial mode",
    )

    args = parser.parse_args()
    parallel = not args.serial

    if args.compare:
        for mode in ("serial", "parallel"):
            is_parallel = mode == "parallel"
            client_t, resp = fetch(
                args.host,
                args.rows,
                is_parallel,
                args.concurrency,
            )
            server_t = resp["elapsed"]
            print(
                f"{mode}: server={server_t}s  client={client_t}s",
            )
        return

    client_t, resp = fetch(
        args.host,
        args.rows,
        parallel,
        args.concurrency,
    )

    if args.raw:
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        return

    mode_str = "PARALLEL" if parallel else "SERIAL"
    server_t = resp["elapsed"]

    print(json.dumps(resp["data"], indent=2, ensure_ascii=False))
    print(f"{mode_str}: client={client_t}s  server={server_t}s")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(1)

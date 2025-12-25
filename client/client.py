# client/client.py
import argparse, requests, time, sys, json

def fetch(host, rows, parallel, concurrency):

    t0 = time.perf_counter() # Start timer
    
    # Call the API endpoint with the specified parameters
    r = requests.get(
        f"{host}/games",
        params={
            "rows": rows,
            "parallel": str(parallel).lower(),
            "concurrency": concurrency,
        },
        timeout=60,
    )
    r.raise_for_status()
    client_elapsed = round(time.perf_counter() - t0, 3) # Calculate elapsed time
    return client_elapsed, r.json()

def main():
    # Use argparse to parse command line arguments
    p = argparse.ArgumentParser("SteamScraper")

    p.add_argument("--rows", type=int, help="N (1-100) games")
    p.add_argument("--host", default="http://127.0.0.1:8000")
    p.add_argument("--concurrency", type=int, default=20,
                   help="# of concurrent requests")
    
    p.add_argument("--compare", action="store_true",
                   help="Compare client and server time")
    
    p.add_argument("--raw", action="store_true",
                      help="Show JSON response (no timing)")


    # Add mutually exclusive group for parallel and serial mode
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--parallel", action="store_true", help="Parallel mode (default)")
    mode.add_argument("--serial",   action="store_true", help="Serial mode")


    args = p.parse_args()

    parallel = not args.serial

    if args.compare:
        for mode in ("serial", "parallel"):
            client_t, resp = fetch(args.host, args.rows, mode == "parallel", args.concurrency)
            print(f"{mode}: server={resp['elapsed']}s  client={client_t}s")
        return

       
    client_t, resp = fetch(args.host, args.rows, parallel, args.concurrency)

    if args.raw:
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        return

    mode_str = "PARALLEL" if parallel else "SERIAL"
    server_t = resp["elapsed"]

    print(json.dumps(resp["data"], indent=2, ensure_ascii=False))
    print(f"{mode_str}: client={client_t}s  server={server_t}s\n")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(1)

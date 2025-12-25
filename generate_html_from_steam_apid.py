import argparse
import pathlib
import time

import requests

COOKIES = {
    "birthtime": str(int(time.time()) - 30 * 365 * 24 * 3600),
    "lastagecheckage": "1-January-1995",
    "wants_mature_content": "1",
}
HEADERS = {"User-Agent": "DumpSteamHTML v1.0"}
URL = "https://store.steampowered.com/app/{appid}"


def save(
    appid: int,
    fname: pathlib.Path,
    lang: str = "english",
    timeout: int = 10,
) -> None:
    response = requests.get(
        URL.format(appid=appid),
        params={"l": lang},
        headers=HEADERS,
        cookies=COOKIES,
        timeout=timeout,
    )
    response.raise_for_status()
    fname.write_bytes(response.content)
    print("Saved", fname)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("appid", type=int, help="Steam App ID")
    parser.add_argument(
        "--out",
        default="tests/html",
        help="output directory for HTML",
    )
    args = parser.parse_args()

    dest = pathlib.Path(args.out)
    dest.mkdir(parents=True, exist_ok=True)
    save(args.appid, dest / f"{args.appid}.html")

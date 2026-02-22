import csv
import os
import socket
import struct
import time
from pathlib import Path
from typing import Optional

from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError


HOST = os.getenv("SYN_HOST", "127.0.0.1")
PORT = int(os.getenv("SYN_PORT", "5050"))
LATENCY_LOG = Path(os.getenv("SYN_LATENCY_LOG", "latency_log.csv"))
PACKET_SIZE = 16

WYZE_ACCESS_TOKEN = os.getenv("WYZE_ACCESS_TOKEN", "")
WYZE_BULBS = os.getenv("WYZE_BULBS", "")


def parse_bulbs(raw: str) -> list[dict]:
    bulbs = []
    if not raw.strip():
        return bulbs
    for item in raw.split(","):
        mac, model = item.split(":", 1)
        bulbs.append({"mac": mac.strip(), "model": model.strip()})
    return bulbs


def recv_exact(conn: socket.socket, size: int) -> Optional[bytes]:
    data = b""
    while len(data) < size:
        chunk = conn.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def unpack_payload(packet: bytes) -> tuple[int, int, int, int, int]:
    version, r, g, b, track_hash, detect_ms = struct.unpack("!BBBBIQ", packet)
    if version != 1:
        raise ValueError(f"unsupported payload version: {version}")
    return r, g, b, track_hash, detect_ms


def set_color(client: Optional[Client], bulbs: list[dict], rgb: tuple[int, int, int]) -> bool:
    if client is None or not bulbs:
        return True
    hex_color = f"{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    try:
        for bulb in bulbs:
            client.bulbs.set_color(
                device_mac=bulb["mac"],
                device_model=bulb["model"],
                color=hex_color,
            )
        return True
    except WyzeApiError as exc:
        print(f"consumer wyze error: {exc}")
        return False


def ensure_latency_header(path: Path) -> None:
    if path.exists():
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "detect_ms",
                "received_ms",
                "command_done_ms",
                "transport_ms",
                "end_to_end_ms",
                "track_hash",
                "r",
                "g",
                "b",
                "success",
            ]
        )


def append_latency_row(
    path: Path,
    detect_ms: int,
    received_ms: int,
    done_ms: int,
    track_hash: int,
    rgb: tuple[int, int, int],
    success: bool,
) -> None:
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                detect_ms,
                received_ms,
                done_ms,
                received_ms - detect_ms,
                done_ms - detect_ms,
                track_hash,
                rgb[0],
                rgb[1],
                rgb[2],
                int(success),
            ]
        )


def main() -> None:
    bulbs = parse_bulbs(WYZE_BULBS)
    client = Client(token=WYZE_ACCESS_TOKEN) if WYZE_ACCESS_TOKEN else None
    ensure_latency_header(LATENCY_LOG)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(1)
        print(f"consumer listening on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            print(f"producer connected from {addr}")
            with conn:
                while True:
                    packet = recv_exact(conn, PACKET_SIZE)
                    if packet is None:
                        break

                    received_ms = time.time_ns() // 1_000_000
                    r, g, b, track_hash, detect_ms = unpack_payload(packet)
                    success = set_color(client, bulbs, (r, g, b))
                    done_ms = time.time_ns() // 1_000_000
                    append_latency_row(
                        LATENCY_LOG,
                        detect_ms=detect_ms,
                        received_ms=received_ms,
                        done_ms=done_ms,
                        track_hash=track_hash,
                        rgb=(r, g, b),
                        success=success,
                    )
                    print(
                        f"applied rgb=({r},{g},{b}) track_hash={track_hash} "
                        f"transport_ms={received_ms - detect_ms} "
                        f"end_to_end_ms={done_ms - detect_ms} success={success}"
                    )


if __name__ == "__main__":
    main()

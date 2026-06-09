#!/usr/bin/env python3
"""
Test KMBox Net connectivity before running the bot.
Reads config.ini [kmbox] and sends a small test move.

Usage: python scripts/test_kmbox.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from configReader import ConfigReader
from mouse.kmbox_mouse import KMBoxMouse


def main():
    cfg_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
    cfg = ConfigReader(path=cfg_path)
    cfg.read_config()

    if not cfg.kmbox_ip or cfg.kmbox_ip == "192.168.1.100":
        print("ERROR: kmbox_ip is still the default placeholder.")
        print("Edit config.ini [kmbox] with the IP shown on your KMBox Net screen.")
        sys.exit(1)

    if not cfg.kmbox_uid or cfg.kmbox_uid == "XXXXXXXX":
        print("ERROR: kmbox_uid is still the default placeholder.")
        print("Edit config.ini [kmbox] with the UUID shown on your KMBox Net screen.")
        sys.exit(1)

    print(f"KMBox Net: {cfg.kmbox_ip}:{cfg.kmbox_port} uid={cfg.kmbox_uid}")
    mouse = KMBoxMouse(cfg)

    print("Sending: move 5px right...")
    mouse.send_move(5, 0)
    time.sleep(0.15)
    print("Sending: move 5px left (returning)...")
    mouse.send_move(-5, 0)
    time.sleep(0.15)

    print()
    print("Packets sent. If your mouse cursor moved 5px right then back, KMBox is working.")
    print()
    print("If nothing moved, check:")
    print("  1. KMBox Net USB cable is connected to the gaming PC")
    print("  2. KMBox Net is on the same LAN as this machine")
    print("  3. config.ini [kmbox] IP/port/uid match the KMBox Net LCD screen")


if __name__ == "__main__":
    main()

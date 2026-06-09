"""
    Unibot, an open-source colorbot.
    Copyright (C) 2025 vike256

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import socket
import struct
import time
import random
import numpy as np

from mouse.base_mouse import BaseMouse

_CMD_MOVE  = 0x0001
_CMD_LEFT  = 0x0002
_CMD_RIGHT = 0x0003
_CMD_MID   = 0x0004


class KMBoxMouse(BaseMouse):
    """
    Pure Python UDP client for KMBox Net (port 6234).

    Packet layout (little-endian, 28 bytes):
      offset 0:  uid    uint32 — device UID from LCD (e.g. "AABBCCDD" → 0xAABBCCDD)
      offset 4:  rand   uint32 — random per-packet nonce
      offset 8:  cmd    uint32 — command code
      offset 12: x      int32  — x delta
      offset 16: y      int32  — y delta
      offset 20: wheel  int32  — scroll delta
      offset 24: button uint8  — button flags
      offset 25: resv   uint8  — reserved
      offset 26: high   int16  — reserved

    Verify packet format against physical device on first run — adjust cmd
    values if moves are rejected (see KMBox firmware docs).
    """

    def __init__(self, config):
        super().__init__(config)
        self._uid  = int(config.kmbox_uid, 16)
        self._addr = (config.kmbox_ip, int(config.kmbox_port))
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _build_packet(self, cmd: int, x: int = 0, y: int = 0,
                      wheel: int = 0, button: int = 0) -> bytes:
        return struct.pack(
            "<IIIiiibbh",
            self._uid,
            random.randint(0, 0xFFFFFFFF),
            cmd,
            x,
            y,
            wheel,
            button,
            0,
            0,
        )

    def send_move(self, x: int, y: int):
        self._sock.sendto(self._build_packet(_CMD_MOVE, x=x, y=y), self._addr)

    def send_click(self, delay_before_click: float = 0):
        time.sleep(delay_before_click)
        self.last_click_time = time.time()
        random_delay = (np.random.randint(40) + 40) / 1000
        self._sock.sendto(self._build_packet(_CMD_LEFT, button=1), self._addr)
        time.sleep(random_delay)
        self._sock.sendto(self._build_packet(_CMD_LEFT, button=0), self._addr)
        print(f"(KMBox) Sent: Click(random_delay={random_delay * 1000:g})")
        time.sleep((np.random.randint(10) + 25) / 1000)

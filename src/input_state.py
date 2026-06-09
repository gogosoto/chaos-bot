"""Cross-platform input state tracker using pynput listener threads.

Replaces win32api.GetAsyncKeyState() with a thread-safe set of currently
pressed keys and mouse buttons. Exposes is_vk_pressed() for drop-in
compatibility with Windows VK code checks.
"""

from pynput import keyboard, mouse

# Ensure mouse.Button has x1/x2 for extra buttons (macOS pynput only ships
# left/middle/right; Linux and Windows pynput include x1/x2 natively).
def _ensure_extra_mouse_buttons() -> None:
    """Patch mouse.Button with x1/x2 when missing (macOS pynput)."""
    if hasattr(mouse.Button, 'x1') and hasattr(mouse.Button, 'x2'):
        return
    try:
        from pynput.mouse._darwin import _button_value  # type: ignore[import]
        mouse.Button.x1 = _button_value('kCGEventOther', 3)  # type: ignore[attr-defined]
        mouse.Button.x2 = _button_value('kCGEventOther', 4)  # type: ignore[attr-defined]
    except (ImportError, AttributeError):
        # Non-Darwin platform that also lacks x1/x2 — create simple sentinels.
        class _ExtraButton:
            def __init__(self, name: str) -> None:
                self._name = name
            def __repr__(self) -> str:
                return f'Button.{self._name}'
        if not hasattr(mouse.Button, 'x1'):
            mouse.Button.x1 = _ExtraButton('x1')  # type: ignore[attr-defined]
        if not hasattr(mouse.Button, 'x2'):
            mouse.Button.x2 = _ExtraButton('x2')  # type: ignore[attr-defined]

_ensure_extra_mouse_buttons()

# Windows VK codes → pynput keyboard keys
_VK_KEY_MAP: dict[int, keyboard.Key] = {
    0x70: keyboard.Key.f1,
    0x71: keyboard.Key.f2,
    0x72: keyboard.Key.f3,
    0x73: keyboard.Key.f4,
    0x74: keyboard.Key.f5,
    0x75: keyboard.Key.f6,
    0x76: keyboard.Key.f7,
    0x77: keyboard.Key.f8,
    0x78: keyboard.Key.f9,
    0x79: keyboard.Key.f10,
    0x7A: keyboard.Key.f11,
    0x7B: keyboard.Key.f12,
}

# Windows VK codes → pynput mouse buttons
_VK_BUTTON_MAP: dict[int, mouse.Button] = {
    0x01: mouse.Button.left,
    0x02: mouse.Button.right,
    0x04: mouse.Button.middle,
    0x05: mouse.Button.x2,   # Mouse5 / XBUTTON2
    0x06: mouse.Button.x1,   # Mouse4 / XBUTTON1
}


def vk_to_pynput_key(vk: int) -> keyboard.Key:
    """Return the pynput Key for a Windows virtual-key code (keyboard)."""
    return _VK_KEY_MAP[vk]


def vk_to_pynput_button(vk: int) -> mouse.Button:
    """Return the pynput Button for a Windows virtual-key code (mouse)."""
    return _VK_BUTTON_MAP[vk]


class InputState:
    """Thread-safe key/button state tracker using pynput listeners."""

    def __init__(self) -> None:
        self._keys: set = set()
        self._buttons: set = set()

        self._kb = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._ms = mouse.Listener(on_click=self._on_click)
        self._kb.start()
        self._ms.start()

    def _on_key_press(self, key: keyboard.Key) -> None:
        self._keys.add(key)

    def _on_key_release(self, key: keyboard.Key) -> None:
        self._keys.discard(key)

    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        if pressed:
            self._buttons.add(button)
        else:
            self._buttons.discard(button)

    def is_key_pressed(self, key: keyboard.Key) -> bool:
        return key in self._keys

    def is_button_pressed(self, button: mouse.Button) -> bool:
        return button in self._buttons

    def is_vk_pressed(self, vk: int) -> bool:
        """Check if a Windows VK code is currently pressed (key or mouse button)."""
        if vk in _VK_KEY_MAP:
            return _VK_KEY_MAP[vk] in self._keys
        if vk in _VK_BUTTON_MAP:
            return _VK_BUTTON_MAP[vk] in self._buttons
        return False

    def stop(self) -> None:
        """Stop the background listener threads."""
        self._kb.stop()
        self._ms.stop()

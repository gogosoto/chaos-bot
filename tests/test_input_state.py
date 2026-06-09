import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import pytest
from unittest.mock import patch
from pynput import keyboard, mouse


def test_vk_to_pynput_key_f1():
    from input_state import vk_to_pynput_key
    assert vk_to_pynput_key(0x70) == keyboard.Key.f1


def test_vk_to_pynput_key_f2():
    from input_state import vk_to_pynput_key
    assert vk_to_pynput_key(0x71) == keyboard.Key.f2


def test_vk_to_pynput_key_f3():
    from input_state import vk_to_pynput_key
    assert vk_to_pynput_key(0x72) == keyboard.Key.f3


def test_vk_to_pynput_key_f4():
    from input_state import vk_to_pynput_key
    assert vk_to_pynput_key(0x73) == keyboard.Key.f4


def test_vk_to_pynput_button_left():
    from input_state import vk_to_pynput_button
    assert vk_to_pynput_button(0x01) == mouse.Button.left


def test_vk_to_pynput_button_right():
    from input_state import vk_to_pynput_button
    assert vk_to_pynput_button(0x02) == mouse.Button.right


def test_vk_to_pynput_button_x1_mouse4():
    from input_state import vk_to_pynput_button
    assert vk_to_pynput_button(0x06) == mouse.Button.x1


def test_vk_to_pynput_button_x2_mouse5():
    from input_state import vk_to_pynput_button
    assert vk_to_pynput_button(0x05) == mouse.Button.x2


def test_input_state_key_press_tracked():
    from input_state import InputState
    with patch('input_state.keyboard.Listener'), patch('input_state.mouse.Listener'):
        state = InputState()
        state._on_key_press(keyboard.Key.f1)
        assert state.is_key_pressed(keyboard.Key.f1) is True


def test_input_state_key_release_removes():
    from input_state import InputState
    with patch('input_state.keyboard.Listener'), patch('input_state.mouse.Listener'):
        state = InputState()
        state._on_key_press(keyboard.Key.f1)
        state._on_key_release(keyboard.Key.f1)
        assert state.is_key_pressed(keyboard.Key.f1) is False


def test_input_state_button_press_tracked():
    from input_state import InputState
    with patch('input_state.keyboard.Listener'), patch('input_state.mouse.Listener'):
        state = InputState()
        state._on_click(0, 0, mouse.Button.left, True)
        assert state.is_button_pressed(mouse.Button.left) is True


def test_input_state_button_release_removes():
    from input_state import InputState
    with patch('input_state.keyboard.Listener'), patch('input_state.mouse.Listener'):
        state = InputState()
        state._on_click(0, 0, mouse.Button.left, True)
        state._on_click(0, 0, mouse.Button.left, False)
        assert state.is_button_pressed(mouse.Button.left) is False


def test_is_vk_pressed_key_mapping():
    from input_state import InputState
    with patch('input_state.keyboard.Listener'), patch('input_state.mouse.Listener'):
        state = InputState()
        state._on_key_press(keyboard.Key.f1)
        assert state.is_vk_pressed(0x70) is True
        assert state.is_vk_pressed(0x71) is False


def test_is_vk_pressed_button_mapping():
    from input_state import InputState
    with patch('input_state.keyboard.Listener'), patch('input_state.mouse.Listener'):
        state = InputState()
        state._on_click(0, 0, mouse.Button.left, True)
        assert state.is_vk_pressed(0x01) is True
        assert state.is_vk_pressed(0x02) is False


def test_is_vk_pressed_unknown_vk_returns_false():
    from input_state import InputState
    with patch('input_state.keyboard.Listener'), patch('input_state.mouse.Listener'):
        state = InputState()
        assert state.is_vk_pressed(0xFF) is False

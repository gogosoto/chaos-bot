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
import time
from configReader import ConfigReader
from input_state import InputState


class Utils:
    def __init__(self):
        self.config = ConfigReader()
        self.reload_config()

        self.delay = 0.25
        self.key_reload_config = self.config.key_reload_config
        self.key_toggle_aim    = self.config.key_toggle_aim
        self.key_toggle_recoil = self.config.key_toggle_recoil
        self.key_exit          = self.config.key_exit
        self.key_trigger       = self.config.key_trigger
        self.key_rapid_fire    = self.config.key_rapid_fire
        self.aim_keys          = self.config.aim_keys
        self.aim_state         = False
        self.recoil_state      = False

        self.input = InputState()

    def check_key_binds(self):
        if self.input.is_vk_pressed(self.key_reload_config):
            return True

        if self.input.is_vk_pressed(self.key_toggle_aim):
            self.aim_state = not self.aim_state
            print("AIM: " + str(self.aim_state))
            time.sleep(self.delay)

        if self.input.is_vk_pressed(self.key_toggle_recoil):
            self.recoil_state = not self.recoil_state
            print("RECOIL: " + str(self.recoil_state))
            time.sleep(self.delay)

        if self.input.is_vk_pressed(self.key_exit):
            print("Exiting")
            self.input.stop()
            exit(1)

        return False

    def reload_config(self):
        self.config.read_config()

    def get_aim_state(self):
        if self.aim_state:
            if self.aim_keys[0] == 'off':
                return True
            for key in self.aim_keys:
                if self.input.is_vk_pressed(key):
                    return True
        return False

    def get_trigger_state(self):
        return self.input.is_vk_pressed(self.key_trigger)

    def get_rapid_fire_state(self):
        return self.input.is_vk_pressed(self.key_rapid_fire)

    def get_input_state(self):
        return self.input

    @staticmethod
    def print_attributes(obj):
        attributes = vars(obj)
        for attribute, value in attributes.items():
            print(f'{attribute}: {value}')

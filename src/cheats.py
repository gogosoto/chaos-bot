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
class Cheats:
    def __init__(self, config):
        self.cfg = config
        self.move_x, self.move_y = (0, 0)
        self.previous_x, self.previous_y = (0, 0)
        self.recoil_offset = 0

    def calculate_aim(self, state, target):
        if state and target is not None:
            x, y = target
            x *= getattr(self.cfg, 'scale_x', 1.0)
            y *= getattr(self.cfg, 'scale_y', 1.0)
            x *= self.cfg.speed
            y *= self.cfg.speed * self.cfg.y_speed_multiplier
            x = (1 - self.cfg.aim_smoothing_factor) * self.previous_x + self.cfg.aim_smoothing_factor * x
            y = (1 - self.cfg.aim_smoothing_factor) * self.previous_y + self.cfg.aim_smoothing_factor * y
            self.previous_x, self.previous_y = (x, y)
            self.move_x, self.move_y = (x, y)

    def apply_recoil(self, state, delta_time, input_state=None):
        left_held = input_state.is_vk_pressed(0x01) if input_state else False
        if state and delta_time != 0:
            if self.cfg.recoil_mode == 'move' and left_held:
                self.move_x += self.cfg.recoil_x * delta_time
                self.move_y += self.cfg.recoil_y * delta_time
            elif self.cfg.recoil_mode == 'offset':
                if left_held:
                    if self.recoil_offset < self.cfg.max_offset:
                        self.recoil_offset += self.cfg.recoil_y * delta_time
                        if self.recoil_offset > self.cfg.max_offset:
                            self.recoil_offset = self.cfg.max_offset
                else:
                    if self.recoil_offset > 0:
                        self.recoil_offset -= self.cfg.recoil_recover * delta_time
                        if self.recoil_offset < 0:
                            self.recoil_offset = 0
        else:
            self.recoil_offset = 0

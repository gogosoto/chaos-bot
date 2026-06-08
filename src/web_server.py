"""
    Unibot Web Control Server
    Flask-based dashboard for remote control over LAN.
    Access via http://local-ip:5000
"""
from flask import Flask, render_template, request, jsonify
import threading
import json
import os
from configReader import ConfigReader


class WebServer:
    """Flask server for remote Unibot control."""

    def __init__(self, config, host='0.0.0.0', port=5000):
        self.config = config
        self.host = host
        self.port = port
        self.app = Flask(__name__, template_folder='../templates', static_folder='../static')
        self.setup_routes()

        # State tracking
        self.bot_state = {
            'aim_enabled': False,
            'trigger_enabled': False,
            'rapid_fire_enabled': False,
            'recoil_enabled': False,
            'fps': 0,
            'target_detected': False,
            'detected_pose': 'unknown'
        }

        self.server_thread = None

    def setup_routes(self):
        """Setup Flask routes."""

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/api/state')
        def get_state():
            """Get current bot state."""
            return jsonify(self.bot_state)

        @self.app.route('/api/config')
        def get_config():
            """Get current config."""
            config_dict = {
                'aim': {
                    'speed': self.config.speed,
                    'smoothing': self.config.aim_smoothing_factor,
                    'y_multiplier': self.config.y_speed_multiplier,
                },
                'trigger': {
                    'delay': self.config.trigger_delay,
                    'threshold': self.config.trigger_threshold,
                },
                'rapid_fire': {
                    'cps': self.config.target_cps,
                },
                'recoil': {
                    'mode': self.config.recoil_mode,
                    'x': self.config.recoil_x,
                    'y': self.config.recoil_y,
                },
                'screen': {
                    'lower_color': list(self.config.lower_color),
                    'upper_color': list(self.config.upper_color),
                },
                'shape_validation': {
                    'enabled': self.config.shape_validation_enabled,
                    'aspect_ratio_min': self.config.aspect_ratio_min,
                    'aspect_ratio_max': self.config.aspect_ratio_max,
                    'min_convexity': self.config.min_convexity_score,
                    'min_solidity': self.config.min_solidity_score,
                },
                'pose_detection': {
                    'standing_threshold': self.config.pose_standing_threshold,
                    'crouching_threshold': self.config.pose_crouching_threshold,
                    'prone_threshold': self.config.pose_prone_threshold,
                }
            }
            return jsonify(config_dict)

        @self.app.route('/api/control', methods=['POST'])
        def control():
            """Handle control commands."""
            data = request.json
            action = data.get('action')

            if action == 'toggle_aim':
                self.bot_state['aim_enabled'] = not self.bot_state['aim_enabled']
            elif action == 'toggle_trigger':
                self.bot_state['trigger_enabled'] = not self.bot_state['trigger_enabled']
            elif action == 'toggle_rapid_fire':
                self.bot_state['rapid_fire_enabled'] = not self.bot_state['rapid_fire_enabled']
            elif action == 'toggle_recoil':
                self.bot_state['recoil_enabled'] = not self.bot_state['recoil_enabled']

            return jsonify({'status': 'ok', 'state': self.bot_state})

        @self.app.route('/api/config/update', methods=['POST'])
        def update_config():
            """Update config values."""
            data = request.json
            section = data.get('section')
            key = data.get('key')
            value = data.get('value')

            # Validate and update config attribute
            if hasattr(self.config, key):
                try:
                    # Type conversion
                    if isinstance(getattr(self.config, key), int):
                        setattr(self.config, key, int(value))
                    elif isinstance(getattr(self.config, key), float):
                        setattr(self.config, key, float(value))
                    elif isinstance(getattr(self.config, key), bool):
                        setattr(self.config, key, value in ['true', True, 1])
                    else:
                        setattr(self.config, key, value)
                    return jsonify({'status': 'ok', 'message': f'Updated {key}'})
                except Exception as e:
                    return jsonify({'status': 'error', 'message': str(e)}), 400
            return jsonify({'status': 'error', 'message': f'Config key {key} not found'}), 400

    def update_state(self, aim, trigger, rapid_fire, recoil, fps, target_detected, pose):
        """Update bot state (called from main bot loop)."""
        self.bot_state['aim_enabled'] = aim
        self.bot_state['trigger_enabled'] = trigger
        self.bot_state['rapid_fire_enabled'] = rapid_fire
        self.bot_state['recoil_enabled'] = recoil
        self.bot_state['fps'] = fps
        self.bot_state['target_detected'] = target_detected
        self.bot_state['detected_pose'] = pose

    def start(self):
        """Start web server in background thread."""
        self.server_thread = threading.Thread(
            target=lambda: self.app.run(host=self.host, port=self.port, debug=False),
            daemon=True
        )
        self.server_thread.start()
        print(f'Unibot Web Server started on http://0.0.0.0:{self.port}')

    def stop(self):
        """Stop web server."""
        if self.server_thread:
            # Flask doesn't have a clean shutdown via threading, but daemon=True handles it
            pass

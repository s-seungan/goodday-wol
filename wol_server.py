#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
좋은날금박 WOL 서버
24시간 클라우드 서버 (Render.com)
"""
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import socket
import os

app = Flask(__name__)
CORS(app)

# ★ 비밀번호 설정 — 여기서 변경하세요
WOL_PASSWORD = os.environ.get('WOL_PASSWORD', '5875')

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return send_from_directory('.', 'wol_remote_pc.html')

@app.route('/ping')
def ping():
    return jsonify({'status': 'ok'})

@app.route('/wake', methods=['POST'])
def wake_on_lan():
    try:
        data = request.json

        # ★ 비밀번호 확인
        if data.get('password') != WOL_PASSWORD:
            return jsonify({'success': False, 'message': '비밀번호가 틀렸습니다'}), 401

        mac_address = data.get('mac')
        ip_address = data.get('ip')
        port = int(data.get('port', 9))

        mac_address = mac_address.replace(':', '').replace('-', '')
        mac_bytes = bytes.fromhex(mac_address)
        magic_packet = b'\xff' * 6 + mac_bytes * 16

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, ('255.255.255.255', port))
        sock.sendto(magic_packet, (ip_address, port))
        sock.close()

        return jsonify({'success': True, 'message': 'WOL packet sent successfully'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/check', methods=['POST'])
def check_pc():
    try:
        data = request.json
        ip = data.get('ip')
        port = int(data.get('port', 3389))

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip, port))
        sock.close()

        return jsonify({'online': result == 0})
    except Exception as e:
        return jsonify({'online': False})

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Empty filename'}), 400
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return jsonify({'success': True, 'filename': file.filename})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Good Day Gold Foil - WOL Server Started!")
    print(f"Server running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

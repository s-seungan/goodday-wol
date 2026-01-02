#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
좋은날금박 WOL 서버
24시간 클라우드 서버 (Render.com)
PC 상태 확인 기능 포함
"""

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import socket
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'wol_remote_pc.html')

@app.route('/wake', methods=['POST'])
def wake_on_lan():
    try:
        data = request.json
        mac_address = data.get('mac')
        ip_address = data.get('ip')
        port = int(data.get('port', 9))
        
        # MAC 주소 정규화
        mac_address = mac_address.replace(':', '').replace('-', '')
        
        # Magic Packet 생성
        mac_bytes = bytes.fromhex(mac_address)
        magic_packet = b'\xff' * 6 + mac_bytes * 16
        
        # UDP 전송
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (ip_address, port))
        sock.close()
        
        return jsonify({
            'success': True,
            'message': 'WOL packet sent successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/check', methods=['POST'])
def check_pc_status():
    """PC 온라인 상태 확인 (TCP 포트 연결 테스트)"""
    try:
        data = request.json
        ip_address = data.get('ip')
        port = int(data.get('port', 3389))
        
        # TCP 연결 테스트 (타임아웃 3초)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        
        result = sock.connect_ex((ip_address, port))
        sock.close()
        
        online = (result == 0)
        
        return jsonify({
            'online': online,
            'ip': ip_address,
            'port': port,
            'message': 'PC is online' if online else 'PC is offline'
        })
        
    except socket.timeout:
        return jsonify({
            'online': False,
            'message': 'Connection timeout - PC is offline'
        })
    except Exception as e:
        return jsonify({
            'online': False,
            'message': str(e)
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Good Day Gold Foil - WOL Server Started!")
    print(f"Server running on port {port}")
    print(f"Features: WOL + PC Status Check")
    app.run(host='0.0.0.0', port=port, debug=False)

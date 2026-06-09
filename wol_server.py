#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
좋은날금박 WOL 서버
24시간 클라우드 서버 (Render.com)
"""

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import socket
import struct
import os

app = Flask(__name__)
CORS(app)

# 업로드 폴더 생성
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'filename': file.filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Good Day Gold Foil - WOL Server Started!")
    print(f"Server running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

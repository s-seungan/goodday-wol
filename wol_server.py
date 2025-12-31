#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
좋은날금박 원격 PC 부팅 서버
Wake on LAN 매직 패킷 전송 및 파일 관리
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import socket
import struct
import os
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)  # CORS 허용 (웹앱에서 접근 가능)

# 설정
CONFIG_FILE = 'wol_config.json'
UPLOAD_FOLDER = 'uploads'
LOG_FILE = 'wol_server.log'

# 업로드 폴더 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def log_message(message):
    """로그 기록"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    
    print(log_entry.strip())
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def send_magic_packet(mac_address, ip_address='255.255.255.255', port=9):
    """
    WOL 매직 패킷 전송
    
    Args:
        mac_address: MAC 주소 (AA:BB:CC:DD:EE:FF 또는 AA-BB-CC-DD-EE-FF)
        ip_address: 브로드캐스트 주소 또는 외부 IP
        port: WOL 포트 (기본 9)
    """
    try:
        # MAC 주소 정리 (구분자 제거)
        mac_address = mac_address.replace(':', '').replace('-', '').upper()
        
        if len(mac_address) != 12:
            raise ValueError(f"잘못된 MAC 주소 형식: {mac_address}")
        
        # MAC 주소를 바이트로 변환
        mac_bytes = bytes.fromhex(mac_address)
        
        # 매직 패킷 생성
        # 6바이트 0xFF + MAC 주소 16번 반복 = 102바이트
        magic_packet = b'\xff' * 6 + mac_bytes * 16
        
        # UDP 소켓 생성
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # 매직 패킷 전송
        sock.sendto(magic_packet, (ip_address, port))
        sock.close()
        
        log_message(f"✅ WOL 신호 전송 성공: MAC={mac_address}, IP={ip_address}:{port}")
        return True, "매직 패킷 전송 완료"
        
    except Exception as e:
        error_msg = f"❌ WOL 신호 전송 실패: {str(e)}"
        log_message(error_msg)
        return False, str(e)

def ping_host(ip_address, timeout=1):
    """
    호스트 핑 체크 (간단한 상태 확인)
    """
    try:
        # Windows와 Linux 모두 지원
        import platform
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = f"ping {param} 1 -w {timeout*1000} {ip_address}"
        
        response = os.system(command + " > nul 2>&1" if platform.system().lower() == 'windows' else command + " > /dev/null 2>&1")
        return response == 0
    except:
        return False

@app.route('/')
def index():
    """메인 페이지 - HTML 앱 제공"""
    return send_file('wol_remote_pc.html')

@app.route('/api/wake', methods=['POST'])
def wake_pc():
    """WOL 신호 전송 API"""
    try:
        data = request.json
        mac = data.get('mac')
        ip = data.get('ip', '255.255.255.255')
        port = int(data.get('port', 9))
        name = data.get('name', 'Unknown PC')
        
        if not mac:
            return jsonify({
                'success': False,
                'message': 'MAC 주소가 필요합니다'
            }), 400
        
        log_message(f"🚀 WOL 요청: {name} (MAC: {mac}, IP: {ip}:{port})")
        
        success, message = send_magic_packet(mac, ip, port)
        
        return jsonify({
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        log_message(f"❌ API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/status', methods=['POST'])
def check_status():
    """PC 상태 확인 API"""
    try:
        data = request.json
        ip = data.get('ip')
        
        if not ip:
            return jsonify({
                'success': False,
                'message': 'IP 주소가 필요합니다'
            }), 400
        
        # 간단한 핑 체크
        is_online = ping_host(ip)
        
        return jsonify({
            'success': True,
            'online': is_online,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    """파일 목록 조회"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return jsonify({
            'success': True,
            'files': files
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    """파일 업로드"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '파일이 없습니다'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '파일명이 없습니다'
            }), 400
        
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        log_message(f"📤 파일 업로드: {file.filename}")
        
        return jsonify({
            'success': True,
            'message': '파일 업로드 완료',
            'filename': file.filename
        })
        
    except Exception as e:
        log_message(f"❌ 파일 업로드 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/files/download/<filename>', methods=['GET'])
def download_file(filename):
    """파일 다운로드"""
    try:
        log_message(f"📥 파일 다운로드: {filename}")
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404

@app.route('/api/files/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """파일 삭제"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            log_message(f"🗑️ 파일 삭제: {filename}")
            return jsonify({
                'success': True,
                'message': '파일 삭제 완료'
            })
        else:
            return jsonify({
                'success': False,
                'message': '파일을 찾을 수 없습니다'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """로그 조회"""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                logs = f.readlines()
                # 최근 100줄만
                logs = logs[-100:]
        else:
            logs = []
        
        return jsonify({
            'success': True,
            'logs': logs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def print_server_info():
    """서버 정보 출력"""
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("\n" + "="*60)
    print("Good Day Gold Foil - WOL Server Started!")
    print("="*60)
    print(f"Local: http://localhost:5000")
    print(f"Network: http://{local_ip}:5000")
    print(f"Upload Folder: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"Log File: {os.path.abspath(LOG_FILE)}")
    print("="*60)
    print("How to use:")
    print("   1. Access the address above from smartphone/PC")
    print("   2. Register PC info (MAC address, IP)")
    print("   3. Click button to wake PC remotely!")
    print("="*60)
    print("To stop server: Ctrl+C\n")
    
    log_message("서버 시작됨")

if __name__ == '__main__':
    print_server_info()
    
    # 서버 실행
    # debug=False: 프로덕션 모드
    # host='0.0.0.0': 외부 접속 허용
    # port=5000: 포트 번호
    app.run(host='0.0.0.0', port=5000, debug=False)

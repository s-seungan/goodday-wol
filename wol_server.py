<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>좋은날금박 원격 PC 부팅</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; background-color: #707f7a; min-height: 100vh; padding: 15px; }
        .container { max-width: 900px; margin: 0 auto; background-color: rgba(200, 222, 186, 0.98); border: 8px solid #294731; border-radius: 25px; padding: 20px; box-shadow: 0 15px 50px rgba(0,0,0,0.3); }
        h1 { text-align: center; color: #294731; margin-bottom: 8px; font-size: 37px; font-weight: bold; }
        .top-buttons { display: flex; gap: 10px; margin-bottom: 8px; }
        .top-buttons button { flex: 1; padding: 12px; font-size: 25px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; }
        .add-pc-btn { background: #5A8348; color: white; }
        .add-pc-btn:hover { background: #6b9b57; }
        .refresh-all-btn { background: #478358; color: white; }
        .refresh-all-btn:hover { background: #4a7340; }
        .pc-list { margin-bottom: 10px; }
        .pc-item { background: #fff; border: 3px solid #478358; border-radius: 12px; padding: 15px; margin-bottom: 8px; }
        .pc-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; flex-wrap: wrap; }
        .status-light { width: 35px; height: 35px; border-radius: 50%; border: 3px solid #294731; flex-shrink: 0; }
        .status-light.online { background: radial-gradient(circle at 30% 30%, #7fff7f, #00cc00); box-shadow: 0 0 20px #00cc00, 0 0 40px #00cc00; animation: pulse-green 1.5s infinite; }
        .status-light.offline { background: radial-gradient(circle at 30% 30%, #ff7f7f, #cc0000); box-shadow: 0 0 15px #cc0000; }
        .status-light.checking { background: radial-gradient(circle at 30% 30%, #ffff7f, #cccc00); box-shadow: 0 0 15px #cccc00; animation: pulse-yellow 0.8s infinite; }
        .status-light.booting { background: radial-gradient(circle at 30% 30%, #7fbfff, #0080ff); box-shadow: 0 0 15px #0080ff; animation: pulse-blue 0.5s infinite; }
        @keyframes pulse-green { 0%, 100% { box-shadow: 0 0 20px #00cc00, 0 0 40px #00cc00; } 50% { box-shadow: 0 0 30px #00ff00, 0 0 60px #00ff00; } }
        @keyframes pulse-yellow { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        @keyframes pulse-blue { 0%, 100% { box-shadow: 0 0 15px #0080ff; } 50% { box-shadow: 0 0 30px #00bfff, 0 0 50px #00bfff; } }
        .status-text { font-size: 18px; font-weight: bold; padding: 5px 12px; border-radius: 15px; }
        .status-text.online { background: #d4edda; color: #155724; }
        .status-text.offline { background: #f8d7da; color: #721c24; }
        .status-text.checking { background: #fff3cd; color: #856404; }
        .status-text.booting { background: #cce5ff; color: #004085; }
        .pc-name { font-size: 28px; font-weight: bold; color: #294731; }
        .pc-info { font-size: 16px; color: #478358; margin-bottom: 5px; line-height: 1.4; }
        .progress-container { display: none; margin: 12px 0; background: #e9ecef; border: 2px solid #478358; border-radius: 10px; overflow: hidden; height: 30px; position: relative; }
        .progress-container.active { display: block; }
        .progress-bar { height: 100%; background: linear-gradient(90deg, #5A8348, #6b9b57); border-radius: 8px; transition: width 1s linear; }
        .progress-text { position: absolute; width: 100%; text-align: center; line-height: 30px; font-size: 14px; font-weight: bold; color: #294731; }
        .progress-time { text-align: center; font-size: 16px; color: #294731; margin-top: 5px; font-weight: bold; }
        .button-group { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
        .button-group button { flex: 1; min-width: 80px; padding: 12px; font-size: 18px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: all 0.3s; }
        .btn-wake { background: #5A8348; color: white; }
        .btn-wake:hover { background: #6b9b57; }
        .btn-wake:disabled { background: #aaa; cursor: not-allowed; }
        .btn-check { background: #478358; color: white; }
        .btn-check:hover { background: #4a7340; }
        .btn-rdp { background: #294731; color: white; }
        .btn-rdp:hover { background: #1e3525; }
        .btn-edit { background: #f39c12; color: white; max-width: 55px; }
        .btn-edit:hover { background: #e67e22; }
        .btn-delete { background: #e74c3c; color: white; max-width: 55px; }
        .btn-delete:hover { background: #c0392b; }
        .pc-log { background: #294731; color: #ecf0f1; padding: 10px; border-radius: 8px; max-height: 120px; overflow-y: auto; font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; font-size: 14px; margin-top: 12px; border: 2px solid #478358; }
        .pc-log-entry { margin-bottom: 4px; padding: 3px 6px; border-left: 3px solid #6b9b57; background: rgba(255,255,255,0.05); }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 1000; }
        .modal-content { background: rgba(200, 222, 186, 0.98); border: 5px solid #294731; max-width: 500px; margin: 30px auto; padding: 25px; border-radius: 20px; max-height: 90vh; overflow-y: auto; }
        .modal h2 { font-size: 28px; color: #294731; margin-bottom: 20px; }
        .form-group { margin-bottom: 8px; }
        label { display: block; font-size: 22px; font-weight: bold; color: #294731; margin-bottom: 6px; }
        input { width: 100%; padding: 12px; font-size: 24px; border: 3px solid #478358; border-radius: 8px; background: #fff; font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; }
        .help-text { font-size: 14px; color: #478358; margin-top: 4px; }
        .modal-buttons { display: flex; gap: 10px; margin-top: 20px; }
        .modal-buttons button { flex: 1; padding: 12px; font-size: 20px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; }
        .btn-save { background: #5A8348; color: white; }
        .btn-save:hover { background: #6b9b57; }
        .btn-cancel { background: #95a5a6; color: white; }
        .last-check { font-size: 14px; color: #666; margin-top: 3px; }
        @media (max-width: 768px) {
            h1 { font-size: 26px; } .pc-name { font-size: 22px; } .pc-info { font-size: 14px; }
            .top-buttons button { font-size: 16px; padding: 10px; }
            .button-group { flex-direction: column; }
            .button-group button { font-size: 16px; width: 100%; max-width: none; }
            .status-light { width: 30px; height: 30px; } .status-text { font-size: 16px; }
            .pc-log { font-size: 12px; max-height: 100px; }
            .container { padding: 12px; border-width: 5px; }
            .modal h2 { font-size: 24px; } label { font-size: 18px; } input { font-size: 20px; padding: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌟 좋은날금박 원격 PC</h1>

        <div id="serverStatus" style="text-align:center;margin-bottom:6px;font-size:16px;padding:6px;border-radius:8px;background:#294731;color:#c8deba;">
            ⏳ 서버 확인 중...
        </div>

        <div class="top-buttons">
            <button class="add-pc-btn" onclick="showAddModal()">+ PC 추가하기</button>
            <button class="refresh-all-btn" onclick="checkAllPCs()">🔄 전체 상태 확인</button>
        </div>
        <div class="top-buttons" style="margin-top:0;">
            <button style="flex:1;padding:10px;font-size:18px;font-weight:bold;background:#4a7c59;color:white;border:none;border-radius:10px;cursor:pointer;" onclick="showServerModal()">⚙️ 서버 주소 설정</button>
        </div>
        
        <div id="pcList" class="pc-list"></div>
    </div>
    
    <!-- PC 추가/수정 모달 -->
    <div id="addModal" class="modal">
        <div class="modal-content">
            <h2>PC 추가</h2>
            <div class="form-group"><label>PC 이름</label><input type="text" id="pcName" placeholder="예: 사무실 PC"></div>
            <div class="form-group"><label>MAC 주소</label><input type="text" id="macAddress" placeholder="예: 40-8D-5C-17-C4-AA"><div class="help-text">하이픈(-) 또는 콜론(:) 포함</div></div>
            <div class="form-group"><label>외부 IP 주소</label><input type="text" id="ipAddress" placeholder="예: 121.129.9.120"><div class="help-text">whatismyip.com에서 확인 (WoL·RDP용)</div></div>
            <div class="form-group"><label>내부 IP (사무실 LAN) ★</label><input type="text" id="localIp" placeholder="예: 172.30.1.26"><div class="help-text">★ 상태확인 정확도 향상 — cmd에서 ipconfig로 확인</div></div>
            <div class="form-group"><label>WOL 포트</label><input type="number" id="wolPort" value="9"></div>
            <div class="form-group"><label>원격 데스크톱 포트</label><input type="number" id="rdpPort" value="3389"></div>
            <div class="modal-buttons">
                <button class="btn-save" onclick="savePC()">저장</button>
                <button class="btn-cancel" onclick="closeModal()">취소</button>
            </div>
        </div>
    </div>

    <!-- ★ 비밀번호 입력 모달 -->
    <div id="pwModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.75);z-index:2000;justify-content:center;align-items:center;">
        <div style="background:#c8deba;border:6px solid #294731;border-radius:20px;padding:30px;max-width:380px;width:90%;margin:20px;text-align:center;">
            <div style="font-size:50px;margin-bottom:10px;">🔐</div>
            <h2 style="color:#294731;font-size:26px;margin-bottom:15px;">비밀번호 입력</h2>
            <input type="password" id="pwInput" placeholder="비밀번호"
                style="width:100%;padding:14px;font-size:22px;border:3px solid #294731;border-radius:10px;margin-bottom:15px;box-sizing:border-box;text-align:center;"
                onkeydown="if(event.key==='Enter')confirmPW()">
            <div id="pwError" style="color:#c0392b;font-size:16px;margin-bottom:10px;display:none;">❌ 비밀번호가 틀렸습니다</div>
            <div style="display:flex;gap:10px;">
                <button onclick="confirmPW()" style="flex:1;padding:14px;font-size:20px;background:#294731;color:white;border:none;border-radius:10px;cursor:pointer;font-weight:bold;">확인</button>
                <button onclick="closePWModal()" style="flex:1;padding:14px;font-size:20px;background:#888;color:white;border:none;border-radius:10px;cursor:pointer;">취소</button>
            </div>
        </div>
    </div>
    
    <!-- 서버 URL 설정 모달 -->
    <div id="serverModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);z-index:1000;justify-content:center;align-items:center;">
        <div style="background:#c8deba;border:6px solid #294731;border-radius:20px;padding:25px;max-width:420px;width:90%;margin:20px;">
            <h2 style="color:#294731;font-size:26px;margin-bottom:15px;text-align:center;">⚙️ 서버 주소 설정</h2>
            <input type="text" id="serverUrlInput" placeholder="https://goodday-wol.onrender.com"
                style="width:100%;padding:12px;font-size:18px;border:2px solid #294731;border-radius:10px;margin-bottom:10px;box-sizing:border-box;">
            <div style="display:flex;gap:10px;">
                <button onclick="saveServerUrl()" style="flex:1;padding:12px;font-size:20px;background:#294731;color:white;border:none;border-radius:10px;cursor:pointer;font-weight:bold;">저장</button>
                <button onclick="document.getElementById('serverModal').style.display='none'" style="flex:1;padding:12px;font-size:20px;background:#888;color:white;border:none;border-radius:10px;cursor:pointer;">취소</button>
            </div>
        </div>
    </div>

    <script>
        let serverUrl = localStorage.getItem('serverUrl') || '';
        let pcs = JSON.parse(localStorage.getItem('pcs') || '[]');
        let pcStatus = JSON.parse(localStorage.getItem('pcStatus') || '{}');
        let pcLogs = JSON.parse(localStorage.getItem('pcLogs') || '{}');
        let editingIndex = -1;
        let bootingTimers = {};

        // ★ 비밀번호 모달 관련
        let pendingWakeIndex = -1;

        function showWakeModal(index) {
            pendingWakeIndex = index;
            document.getElementById('pwInput').value = '';
            document.getElementById('pwError').style.display = 'none';
            document.getElementById('pwModal').style.display = 'flex';
            setTimeout(() => document.getElementById('pwInput').focus(), 100);
        }

        function closePWModal() {
            document.getElementById('pwModal').style.display = 'none';
            pendingWakeIndex = -1;
        }

        function confirmPW() {
            const pw = document.getElementById('pwInput').value;
            if (!pw) return;
            document.getElementById('pwModal').style.display = 'none';
            wakePC(pendingWakeIndex, pw);
            pendingWakeIndex = -1;
        }

        function showServerModal() {
            document.getElementById('serverUrlInput').value = serverUrl;
            document.getElementById('serverModal').style.display = 'flex';
        }

        function saveServerUrl() {
            const val = document.getElementById('serverUrlInput').value.trim().replace(/\/$/, '');
            serverUrl = val;
            localStorage.setItem('serverUrl', val);
            document.getElementById('serverModal').style.display = 'none';
            pingServer();
        }

        async function pingServer() {
            const statusEl = document.getElementById('serverStatus');
            if (!serverUrl) {
                statusEl.style.background = '#e74c3c';
                statusEl.textContent = '❌ 서버 주소 미설정 — ⚙️ 버튼 클릭하여 입력';
                return;
            }
            try {
                const r = await fetch(serverUrl + '/ping', { signal: AbortSignal.timeout(8000) });
                const d = await r.json();
                statusEl.style.background = '#294731';
                statusEl.textContent = '🟢 서버 연결됨: ' + serverUrl;
            } catch(e) {
                statusEl.style.background = '#c0392b';
                statusEl.textContent = '🔴 서버 응답 없음 (Render.com 슬립 중? 30초 후 재시도)';
            }
        }

        setInterval(pingServer, 14 * 60 * 1000);
        
        function renderPCs() {
            const list = document.getElementById('pcList');
            list.innerHTML = '';
            pcs.forEach((pc, index) => {
                const status = pcStatus[pc.ip] || { online: false, lastCheck: null, booting: false };
                let statusClass, statusText;
                if (status.booting) { statusClass = 'booting'; statusText = '🔵 부팅 중...'; }
                else if (status.checking) { statusClass = 'checking'; statusText = '🟡 확인 중...'; }
                else if (status.online) { statusClass = 'online'; statusText = '🟢 켜짐'; }
                else { statusClass = 'offline'; statusText = '🔴 꺼짐'; }
                const lastCheckText = status.lastCheck ? `마지막 확인: ${new Date(status.lastCheck).toLocaleTimeString('ko-KR')}` : '';
                const isBooting = status.booting;
                const progressPercent = status.bootProgress || 0;
                const remainingTime = status.remainingTime || 0;
                const logs = pcLogs[pc.ip] || [];
                const logHtml = logs.map(log => `<div class="pc-log-entry">${log}</div>`).join('');
                const item = document.createElement('div');
                item.className = 'pc-item';
                item.id = `pc-${index}`;
                item.innerHTML = `
                    <div class="pc-header">
                        <div class="status-light ${statusClass}"></div>
                        <div class="pc-name">${pc.name}</div>
                        <span class="status-text ${statusClass}">${statusText}</span>
                    </div>
                    <div class="pc-info">MAC: ${pc.mac}</div>
                    <div class="pc-info">IP: ${pc.ip}:${pc.wolPort}</div>
                    ${lastCheckText ? `<div class="last-check">${lastCheckText}</div>` : ''}
                    <div class="progress-container ${isBooting ? 'active' : ''}" id="progress-${index}">
                        <div class="progress-bar" style="width: ${progressPercent}%"></div>
                        <div class="progress-text">부팅 중... ${progressPercent}%</div>
                    </div>
                    ${isBooting ? `<div class="progress-time" id="time-${index}">⏱️ 남은 시간: ${Math.floor(remainingTime/60)}분 ${remainingTime%60}초</div>` : ''}
                    <div class="button-group">
                        <button class="btn-wake" onclick="showWakeModal(${index})" ${isBooting ? 'disabled' : ''}>⚡ PC 켜기</button>
                        <button class="btn-check" onclick="checkPC(${index})">🔍 상    태</button>
                        <button class="btn-rdp" onclick="connectRDP(${index})">🖥️ 원    격</button>
                        <button class="btn-edit" onclick="editPC(${index})">✏️</button>
                        <button class="btn-delete" onclick="deletePC(${index})">🗑️</button>
                    </div>
                    <div class="pc-log" id="log-${index}">
                        ${logHtml || '<div class="pc-log-entry">로그 없음</div>'}
                    </div>`;
                list.appendChild(item);
            });
        }

        function addPCLog(index, message) {
            const pc = pcs[index];
            if (!pc) return;
            const time = new Date().toLocaleTimeString('ko-KR');
            const logEntry = `[${time}] ${message}`;
            if (!pcLogs[pc.ip]) pcLogs[pc.ip] = [];
            pcLogs[pc.ip].unshift(logEntry);
            if (pcLogs[pc.ip].length > 10) pcLogs[pc.ip] = pcLogs[pc.ip].slice(0, 10);
            localStorage.setItem('pcLogs', JSON.stringify(pcLogs));
            const logDiv = document.getElementById(`log-${index}`);
            if (logDiv) {
                const entry = document.createElement('div');
                entry.className = 'pc-log-entry';
                entry.textContent = logEntry;
                logDiv.insertBefore(entry, logDiv.firstChild);
                while (logDiv.children.length > 10) logDiv.removeChild(logDiv.lastChild);
            }
        }

        function showAddModal() {
            editingIndex = -1;
            ['pcName','macAddress','ipAddress','localIp'].forEach(id => document.getElementById(id).value = '');
            document.getElementById('wolPort').value = '9';
            document.getElementById('rdpPort').value = '3389';
            document.getElementById('addModal').style.display = 'block';
        }

        function closeModal() { document.getElementById('addModal').style.display = 'none'; }

        function savePC() {
            const pc = {
                name: document.getElementById('pcName').value,
                mac: document.getElementById('macAddress').value,
                ip: document.getElementById('ipAddress').value,
                localIp: document.getElementById('localIp').value.trim(),
                wolPort: document.getElementById('wolPort').value,
                rdpPort: document.getElementById('rdpPort').value
            };
            if (!pc.name || !pc.mac || !pc.ip) { alert('모든 필수 항목을 입력하세요'); return; }
            if (editingIndex >= 0) pcs[editingIndex] = pc; else pcs.push(pc);
            localStorage.setItem('pcs', JSON.stringify(pcs));
            renderPCs();
            closeModal();
            const idx = editingIndex >= 0 ? editingIndex : pcs.length - 1;
            addPCLog(idx, `✅ PC ${editingIndex >= 0 ? '수정' : '추가'} 완료`);
        }

        function editPC(index) {
            editingIndex = index;
            const pc = pcs[index];
            document.getElementById('pcName').value = pc.name;
            document.getElementById('macAddress').value = pc.mac;
            document.getElementById('ipAddress').value = pc.ip;
            document.getElementById('localIp').value = pc.localIp || '';
            document.getElementById('wolPort').value = pc.wolPort;
            document.getElementById('rdpPort').value = pc.rdpPort;
            document.getElementById('addModal').style.display = 'block';
        }

        function deletePC(index) {
            if (confirm('정말 삭제하시겠습니까?')) {
                const pc = pcs[index];
                if (bootingTimers[index]) { clearInterval(bootingTimers[index]); delete bootingTimers[index]; }
                delete pcStatus[pc.ip]; delete pcLogs[pc.ip];
                localStorage.setItem('pcStatus', JSON.stringify(pcStatus));
                localStorage.setItem('pcLogs', JSON.stringify(pcLogs));
                pcs.splice(index, 1);
                localStorage.setItem('pcs', JSON.stringify(pcs));
                renderPCs();
            }
        }

        async function checkPC(index) {
            const pc = pcs[index];
            const checkIp = pc.localIp || pc.ip;
            addPCLog(index, `🔍 상태 확인 중...`);
            pcStatus[pc.ip] = { ...pcStatus[pc.ip], checking: true, booting: false };
            if (bootingTimers[index]) { clearInterval(bootingTimers[index]); delete bootingTimers[index]; }
            localStorage.setItem('pcStatus', JSON.stringify(pcStatus));
            renderPCs();
            try {
                const response = await fetch(serverUrl + '/check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip: checkIp, port: pc.rdpPort })
                });
                const result = await response.json();
                pcStatus[pc.ip] = { online: result.online, lastCheck: new Date().toISOString(), checking: false, booting: false };
                localStorage.setItem('pcStatus', JSON.stringify(pcStatus));
                renderPCs();
                addPCLog(index, result.online ? `🟢 켜져 있음! ✅` : `🔴 꺼져 있음`);
            } catch (error) {
                pcStatus[pc.ip] = { online: false, lastCheck: new Date().toISOString(), checking: false, booting: false };
                localStorage.setItem('pcStatus', JSON.stringify(pcStatus));
                renderPCs();
                addPCLog(index, `🔴 응답 없음`);
            }
        }

        async function checkAllPCs() {
            for (let i = 0; i < pcs.length; i++) {
                await checkPC(i);
                if (i < pcs.length - 1) await new Promise(r => setTimeout(r, 500));
            }
        }

        // ★ 비밀번호 받아서 서버로 전송
        async function wakePC(index, password) {
            const pc = pcs[index];
            addPCLog(index, `⚡ WOL 신호 전송 중...`);
            try {
                const response = await fetch(serverUrl + '/wake', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mac: pc.mac, ip: pc.ip, port: pc.wolPort, password: password })
                });
                const result = await response.json();
                if (result.success) {
                    addPCLog(index, `✅ WOL 신호 전송 완료!`);
                    addPCLog(index, `⏳ 부팅 대기 중... (2분)`);
                    startBootProgress(index, pc);
                } else {
                    // ★ 비밀번호 틀렸을 때
                    if (response.status === 401) {
                        addPCLog(index, `❌ 비밀번호 오류`);
                        document.getElementById('pwError').style.display = 'block';
                        document.getElementById('pwModal').style.display = 'flex';
                        pendingWakeIndex = index;
                    } else {
                        addPCLog(index, `❌ 오류: ${result.message}`);
                    }
                }
            } catch (error) {
                addPCLog(index, `❌ 전송 실패: ${error.message}`);
            }
        }

        function startBootProgress(index, pc) {
            const totalTime = 120;
            let elapsed = 0;
            pcStatus[pc.ip] = { ...pcStatus[pc.ip], booting: true, bootProgress: 0, remainingTime: totalTime };
            localStorage.setItem('pcStatus', JSON.stringify(pcStatus));
            renderPCs();
            if (bootingTimers[index]) clearInterval(bootingTimers[index]);
            bootingTimers[index] = setInterval(() => {
                elapsed++;
                const progress = Math.min(Math.round((elapsed / totalTime) * 100), 100);
                const remaining = totalTime - elapsed;
                pcStatus[pc.ip] = { ...pcStatus[pc.ip], bootProgress: progress, remainingTime: remaining };
                localStorage.setItem('pcStatus', JSON.stringify(pcStatus));
                const progressBar = document.querySelector(`#progress-${index} .progress-bar`);
                const progressText = document.querySelector(`#progress-${index} .progress-text`);
                const timeText = document.getElementById(`time-${index}`);
                if (progressBar) progressBar.style.width = `${progress}%`;
                if (progressText) progressText.textContent = `부팅 중... ${progress}%`;
                if (timeText) timeText.textContent = `⏱️ 남은 시간: ${Math.floor(remaining/60)}분 ${remaining%60}초`;
                if (elapsed >= totalTime) {
                    clearInterval(bootingTimers[index]);
                    delete bootingTimers[index];
                    addPCLog(index, `🔍 자동 상태 확인...`);
                    checkPC(index);
                }
            }, 1000);
        }

        function connectRDP(index) {
            const pc = pcs[index];
            const rdpContent = [`full address:s:${pc.ip}:${pc.rdpPort}`,`prompt for credentials:i:1`,`administrative session:i:1`,`screen mode id:i:2`,`compression:i:1`,`autoreconnection enabled:i:1`].join('\r\n');
            const blob = new Blob([rdpContent], { type: 'application/rdp' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url; a.download = `${pc.name}.rdp`;
            document.body.appendChild(a); a.click();
            document.body.removeChild(a); URL.revokeObjectURL(url);
            addPCLog(index, `🖥️ ${pc.name}.rdp 다운로드`);
        }

        renderPCs();
        pingServer();
        if (pcs.length > 0) setTimeout(checkAllPCs, 1500);
    </script>
</body>
</html>

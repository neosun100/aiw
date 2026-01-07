"""Web UI HTML Templates"""

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIW · AI Workspace Manager</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css">
    <script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-web-links@0.9.0/lib/xterm-addon-web-links.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0a0e27; color: #fff; min-height: 100vh; }
        body::before { content: ''; position: fixed; inset: 0; background: radial-gradient(circle at 20% 50%, rgba(120,119,198,0.15) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(99,102,241,0.15) 0%, transparent 50%); pointer-events: none; z-index: 0; }
        .container { max-width: 1800px; margin: 0 auto; padding: 30px 20px; position: relative; z-index: 1; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; font-weight: 700; background: linear-gradient(135deg, #667eea, #764ba2, #f093fb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .header .subtitle { color: rgba(255,255,255,0.5); font-size: 0.9em; margin-top: 5px; }
        .controls { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; flex-wrap: wrap; gap: 15px; }
        .btn { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; border: none; padding: 12px 24px; border-radius: 10px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 8px; transition: all 0.3s; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(102,126,234,0.4); }
        .btn-secondary { background: rgba(255,255,255,0.1); }
        .btn-danger { background: linear-gradient(135deg, #ef4444, #dc2626); }
        .stat-badge { background: linear-gradient(135deg, #f093fb, #f5576c); padding: 10px 20px; border-radius: 10px; font-weight: 600; }
        
        /* 主布局 */
        .main-layout { display: grid; grid-template-columns: 280px 1fr; gap: 20px; height: calc(100vh - 200px); min-height: 500px; transition: grid-template-columns 0.3s; }
        .main-layout.sidebar-collapsed { grid-template-columns: 50px 1fr; }
        .main-layout.fullscreen { position: fixed; inset: 0; height: 100vh; z-index: 100; grid-template-columns: 1fr; gap: 0; background: #0a0e27; }
        
        /* 侧边栏 */
        .sidebar { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; transition: all 0.3s; }
        .sidebar-collapsed .sidebar { border-radius: 12px; }
        .sidebar-header { padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); font-weight: 600; color: rgba(255,255,255,0.7); display: flex; justify-content: space-between; align-items: center; }
        .sidebar-toggle { background: none; border: none; color: rgba(255,255,255,0.6); cursor: pointer; font-size: 16px; padding: 4px 8px; border-radius: 4px; }
        .sidebar-toggle:hover { background: rgba(255,255,255,0.1); color: #fff; }
        .sidebar-collapsed .sidebar-header span { display: none; }
        .sidebar-collapsed .sidebar-toggle { transform: rotate(180deg); }
        .workspace-list { flex: 1; overflow-y: auto; }
        .sidebar-collapsed .workspace-list { display: none; }
        .fullscreen .sidebar { display: none; }
        .ws-item { padding: 12px 15px; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.05); transition: all 0.2s; display: flex; align-items: center; gap: 10px; }
        .ws-item:hover { background: rgba(255,255,255,0.05); }
        .ws-item.active { background: rgba(102,126,234,0.2); border-left: 3px solid #667eea; }
        .ws-item .dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; flex-shrink: 0; }
        .ws-item .info { flex: 1; min-width: 0; }
        .ws-item .name { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .ws-item .meta { font-size: 0.75em; color: rgba(255,255,255,0.5); margin-top: 2px; }
        .ws-item .edit-btn { opacity: 0; background: none; border: none; color: rgba(255,255,255,0.5); cursor: pointer; padding: 4px; font-size: 12px; }
        .ws-item:hover .edit-btn { opacity: 1; }
        .ws-item .edit-btn:hover { color: #667eea; }
        
        /* 终端区域 */
        .terminal-area { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; transition: all 0.3s; }
        .fullscreen .terminal-area { border-radius: 0; border: none; }
        .terminal-header { padding: 12px 20px; background: rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; }
        .fullscreen .terminal-header { padding: 8px 15px; }
        .terminal-title { font-weight: 600; display: flex; align-items: center; gap: 10px; }
        .terminal-title .badge { background: linear-gradient(135deg, #667eea, #764ba2); padding: 4px 10px; border-radius: 6px; font-size: 0.8em; }
        .terminal-actions { display: flex; gap: 8px; }
        .terminal-actions button { background: rgba(255,255,255,0.1); border: none; color: #fff; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.85em; }
        .terminal-actions button:hover { background: rgba(255,255,255,0.2); }
        .terminal-container { flex: 1; padding: 10px; display: flex; flex-direction: column; }
        .terminal-container .xterm { flex: 1; height: 100% !important; }
        .terminal-container .xterm-viewport { height: 100% !important; }
        .terminal-placeholder { flex: 1; display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0.4); }
        
        /* Modal */
        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 1000; }
        .modal.show { display: flex; }
        .modal-content { background: #16213e; padding: 25px; border-radius: 16px; min-width: 380px; border: 1px solid rgba(255,255,255,0.1); }
        .modal-content h3 { margin-bottom: 20px; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; margin-bottom: 6px; color: rgba(255,255,255,0.7); font-size: 0.9em; }
        .form-group input, .form-group select { width: 100%; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.2); padding: 10px 12px; border-radius: 8px; }
        .form-group input:focus, .form-group select:focus { outline: none; border-color: #667eea; }
        .modal-actions { display: flex; gap: 10px; margin-top: 20px; }
        .modal-actions .btn { flex: 1; justify-content: center; }
        
        @media (max-width: 900px) { .main-layout { grid-template-columns: 1fr; } .sidebar { max-height: 200px; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI WORKSPACE</h1>
            <p class="subtitle">Multi-Agent Management Platform</p>
        </div>
        
        <div class="controls">
            <div style="display:flex;gap:10px;">
                <button class="btn" onclick="showNewModal()">➕ New</button>
                <button class="btn btn-secondary" onclick="refresh()">🔄 Refresh</button>
            </div>
            <div class="stat-badge">Workspaces: <span id="wsCount">0</span></div>
        </div>
        
        <div class="main-layout" id="mainLayout">
            <div class="sidebar">
                <div class="sidebar-header"><span>📋 Workspaces</span><button class="sidebar-toggle" onclick="toggleSidebar()" title="Toggle sidebar">◀</button></div>
                <div class="workspace-list" id="workspaceList"></div>
            </div>
            
            <div class="terminal-area">
                <div class="terminal-header" id="terminalHeader" style="display:none;">
                    <div class="terminal-title">
                        <span id="terminalName">-</span>
                        <span class="badge" id="terminalTool">-</span>
                    </div>
                    <div class="terminal-actions">
                        <button onclick="toggleFullscreen()" id="fullscreenBtn">⛶ Fullscreen</button>
                        <button onclick="disconnectTerminal()">⏹ Disconnect</button>
                        <button onclick="killCurrent()" style="background:rgba(239,68,68,0.3);">🗑 Kill</button>
                    </div>
                </div>
                <div class="terminal-container" id="terminalContainer" style="display:none;"></div>
                <div class="terminal-placeholder" id="terminalPlaceholder">
                    <div style="text-align:center;">
                        <div style="font-size:3em;margin-bottom:15px;">🖥️</div>
                        <div>Select a workspace to connect</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- New Workspace Modal -->
    <div id="newModal" class="modal">
        <div class="modal-content">
            <h3>🚀 New Workspace</h3>
            <div class="form-group"><label>Name *</label><input id="newName" placeholder="e.g. api-dev" /></div>
            <div class="form-group"><label>AI Tool</label><select id="newTool"></select></div>
            <div class="form-group"><label>Model</label><select id="newModel"></select></div>
            <div class="form-group"><label>Working Directory</label><input id="newDir" placeholder="Optional" /></div>
            <div class="form-group"><label>Description</label><input id="newDesc" placeholder="Optional" /></div>
            <div class="modal-actions">
                <button class="btn" onclick="createWorkspace()">Create</button>
                <button class="btn btn-secondary" onclick="hideModal('newModal')">Cancel</button>
            </div>
        </div>
    </div>
    
    <!-- Edit Workspace Modal -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <h3>✏️ Edit Workspace</h3>
            <div class="form-group"><label>Name</label><input id="editName" /></div>
            <div class="modal-actions">
                <button class="btn" onclick="saveEdit()">Save</button>
                <button class="btn btn-secondary" onclick="hideModal('editModal')">Cancel</button>
            </div>
        </div>
    </div>

    <script>
        let tools = {}, defaultTool = 'gemini', workspaces = [], currentWs = null;
        let term = null, termWs = null, fitAddon = null;
        
        async function init() {
            const res = await fetch('/api/tools');
            const data = await res.json();
            tools = data.tools; defaultTool = data.default;
            
            const sel = document.getElementById('newTool');
            sel.innerHTML = Object.keys(tools).map(t => `<option value="${t}" ${t===defaultTool?'selected':''}>${t}</option>`).join('');
            sel.onchange = updateModels;
            updateModels();
            
            connectStatusWS();
        }
        
        function updateModels() {
            const t = document.getElementById('newTool').value;
            const models = tools[t]?.models || [];
            const def = tools[t]?.default_model || '';
            document.getElementById('newModel').innerHTML = models.map(m => `<option value="${m}" ${m===def?'selected':''}>${m}</option>`).join('');
        }
        
        function connectStatusWS() {
            const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(`${proto}//${location.host}/ws`);
            ws.onmessage = (e) => renderList(JSON.parse(e.data));
            ws.onclose = () => setTimeout(connectStatusWS, 3000);
        }
        
        function renderList(data) {
            workspaces = data.workspaces;
            document.getElementById('wsCount').textContent = data.count;
            
            const list = document.getElementById('workspaceList');
            if (data.count === 0) {
                list.innerHTML = '<div style="padding:20px;text-align:center;color:rgba(255,255,255,0.4);">No workspaces</div>';
                return;
            }
            
            list.innerHTML = data.workspaces.map(ws => `
                <div class="ws-item ${currentWs===ws.name?'active':''}" data-name="${ws.name}">
                    <div class="dot"></div>
                    <div class="info" onclick="connectTo('${ws.name}')">
                        <div class="name">${esc(ws.name)}</div>
                        <div class="meta">${ws.tool} · ${ws.model}</div>
                    </div>
                    <button class="edit-btn" onclick="event.stopPropagation();showEditModal('${ws.name}')" title="Edit">✏️</button>
                </div>
            `).join('');
        }
        
        function connectTo(name) {
            if (currentWs === name && term) return;
            disconnectTerminal();
            currentWs = name;
            
            const ws = workspaces.find(w => w.name === name);
            document.getElementById('terminalName').textContent = name;
            document.getElementById('terminalTool').textContent = ws ? ws.tool : '';
            document.getElementById('terminalHeader').style.display = 'flex';
            document.getElementById('terminalPlaceholder').style.display = 'none';
            document.getElementById('terminalContainer').style.display = 'block';
            
            // 更新侧边栏选中状态
            document.querySelectorAll('.ws-item').forEach(el => el.classList.remove('active'));
            document.querySelector(`.ws-item[onclick="connectTo('${name}')"]`)?.classList.add('active');
            
            // 初始化 xterm.js
            term = new Terminal({
                cursorBlink: true,
                fontSize: 14,
                fontFamily: '"Cascadia Code", "Fira Code", Menlo, monospace',
                theme: { background: '#0d1117', foreground: '#c9d1d9', cursor: '#58a6ff', selection: 'rgba(56,139,253,0.4)' },
                allowProposedApi: true
            });
            
            fitAddon = new FitAddon.FitAddon();
            term.loadAddon(fitAddon);
            term.loadAddon(new WebLinksAddon.WebLinksAddon());
            
            const container = document.getElementById('terminalContainer');
            container.innerHTML = '';
            term.open(container);
            fitAddon.fit();
            
            // 连接 WebSocket
            const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
            termWs = new WebSocket(`${proto}//${location.host}/ws/terminal/${name}`);
            termWs.binaryType = 'arraybuffer';
            
            termWs.onopen = () => {
                // 发送初始大小
                termWs.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
            };
            
            termWs.onmessage = (e) => {
                if (e.data instanceof ArrayBuffer) {
                    term.write(new Uint8Array(e.data));
                } else {
                    term.write(e.data);
                }
            };
            
            termWs.onclose = () => {
                term?.write('\\r\\n\\x1b[33m[Disconnected]\\x1b[0m\\r\\n');
            };
            
            // 终端输入发送到 WebSocket
            term.onData(data => {
                if (termWs?.readyState === WebSocket.OPEN) {
                    termWs.send(new TextEncoder().encode(data));
                }
            });
            
            // 窗口大小变化
            window.addEventListener('resize', handleResize);
            term.focus();
        }
        
        function handleResize() {
            if (fitAddon && term) {
                fitAddon.fit();
                if (termWs?.readyState === WebSocket.OPEN) {
                    termWs.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
                }
            }
        }
        
        function disconnectTerminal() {
            if (termWs) { termWs.close(); termWs = null; }
            if (term) { term.dispose(); term = null; }
            currentWs = null;
            document.getElementById('terminalHeader').style.display = 'none';
            document.getElementById('terminalContainer').style.display = 'none';
            document.getElementById('terminalPlaceholder').style.display = 'flex';
            document.querySelectorAll('.ws-item').forEach(el => el.classList.remove('active'));
            window.removeEventListener('resize', handleResize);
        }
        
        async function killCurrent() {
            if (!currentWs || !confirm(`Kill workspace "${currentWs}"?`)) return;
            await fetch(`/api/workspaces/${currentWs}`, { method: 'DELETE' });
            disconnectTerminal();
        }
        
        function esc(s) { return s ? s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') : ''; }
        function showModal(id) { document.getElementById(id).classList.add('show'); }
        function hideModal(id) { document.getElementById(id).classList.remove('show'); }
        function showNewModal() { showModal('newModal'); document.getElementById('newName').focus(); }
        function refresh() { location.reload(); }
        
        function toggleSidebar() {
            document.getElementById('mainLayout').classList.toggle('sidebar-collapsed');
            setTimeout(handleResize, 300);
        }
        
        function toggleFullscreen() {
            const layout = document.getElementById('mainLayout');
            layout.classList.toggle('fullscreen');
            const btn = document.getElementById('fullscreenBtn');
            btn.textContent = layout.classList.contains('fullscreen') ? '⛶ Exit' : '⛶ Fullscreen';
            // 延迟 fit 确保布局完成
            setTimeout(() => { if (fitAddon && term) { fitAddon.fit(); handleResize(); } }, 100);
            setTimeout(() => { if (fitAddon && term) { fitAddon.fit(); handleResize(); } }, 300);
        }
        
        let editingWs = null;
        function showEditModal(name) {
            editingWs = name;
            document.getElementById('editName').value = name;
            showModal('editModal');
            document.getElementById('editName').focus();
            document.getElementById('editName').select();
        }
        
        async function saveEdit() {
            const newName = document.getElementById('editName').value.trim();
            if (!newName || newName === editingWs) { hideModal('editModal'); return; }
            
            try {
                const res = await fetch(`/api/workspaces/${editingWs}/rename?new_name=${encodeURIComponent(newName)}`, { method: 'POST' });
                if (!res.ok) throw new Error((await res.json()).detail);
                if (currentWs === editingWs) currentWs = newName;
                hideModal('editModal');
            } catch (e) { alert('Error: ' + e.message); }
        }
        
        async function createWorkspace() {
            const name = document.getElementById('newName').value.trim();
            if (!name) { alert('Name required'); return; }
            
            const body = { name, tool: document.getElementById('newTool').value, model: document.getElementById('newModel').value, dir: document.getElementById('newDir').value || null, desc: document.getElementById('newDesc').value };
            
            try {
                const res = await fetch('/api/workspaces', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
                if (!res.ok) throw new Error((await res.json()).detail);
                hideModal('newModal');
                ['newName','newDir','newDesc'].forEach(id => document.getElementById(id).value = '');
                setTimeout(() => connectTo(name), 500);
            } catch (e) { alert('Error: ' + e.message); }
        }
        
        document.addEventListener('keydown', e => {
            // Esc 退出全屏或关闭弹窗
            if (e.key === 'Escape') {
                if (document.getElementById('mainLayout').classList.contains('fullscreen')) { toggleFullscreen(); return; }
                hideModal('newModal'); hideModal('editModal');
                return;
            }
            if (e.key === 'Enter' && document.getElementById('newModal').classList.contains('show')) { createWorkspace(); return; }
            if (e.key === 'Enter' && document.getElementById('editModal').classList.contains('show')) { saveEdit(); return; }
            
            // 快捷键 (当不在输入框时)
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
            
            const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
            const mod = isMac ? e.metaKey : e.ctrlKey;  // Mac 用 Cmd, 其他用 Ctrl
            
            // Cmd/Ctrl+Shift+F: 全屏切换
            if (mod && e.shiftKey && e.key.toLowerCase() === 'f') { e.preventDefault(); toggleFullscreen(); return; }
            // Cmd/Ctrl+Shift+B: 侧边栏切换
            if (mod && e.shiftKey && e.key.toLowerCase() === 'b') { e.preventDefault(); toggleSidebar(); return; }
            // Cmd/Ctrl+Shift+N: 新建 workspace
            if (mod && e.shiftKey && e.key.toLowerCase() === 'n') { e.preventDefault(); showNewModal(); return; }
            
            // ↑/↓: 切换 workspace (无修饰键，终端未聚焦时)
            if (!e.ctrlKey && !e.metaKey && !e.altKey && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
                if (!term || document.activeElement !== document.querySelector('.xterm-helper-textarea')) {
                    e.preventDefault();
                    switchWorkspace(e.key === 'ArrowUp' ? -1 : 1);
                    return;
                }
            }
            
            // 1-9: 快速切换到第 N 个 workspace (无修饰键)
            if (!e.ctrlKey && !e.metaKey && !e.altKey && e.key >= '1' && e.key <= '9') {
                if (!term || document.activeElement !== document.querySelector('.xterm-helper-textarea')) {
                    const idx = parseInt(e.key) - 1;
                    if (workspaces[idx]) { e.preventDefault(); connectTo(workspaces[idx].name); }
                }
            }
        });
        
        function switchWorkspace(dir) {
            if (workspaces.length === 0) return;
            const idx = workspaces.findIndex(w => w.name === currentWs);
            let newIdx = idx === -1 ? 0 : idx + dir;
            if (newIdx < 0) newIdx = workspaces.length - 1;
            if (newIdx >= workspaces.length) newIdx = 0;
            connectTo(workspaces[newIdx].name);
        }
        
        init();
    </script>
</body>
</html>
'''

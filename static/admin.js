// 管理后台JavaScript
const API_BASE = '/api';
let currentPage = 1;
let totalPages = 1;

// 页面加载时检查登录状态
document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
});

// 检查登录状态
async function checkLoginStatus() {
    try {
        const response = await fetch(`${API_BASE}/admin/check`, {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.success && data.data.logged_in) {
            showAdminPanel(data.data.username);
            loadConfig();
        }
    } catch (error) {
        console.error('检查登录状态失败:', error);
    }
}

// 处理登录
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const loginBtn = document.getElementById('loginBtn');
    
    // 禁用按钮
    loginBtn.disabled = true;
    loginBtn.textContent = '登录中...';
    
    try {
        const response = await fetch(`${API_BASE}/admin/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('loginMessage', data.message, 'success');
            setTimeout(() => {
                showAdminPanel(data.data.username);
                loadConfig();
            }, 500);
        } else {
            showMessage('loginMessage', data.message, 'error');
        }
    } catch (error) {
        showMessage('loginMessage', '登录失败，请检查网络连接', 'error');
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = '登录';
    }
}

// 处理退出登录
async function handleLogout() {
    if (!confirm('确定要退出登录吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/admin/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showLoginForm();
            // 清空表单
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
        }
    } catch (error) {
        alert('退出登录失败');
    }
}

// 显示管理面板
function showAdminPanel(username) {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('adminPanel').classList.add('active');
    document.getElementById('currentUser').textContent = username;
}

// 显示登录表单
function showLoginForm() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('adminPanel').classList.remove('active');
}

// 加载配置
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('mainTitle').value = data.data.main_title;
            document.getElementById('subTitle').value = data.data.sub_title;
        }
    } catch (error) {
        console.error('加载配置失败:', error);
    }
}

// 更新配置
async function handleUpdateConfig(event) {
    event.preventDefault();
    
    const mainTitle = document.getElementById('mainTitle').value.trim();
    const subTitle = document.getElementById('subTitle').value.trim();
    const saveBtn = document.getElementById('saveBtn');
    
    if (!mainTitle) {
        showMessage('configMessage', '主标题不能为空', 'error');
        return;
    }
    
    saveBtn.disabled = true;
    saveBtn.textContent = '保存中...';
    
    try {
        const response = await fetch(`${API_BASE}/admin/config`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                main_title: mainTitle,
                sub_title: subTitle
            })
        });
        
        const data = await response.json();
        
        if (response.status === 401) {
            alert('登录已过期，请重新登录');
            showLoginForm();
            return;
        }
        
        if (data.success) {
            showMessage('configMessage', '配置更新成功！', 'success');
            // 3秒后隐藏消息
            setTimeout(() => {
                hideMessage('configMessage');
            }, 3000);
        } else {
            showMessage('configMessage', data.message, 'error');
        }
    } catch (error) {
        showMessage('configMessage', '更新失败，请检查网络连接', 'error');
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = '保存修改';
    }
}

// 切换标签页
function switchTab(tabName) {
    // 更新标签按钮状态
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    
    // 更新内容显示
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    if (tabName === 'config') {
        document.getElementById('configTab').classList.add('active');
    } else if (tabName === 'logs') {
        document.getElementById('logsTab').classList.add('active');
        loadLogs(1);
    }
}

// 加载日志
async function loadLogs(page = 1) {
    if (page < 1) return;
    
    const logsContainer = document.getElementById('logsContainer');
    logsContainer.innerHTML = '<div class="loading">正在加载日志...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/admin/logs?page=${page}&page_size=20`, {
            credentials: 'include'
        });
        
        if (response.status === 401) {
            alert('登录已过期，请重新登录');
            showLoginForm();
            return;
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentPage = data.data.page;
            totalPages = data.data.total_pages;
            
            // 更新统计
            document.getElementById('totalLogs').textContent = data.data.total;
            
            // 显示日志
            if (data.data.logs.length === 0) {
                logsContainer.innerHTML = '<div class="loading">暂无访问记录</div>';
            } else {
                logsContainer.innerHTML = data.data.logs.map(log => `
                    <div class="log-item">
                        <div class="log-time">${log.access_time}</div>
                        <div class="log-ip">IP: ${log.ip_address}</div>
                        <div class="log-agent">${log.user_agent || '未知设备'}</div>
                    </div>
                `).join('');
            }
            
            // 更新分页按钮
            document.getElementById('prevPage').disabled = currentPage <= 1;
            document.getElementById('nextPage').disabled = currentPage >= totalPages;
            document.getElementById('pageInfo').textContent = `第 ${currentPage} / ${totalPages} 页`;
        }
    } catch (error) {
        logsContainer.innerHTML = '<div class="loading">加载失败，请稍后重试</div>';
        console.error('加载日志失败:', error);
    }
}

// 显示消息
function showMessage(elementId, message, type) {
    const messageEl = document.getElementById(elementId);
    messageEl.textContent = message;
    messageEl.className = `message ${type} active`;
}

// 隐藏消息
function hideMessage(elementId) {
    const messageEl = document.getElementById(elementId);
    messageEl.classList.remove('active');
}

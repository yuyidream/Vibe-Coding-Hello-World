# -*- coding: utf-8 -*-
"""
Flask应用主文件
提供API接口和路由处理
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import logging
from datetime import datetime
import os

from config import config, Config
from database import Database

# 创建Flask应用
app = Flask(__name__)

# 加载配置
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# 启用CORS
CORS(app, supports_credentials=True)

# 配置日志
logging.basicConfig(
    level=getattr(logging, app.config['LOG_LEVEL']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化数据库（传入Config类而不是app.config字典）
db = Database(Config)


# ==================== 工具函数 ====================

def get_client_ip():
    """获取客户端IP地址"""
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    elif request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        return request.remote_addr


def require_login(f):
    """登录验证装饰器"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'success': False, 'message': '未登录或登录已过期'}), 401
        return f(*args, **kwargs)
    
    return decorated_function


# ==================== 公开API ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'success': True,
        'message': 'API运行正常',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取网站配置（主标题、副标题）"""
    try:
        configs = db.get_all_config()
        return jsonify({
            'success': True,
            'data': {
                'main_title': configs.get('main_title', 'Hello World'),
                'sub_title': configs.get('sub_title', '🎉 欢迎来到我的网站 🎉')
            }
        })
    except Exception as e:
        logger.error(f"获取配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取配置失败'
        }), 500


@app.route('/api/log', methods=['POST'])
def add_log():
    """记录访问日志"""
    try:
        data = request.get_json() or {}
        ip_address = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        
        db.add_access_log(ip_address, user_agent)
        
        return jsonify({
            'success': True,
            'message': '日志记录成功'
        })
    except Exception as e:
        logger.error(f"记录日志失败: {str(e)}")
        # 日志记录失败不影响用户体验，返回成功
        return jsonify({'success': True})


# ==================== 管理后台API ====================

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        # 验证账号密码
        user = db.verify_admin(username, password)
        
        if user:
            # 设置session
            session['admin_id'] = user['id']
            session['admin_username'] = user['username']
            session.permanent = True
            
            logger.info(f"管理员登录成功: {username} from {get_client_ip()}")
            
            return jsonify({
                'success': True,
                'message': '登录成功',
                'data': {
                    'username': user['username']
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
            
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '登录失败，请稍后重试'
        }), 500


@app.route('/api/admin/logout', methods=['POST'])
@require_login
def admin_logout():
    """管理员退出登录"""
    username = session.get('admin_username', 'unknown')
    session.clear()
    
    logger.info(f"管理员退出登录: {username}")
    
    return jsonify({
        'success': True,
        'message': '退出登录成功'
    })


@app.route('/api/admin/check', methods=['GET'])
def check_login():
    """检查登录状态"""
    if 'admin_id' in session:
        return jsonify({
            'success': True,
            'data': {
                'logged_in': True,
                'username': session.get('admin_username')
            }
        })
    else:
        return jsonify({
            'success': True,
            'data': {
                'logged_in': False
            }
        })


@app.route('/api/admin/config', methods=['PUT'])
@require_login
def update_config():
    """更新网站配置"""
    try:
        data = request.get_json()
        main_title = data.get('main_title', '').strip()
        sub_title = data.get('sub_title', '').strip()
        
        if not main_title:
            return jsonify({
                'success': False,
                'message': '主标题不能为空'
            }), 400
        
        # 更新配置
        db.update_config('main_title', main_title)
        if sub_title:
            db.update_config('sub_title', sub_title)
        
        logger.info(f"配置更新成功 by {session.get('admin_username')}")
        
        return jsonify({
            'success': True,
            'message': '配置更新成功'
        })
        
    except Exception as e:
        logger.error(f"更新配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新配置失败'
        }), 500


@app.route('/api/admin/logs', methods=['GET'])
@require_login
def get_logs():
    """获取访问日志"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        if page < 1:
            page = 1
        if page_size > 100:
            page_size = 100
        
        offset = (page - 1) * page_size
        
        logs = db.get_access_logs(limit=page_size, offset=offset)
        total = db.get_logs_count()
        
        return jsonify({
            'success': True,
            'data': {
                'logs': logs,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        })
        
    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取日志失败'
        }), 500


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': '接口不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500


# ==================== 应用启动 ====================

if __name__ == '__main__':
    # 初始化数据库
    try:
        logger.info("正在初始化数据库...")
        db.init_database()
        db.insert_default_data()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        exit(1)
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )

from flask import Flask, render_template, request, jsonify, redirect
from models import db, Router
import subprocess
import platform


app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///routers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'change-this-in-production'

db.init_app(app)

# Создание БД при первом запуске
with app.app_context():
    db.create_all()


# 📄 Главная страница
@app.route('/')
def index():
    return render_template('index.html')


# 📋 API: Получить все роутеры
@app.route('/api/routers', methods=['GET'])
def get_routers():
    routers = Router.query.all()
    return jsonify([r.to_dict() for r in routers])


# ➕ API: Добавить роутер
@app.route('/api/routers', methods=['POST'])
def add_router():
    data = request.json
    try:
        router = Router(
            name=data['name'],
            ip_address=data['ip_address'],
            admin_login=data['admin_login'],
            admin_password=data['admin_password'],
            wifi_password=data['wifi_password'],
            location=data['location'],
            note=data.get('note', ''),
            web_port=data.get('web_port', 80),
            ssh_port=data.get('ssh_port', 22)
        )
        db.session.add(router)
        db.session.commit()
        return jsonify(router.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'e  rror': str(e)}), 400


# ✏️ API: Обновить роутер
@app.route('/api/routers/<int:id>', methods=['PUT'])
def update_router(id):
    router = Router.query.get_or_404(id)
    data = request.json
    try:
        router.name = data['name']
        router.ip_address = data['ip_address']
        router.admin_login = data['admin_login']
        router.admin_password = data['admin_password']
        router.wifi_password = data['wifi_password']
        router.location = data['location']
        router.note = data.get('note', router.note)
        router.web_port = data.get('web_port', router.web_port)
        router.ssh_port = data.get('ssh_port', router.ssh_port)
        db.session.commit()
        return jsonify(router.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# 🗑️ API: Удалить роутер
@app.route('/api/routers/<int:id>', methods=['DELETE'])
def delete_router(id):
    router = Router.query.get_or_404(id)
    try:
        db.session.delete(router)
        db.session.commit()
        return jsonify({'message': 'Deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# 🏓 API: Ping роутера (исправлено для Windows)
@app.route('/api/routers/<int:id>/ping', methods=['GET'])
def ping_router(id):
    router = Router.query.get_or_404(id)
    try:
        system = platform.system()
        if system == 'Windows':
            # Windows: -n = count, -w = timeout in MILLISECONDS
            cmd = ['ping', '-n', '1', '-w', '2000', router.ip_address]
        else:
            # Linux/Mac: -c = count, -W = timeout in SECONDS
            cmd = ['ping', '-c', '1', '-W', '2', router.ip_address]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )
        is_alive = result.returncode == 0
        return jsonify({
            'alive': is_alive,
            'output': result.stdout.strip() if is_alive else 'Host unreachable',
            'ip': router.ip_address
        })
    except subprocess.TimeoutExpired:
        return jsonify({'alive': False, 'output': 'Ping timeout', 'ip': router.ip_address})
    except Exception as e:
        return jsonify({'alive': False, 'output': f'Error: {str(e)}', 'ip': router.ip_address}), 500


# 🔗 Прямой редирект на Web-интерфейс
@app.route('/router/<int:id>/web')
def redirect_web(id):
    router = Router.query.get_or_404(id)
    protocol = 'https' if router.web_port in [443, 8443] else 'http'
    return redirect(f"{protocol}://{router.ip_address}:{router.web_port}")


# 🔐 API: SSH команда (исправлено)
@app.route('/api/routers/<int:id>/ssh', methods=['GET'])
def get_ssh_command(id):
    router = Router.query.get_or_404(id)
    cmd = f"ssh {router.admin_login}@{router.ip_address} -p {router.ssh_port or 22}"
    return jsonify({'command': cmd, 'note': 'Password will be prompted securely'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
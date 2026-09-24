from flask import Flask, send_from_directory
from flask_login import LoginManager
from config import Config
from models import db, User
from routes.auth import auth_bp, bcrypt
from routes.facilities import facilities_bp
from routes.reservations import reservations_bp
from routes.payments import payments_bp
import os


def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = None

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(facilities_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(payments_bp)

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    with app.app_context():
        db.create_all()
        _seed_data()

    return app


def _seed_data():
    from models import Facility, User
    from routes.auth import bcrypt

    if User.query.filter_by(username='admin').first() is None:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            display_name='自治体職員（管理者）',
            role='staff',
            language='ja'
        )
        db.session.add(admin_user)

    if User.query.filter_by(username='user').first() is None:
        citizen_user = User(
            username='user',
            email='user@example.com',
            password_hash=bcrypt.generate_password_hash('user123').decode('utf-8'),
            display_name='テスト市民',
            role='citizen',
            language='ja'
        )
        db.session.add(citizen_user)

    db.session.commit()

    if Facility.query.first() is not None:
        return

    facilities = [
        Facility(
            name='中央体育館', name_en='Central Gymnasium', name_zh='中央体育馆',
            type='gym', address='東京都千代田区中央1-2-3',
            address_en='1-2-3 Chuo, Chiyoda-ku, Tokyo',
            address_zh='东京都千代田区中央1-2-3',
            capacity=100, price_per_hour=1500,
            description='冷暖房完備の体育館。バスケットボールコート2面分の広さ。',
            description_en='Air-conditioned gymnasium with space for 2 basketball courts.',
            description_zh='配备冷暖空调的体育馆，拥有2个篮球场的空间。',
            image_url='/static/images/gym.jpg'
        ),
        Facility(
            name='南区会議室', name_en='Minami Ward Meeting Room', name_zh='南区会议室',
            type='meeting_room', address='東京都港区南5-10-15',
            address_en='5-10-15 Minami, Minato-ku, Tokyo',
            address_zh='东京都港区南5-10-15',
            capacity=30, price_per_hour=800,
            description='プロジェクター・ホワイトボード完備の会議室。',
            description_en='Meeting room equipped with projector and whiteboard.',
            description_zh='配备投影仪和白板的会议室。',
            image_url='/static/images/meeting.jpg'
        ),
        Facility(
            name='市民温水プール', name_en='Citizen Heated Pool', name_zh='市民温水游泳池',
            type='pool', address='東京都新宿区西新宿2-8-1',
            address_en='2-8-1 Nishi-Shinjuku, Shinjuku-ku, Tokyo',
            address_zh='东京都新宿区西新宿2-8-1',
            capacity=50, price_per_hour=1000,
            description='25m×6コースの温水プール。更衣室・シャワー完備。',
            description_en='25m x 6 lane heated pool with changing rooms and showers.',
            description_zh='25米×6泳道的温水游泳池，配备更衣室和淋浴。',
            image_url='/static/images/pool.jpg'
        ),
        Facility(
            name='北区多目的ホール', name_en='Kita Ward Multipurpose Hall', name_zh='北区多功能厅',
            type='meeting_room', address='東京都北区赤羽1-1-1',
            address_en='1-1-1 Akabane, Kita-ku, Tokyo',
            address_zh='东京都北区赤羽1-1-1',
            capacity=200, price_per_hour=3000,
            description='各種イベントに対応可能な多目的ホール。音響設備完備。',
            description_en='Multipurpose hall suitable for various events with sound equipment.',
            description_zh='可应对各种活动的多功能厅，配备音响设备。',
            image_url='/static/images/hall.jpg'
        ),
        Facility(
            name='西体育館', name_en='West Gymnasium', name_zh='西体育馆',
            type='gym', address='東京都練馬区西3-5-7',
            address_en='3-5-7 Nishi, Nerima-ku, Tokyo',
            address_zh='东京都练马区西3-5-7',
            capacity=80, price_per_hour=1200,
            description='バレーボールコート1面分の体育館。',
            description_en='Gymnasium with space for 1 volleyball court.',
            description_zh='拥有1个排球场的体育馆。',
            image_url='/static/images/gym2.jpg'
        ),
    ]

    db.session.add_all(facilities)
    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)

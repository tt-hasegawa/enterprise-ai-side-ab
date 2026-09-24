import os
import io
import json
from datetime import datetime, date, timedelta
from functools import wraps

from flask import (Flask, render_template, request, jsonify, session,
                   send_file)
from flask_bcrypt import Bcrypt
from models import db, User, Facility, Reservation

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facility.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)

import sys
try:
    from PIL import Image
except ImportError:
    import pil
    sys.modules['PIL'] = pil
    import PIL.Image as Image

TRANSLATIONS = {
    'ja': {
        'app_title': '自治体施設予約システム', 'home': 'ホーム',
        'facilities': '施設検索', 'my_reservations': '予約一覧',
        'profile': 'プロフィール', 'login': 'ログイン',
        'register': '登録', 'logout': 'ログアウト',
        'search': '検索', 'search_placeholder': '施設名、所在地で検索',
        'facility_type': '種別', 'all_types': 'すべて',
        'gym': '体育館', 'meeting_room': '会議室', 'pool': '温水プール',
        'price': '料金', 'capacity': '収容人数', 'location': '所在地',
        'date': '日付', 'start_time': '開始時間', 'end_time': '終了時間',
        'num_people': '人数', 'purpose': '利用目的',
        'purpose_placeholder': '利用目的を入力してください',
        'reserve': '予約する', 'cancel': 'キャンセル',
        'confirm_cancel': 'キャンセルしますか？',
        'payment': '決済', 'pay': '支払う', 'paid': '支払済',
        'unpaid': '未払い', 'download_pdf': '予約票をダウンロード',
        'status': '状態', 'confirmed': '予約確定', 'cancelled': 'キャンセル済',
        'username': 'ユーザー名', 'email': 'メールアドレス',
        'password': 'パスワード', 'name': '名前', 'language': '言語',
        'japanese': '日本語', 'english': 'English', 'chinese': '中文',
        'save': '保存',
        'welcome': '自治体施設予約システムへようこそ',
        'welcome_desc': '体育館、会議室、温水プールなど、自治体の施設を簡単に検索・予約できます。',
        'no_results': '該当する施設が見つかりませんでした。',
        'loading': '読み込み中...', 'error': 'エラーが発生しました',
        'register_title': '新規ユーザー登録', 'login_title': 'ログイン',
        'already_have_account': 'すでにアカウントをお持ちの方はこちら',
        'no_account': 'アカウントをお持ちでない方はこちら',
        'reservation_success': '予約が完了しました',
        'reservation_cancelled': '予約をキャンセルしました',
        'payment_success': '決済が完了しました',
        'your_reservations': '予約一覧', 'no_reservations': '予約がありません',
        'facility_detail': '施設詳細', 'back': '戻る',
        'total_price': '合計料金', 'yen': '円',
        'hour': '時間', 'hours': '時間',
        'qr_instruction': '以下のQRコードを施設で提示してください',
        'reservation_id': '予約番号', 'per_hour': '円/時間',
        'check_availability': '空き状況を確認',
        'available': '空きあり', 'unavailable': '予約済',
        'search_results': '検索結果', 'booking_date': '予約日',
        'booking_time': '予約時間', 'profile_title': 'プロフィール設定',
        'language_changed': '言語を変更しました',
        'payment_qr_title': '決済用QRコード',
        'download_ready': 'ダウンロード準備完了',
        'booking_details': '予約詳細', 'my_page': 'マイページ',
        'welcome_user': 'ようこそ', 'confirm': '確認',
        'cancel_reservation': '予約をキャンセルする',
        'total': '合計', 'actions': '操作',
        'detail': '詳細', 'pay_now': '今すぐ支払う',
        'select_time': '時間を選択', 'no_slots': '空き時間枠がありません',
    },
    'en': {
        'app_title': 'Municipal Facility Reservation System',
        'home': 'Home', 'facilities': 'Facility Search',
        'my_reservations': 'My Reservations', 'profile': 'Profile',
        'login': 'Login', 'register': 'Register', 'logout': 'Logout',
        'search': 'Search', 'search_placeholder': 'Search by facility name, location',
        'facility_type': 'Type', 'all_types': 'All',
        'gym': 'Gym', 'meeting_room': 'Meeting Room', 'pool': 'Heated Pool',
        'price': 'Price', 'capacity': 'Capacity', 'location': 'Location',
        'date': 'Date', 'start_time': 'Start Time', 'end_time': 'End Time',
        'num_people': 'Number of People', 'purpose': 'Purpose',
        'purpose_placeholder': 'Enter the purpose of use',
        'reserve': 'Reserve', 'cancel': 'Cancel',
        'confirm_cancel': 'Are you sure you want to cancel?',
        'payment': 'Payment', 'pay': 'Pay', 'paid': 'Paid',
        'unpaid': 'Unpaid', 'download_pdf': 'Download Reservation Slip',
        'status': 'Status', 'confirmed': 'Confirmed', 'cancelled': 'Cancelled',
        'username': 'Username', 'email': 'Email', 'password': 'Password',
        'name': 'Name', 'language': 'Language',
        'japanese': '日本語', 'english': 'English', 'chinese': '中文',
        'save': 'Save',
        'welcome': 'Welcome to Municipal Facility Reservation System',
        'welcome_desc': 'Easily search and reserve municipal facilities such as gyms, meeting rooms, and heated pools.',
        'no_results': 'No facilities found.',
        'loading': 'Loading...', 'error': 'An error occurred',
        'register_title': 'User Registration', 'login_title': 'Login',
        'already_have_account': 'Already have an account?',
        'no_account': "Don't have an account?",
        'reservation_success': 'Reservation completed successfully',
        'reservation_cancelled': 'Reservation cancelled',
        'payment_success': 'Payment completed successfully',
        'your_reservations': 'My Reservations',
        'no_reservations': 'No reservations',
        'facility_detail': 'Facility Details', 'back': 'Back',
        'total_price': 'Total Price', 'yen': 'yen',
        'hour': 'hour', 'hours': 'hours',
        'qr_instruction': 'Show this QR code at the facility',
        'reservation_id': 'Reservation ID', 'per_hour': 'yen/hour',
        'check_availability': 'Check Availability',
        'available': 'Available', 'unavailable': 'Booked',
        'search_results': 'Search Results', 'booking_date': 'Booking Date',
        'booking_time': 'Booking Time', 'profile_title': 'Profile Settings',
        'language_changed': 'Language changed',
        'payment_qr_title': 'Payment QR Code',
        'download_ready': 'Ready for download',
        'booking_details': 'Booking Details', 'my_page': 'My Page',
        'welcome_user': 'Welcome', 'confirm': 'Confirm',
        'cancel_reservation': 'Cancel Reservation',
        'total': 'Total', 'actions': 'Actions',
        'detail': 'Details', 'pay_now': 'Pay Now',
        'select_time': 'Select Time', 'no_slots': 'No available time slots',
    },
    'zh': {
        'app_title': '市政设施预约系统', 'home': '首页',
        'facilities': '设施搜索', 'my_reservations': '我的预约',
        'profile': '个人资料', 'login': '登录', 'register': '注册',
        'logout': '登出', 'search': '搜索',
        'search_placeholder': '按设施名称、地址搜索',
        'facility_type': '类型', 'all_types': '全部',
        'gym': '体育馆', 'meeting_room': '会议室', 'pool': '温水游泳池',
        'price': '费用', 'capacity': '容纳人数', 'location': '地址',
        'date': '日期', 'start_time': '开始时间', 'end_time': '结束时间',
        'num_people': '人数', 'purpose': '使用目的',
        'purpose_placeholder': '请输入使用目的',
        'reserve': '预约', 'cancel': '取消',
        'confirm_cancel': '确定要取消吗？',
        'payment': '支付', 'pay': '支付', 'paid': '已支付',
        'unpaid': '未支付', 'download_pdf': '下载预约单',
        'status': '状态', 'confirmed': '已确认', 'cancelled': '已取消',
        'username': '用户名', 'email': '电子邮箱', 'password': '密码',
        'name': '姓名', 'language': '语言',
        'japanese': '日本語', 'english': 'English', 'chinese': '中文',
        'save': '保存',
        'welcome': '欢迎使用市政设施预约系统',
        'welcome_desc': '轻松搜索和预约体育馆、会议室、温水游泳池等市政设施。',
        'no_results': '未找到符合条件的设施。',
        'loading': '加载中...', 'error': '发生错误',
        'register_title': '用户注册', 'login_title': '登录',
        'already_have_account': '已有账号？',
        'no_account': '没有账号？',
        'reservation_success': '预约成功',
        'reservation_cancelled': '预约已取消',
        'payment_success': '支付成功',
        'your_reservations': '我的预约', 'no_reservations': '暂无预约',
        'facility_detail': '设施详情', 'back': '返回',
        'total_price': '总费用', 'yen': '日元',
        'hour': '小时', 'hours': '小时',
        'qr_instruction': '请向设施工作人员出示此二维码',
        'reservation_id': '预约编号', 'per_hour': '日元/小时',
        'check_availability': '查看可用性',
        'available': '可预约', 'unavailable': '已预约',
        'search_results': '搜索结果', 'booking_date': '预约日期',
        'booking_time': '预约时间', 'profile_title': '个人资料设置',
        'language_changed': '语言已更改',
        'payment_qr_title': '支付二维码',
        'download_ready': '准备下载',
        'booking_details': '预约详情', 'my_page': '个人中心',
        'welcome_user': '欢迎', 'confirm': '确认',
        'cancel_reservation': '取消预约',
        'total': '合计', 'actions': '操作',
        'detail': '详情', 'pay_now': '立即支付',
        'select_time': '选择时间', 'no_slots': '没有可用的时间',
    },
}


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated


def get_user_lang():
    uid = session.get('user_id')
    if uid is None:
        best = request.accept_languages.best_match(['ja', 'en', 'zh'])
        return best or 'ja'
    user = User.query.get(uid)
    if user:
        return user.lang
    best = request.accept_languages.best_match(['ja', 'en', 'zh'])
    return best or 'ja'


def seed_data():
    if Facility.query.first():
        return
    facilities = [
        Facility(
            name_ja='中央体育館', name_en='Central Gym', name_zh='中央体育馆',
            type='gym',
            location_ja='東京都千代田区1-1-1', location_en='1-1-1 Chiyoda, Tokyo',
            location_zh='东京都千代田区1-1-1',
            price=500, capacity=50,
            description_ja='都心に位置する多目的体育館。バスケットボール、バレーボールなどに対応。',
            description_en='Multipurpose gym in central Tokyo. Suitable for basketball, volleyball, etc.',
            description_zh='位于市中心的综合体育馆。可用于篮球、排球等运动。',
        ),
        Facility(
            name_ja='北コミュニティ会議室', name_en='North Community Meeting Room',
            name_zh='北社区会议室',
            type='meeting_room',
            location_ja='東京都北区2-2-2', location_en='2-2-2 Kita, Tokyo',
            location_zh='东京都北区2-2-2',
            price=300, capacity=20,
            description_ja='地域コミュニティの会議やイベントに最適な会議室。',
            description_en='Meeting room ideal for community meetings and events.',
            description_zh='最适合地区社区会议和活动的会议室。',
        ),
        Facility(
            name_ja='市民温水プール', name_en='City Heated Pool', name_zh='市民温水游泳池',
            type='pool',
            location_ja='東京都新宿区3-3-3', location_en='3-3-3 Shinjuku, Tokyo',
            location_zh='东京都新宿区3-3-3',
            price=800, capacity=30,
            description_ja='年中利用可能な温水プール。遊泳レーンと幼児用プールあり。',
            description_en="Year-round heated pool with swimming lanes and children's pool.",
            description_zh='全年可用的温水游泳池。设有游泳道和幼儿泳池。',
        ),
        Facility(
            name_ja='東体育館', name_en='East Gym', name_zh='东体育馆',
            type='gym',
            location_ja='東京都江東区4-4-4', location_en='4-4-4 Koto, Tokyo',
            location_zh='东京都江东区4-4-4',
            price=400, capacity=40,
            description_ja='東東京エリアの地域体育館。卓球、バドミントンに最適。',
            description_en='Regional gym in east Tokyo. Great for table tennis and badminton.',
            description_zh='东京东部地区的体育馆。最适合乒乓球和羽毛球。',
        ),
        Facility(
            name_ja='南多目的ホール', name_en='South Multipurpose Hall',
            name_zh='南多功能厅',
            type='meeting_room',
            location_ja='東京都品川区5-5-5', location_en='5-5-5 Shinagawa, Tokyo',
            location_zh='东京都品川区5-5-5',
            price=600, capacity=100,
            description_ja='各種イベントや講演会に対応可能な多目的ホール。',
            description_en='Multipurpose hall suitable for various events and lectures.',
            description_zh='可举办各类活动和演讲的多功能厅。',
        ),
    ]
    db.session.add_all(facilities)
    db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    pw_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
        username=data['username'], email=data['email'],
        password_hash=pw_hash, name=data.get('name', data['username']),
        lang=data.get('lang', 'ja'),
    )
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    return jsonify({'message': 'Registered successfully', 'user': {
        'id': user.id, 'username': user.username, 'email': user.email,
        'name': user.name, 'lang': user.lang,
    }}), 201


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, data.get('password', '')):
        return jsonify({'error': 'Invalid credentials'}), 401
    session['user_id'] = user.id
    return jsonify({'message': 'Logged in', 'user': {
        'id': user.id, 'username': user.username, 'email': user.email,
        'name': user.name, 'lang': user.lang,
    }})


@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out'})


@app.route('/api/user', methods=['GET', 'PUT'])
@login_required
def api_user():
    user = User.query.get(session['user_id'])
    if request.method == 'PUT':
        data = request.json
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            if data['email'] != user.email and User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already exists'}), 409
            user.email = data['email']
        if 'lang' in data:
            user.lang = data['lang']
        if 'password' in data and data['password']:
            user.password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        db.session.commit()
    return jsonify({'user': {
        'id': user.id, 'username': user.username, 'email': user.email,
        'name': user.name, 'lang': user.lang,
    }})


@app.route('/api/facilities', methods=['GET'])
def api_facilities():
    lang = get_user_lang()
    query = request.args.get('q', '').strip()
    type_filter = request.args.get('type', '')
    price_max = request.args.get('price_max', type=int)

    q = Facility.query
    if type_filter:
        q = q.filter_by(type=type_filter)
    if price_max:
        q = q.filter(Facility.price <= price_max)
    if query:
        like = f'%{query}%'
        if lang == 'ja':
            q = q.filter(db.or_(Facility.name_ja.like(like), Facility.location_ja.like(like)))
        elif lang == 'en':
            q = q.filter(db.or_(Facility.name_en.like(like), Facility.location_en.like(like)))
        elif lang == 'zh':
            q = q.filter(db.or_(Facility.name_zh.like(like), Facility.location_zh.like(like)))
        else:
            q = q.filter(db.or_(Facility.name_ja.like(like), Facility.location_ja.like(like)))

    facilities = q.all()
    return jsonify({'facilities': [f.to_dict(lang) for f in facilities]})


@app.route('/api/facilities/<int:facility_id>', methods=['GET'])
def api_facility(facility_id):
    lang = get_user_lang()
    facility = Facility.query.get_or_404(facility_id)
    return jsonify({'facility': facility.to_dict(lang)})


@app.route('/api/facilities/<int:facility_id>/availability', methods=['GET'])
def api_availability(facility_id):
    Facility.query.get_or_404(facility_id)
    date_str = request.args.get('date', date.today().isoformat())
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    if target_date < date.today():
        return jsonify({'error': 'Cannot check past dates'}), 400

    time_slots = []
    for hour in range(9, 18):
        start = f'{hour:02d}:00'
        end = f'{hour+1:02d}:00'
        existing = Reservation.query.filter(
            Reservation.facility_id == facility_id,
            Reservation.date == target_date,
            Reservation.start_time == start,
            Reservation.status == 'confirmed',
        ).first()
        time_slots.append({
            'start': start, 'end': end, 'available': existing is None,
        })

    return jsonify({'date': target_date.isoformat(), 'time_slots': time_slots})


@app.route('/api/reservations', methods=['GET', 'POST'])
@login_required
def api_reservations():
    lang = get_user_lang()
    if request.method == 'POST':
        data = request.json
        try:
            reserv_date = date.fromisoformat(data['date'])
        except (ValueError, KeyError):
            return jsonify({'error': 'Invalid date'}), 400
        if reserv_date < date.today():
            return jsonify({'error': 'Cannot reserve past dates'}), 400

        conflict = Reservation.query.filter(
            Reservation.facility_id == data['facility_id'],
            Reservation.date == reserv_date,
            Reservation.start_time == data['start_time'],
            Reservation.status == 'confirmed',
        ).first()
        if conflict:
            return jsonify({'error': 'Time slot already booked'}), 409

        purpose = data.get('purpose', '')
        reservation = Reservation(
            user_id=session['user_id'],
            facility_id=data['facility_id'],
            date=reserv_date, start_time=data['start_time'],
            end_time=data['end_time'],
            num_people=data.get('num_people', 1),
            purpose=purpose, status='confirmed',
        )
        db.session.add(reservation)
        db.session.commit()
        return jsonify({'reservation': reservation.to_dict(lang)}), 201

    user_reservations = Reservation.query.filter_by(
        user_id=session['user_id']
    ).order_by(Reservation.date.desc()).all()
    return jsonify({'reservations': [r.to_dict(lang) for r in user_reservations]})


@app.route('/api/reservations/<int:reservation_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_reservation(reservation_id):
    lang = get_user_lang()
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403

    if request.method == 'GET':
        return jsonify({'reservation': reservation.to_dict(lang)})

    if request.method == 'PUT':
        data = request.json
        for key in ('num_people', 'purpose'):
            if key in data:
                setattr(reservation, key, data[key])
        if 'status' in data:
            reservation.status = data['status']
        db.session.commit()
        return jsonify({'reservation': reservation.to_dict(lang)})

    if request.method == 'DELETE':
        reservation.status = 'cancelled'
        db.session.commit()
        return jsonify({'message': 'Reservation cancelled', 'reservation': reservation.to_dict(lang)})


@app.route('/api/reservations/<int:reservation_id>/payment', methods=['GET', 'POST'])
@login_required
def api_payment(reservation_id):
    lang = get_user_lang()
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403
    if request.method == 'POST':
        reservation.payment_status = 'paid'
        db.session.commit()
        return jsonify({'message': 'Payment successful', 'reservation': reservation.to_dict(lang)})
    return jsonify({'reservation': reservation.to_dict(lang)})


@app.route('/api/reservations/<int:reservation_id>/payment/qr', methods=['GET'])
@login_required
def api_payment_qr(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403
    import qrcode
    payment_data = json.dumps({
        'reservation_id': reservation.id,
        'amount': reservation.facility.price,
        'facility': reservation.facility.name_en,
        'date': reservation.date.isoformat(),
    }, ensure_ascii=False)
    qr = qrcode.make(payment_data)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')


@app.route('/api/reservations/<int:reservation_id>/pdf', methods=['GET'])
@login_required
def api_reservation_pdf(reservation_id):
    lang = get_user_lang()
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403

    from fpdf import FPDF
    import qrcode

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Use Unicode font for CJK support
    font_path = None
    for candidate in [
        'C:/Windows/Fonts/msgothic.ttc',
        'C:/Windows/Fonts/yugothic.ttf',
        'C:/Windows/Fonts/meiryo.ttc',
    ]:
        if os.path.exists(candidate):
            font_path = candidate
            break
    if font_path:
        pdf.add_font('CJK', '', font_path, uni=True)
        pdf.add_font('CJK', 'B', font_path, uni=True)
        font_family = 'CJK'
    else:
        font_family = 'Helvetica'

    title_map = {'ja': '予約票', 'en': 'Reservation Slip', 'zh': '预约单'}
    pdf.set_font(font_family, 'B', 20)
    pdf.cell(0, 15, title_map.get(lang, 'Reservation Slip'), new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.ln(5)

    labels_map = {
        'ja': ['予約番号', '施設名', '日付', '時間', '人数', '利用目的', '料金', '状態'],
        'en': ['ID', 'Facility', 'Date', 'Time', 'People', 'Purpose', 'Amount', 'Status'],
        'zh': ['预约编号', '设施名称', '日期', '时间', '人数', '使用目的', '费用', '状态'],
    }
    lbl = labels_map.get(lang, labels_map['en'])

    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(0.5)
    y_start = pdf.get_y()
    pdf.rect(10, y_start, 190, 80)
    pdf.set_y(y_start + 5)

    left_x = 15
    row_h = 9
    y = y_start + 7
    pairs = [
        (lbl[0], str(reservation.id)),
        (lbl[1], getattr(reservation.facility, f'name_{lang}')),
        (lbl[2], reservation.date.isoformat()),
        (lbl[3], f'{reservation.start_time} - {reservation.end_time}'),
        (lbl[4], str(reservation.num_people)),
        (lbl[5], reservation.purpose or '-'),
        (lbl[6], f'{reservation.facility.price:,} JPY'),
        (lbl[7], reservation.status),
    ]
    for label, value in pairs:
        pdf.set_xy(left_x, y)
        pdf.set_font(font_family, 'B', 10)
        pdf.cell(40, row_h, f'{label}:')
        pdf.set_font(font_family, '', 10)
        pdf.cell(0, row_h, str(value))
        y += row_h

    qr_data = json.dumps({'reservation_id': reservation.id, 'amount': reservation.facility.price})
    qr_img = qrcode.make(qr_data)
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format='PNG')
    qr_buf.seek(0)
    qr_path = 'qr_temp.png'
    with open(qr_path, 'wb') as f:
        f.write(qr_buf.getvalue())
    pdf.image(qr_path, x=150, y=pdf.get_y() - 75, w=35)

    pdf.set_y(y + 20)
    pdf.set_font(font_family, '', 8)
    pdf.cell(0, 10, 'Municipal Facility Reservation System', align='C')

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return send_file(buf, mimetype='application/pdf',
                     as_attachment=True,
                     download_name=f'reservation_{reservation.id}.pdf')


@app.route('/api/translations/<lang_code>', methods=['GET'])
def api_translations(lang_code):
    return jsonify(TRANSLATIONS.get(lang_code, TRANSLATIONS['ja']))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)

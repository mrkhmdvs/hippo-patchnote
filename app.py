from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from pathlib import Path
import sqlite3, os, secrets, datetime

BASE = Path(__file__).resolve().parent
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
DB = BASE / 'hippo_journal.db'

PRODUCTS = [
    ('hippo-kassa','HIPPO Kassa'), ('hippo-edi','Hippo EDI'), ('hippo-edo','Hippo EDO'),
    ('hippo-erp','Hippo ERP'), ('hippo-dms','Hippo DMS'), ('hippo-xat','Hippo Xat')
]
I18N = {
'en': {'brand_sub':'PRODUCT JOURNAL','nav_updates':'Updates','nav_products':'Products','nav_guide':'Guide','nav_admin':'Admin studio','nav_login':'Admin login','nav_logout':'Sign out','hero_eyebrow':'THE HIPPO PRODUCT ECOSYSTEM','hero_title':'Every improvement.\nOne clear place.','hero_desc':'Product updates, improvements and fixes from across Hippo — collected in one reliable journal.','search':'Search updates','all_products':'All products','all_types':'All update types','feature':'Featured','latest':'Latest updates','empty_title':'No published updates yet','empty_desc':'New product updates will appear here as soon as they are published.','read_update':'Read update','back':'Back to updates','login_title':'Welcome back','login_desc':'Sign in to the private publishing studio.','username':'Username','password':'Password','sign_in':'Sign in','setup_title':'Set up your private studio','setup_desc':'Create the only administrator account. Public sign-up is disabled after setup.','confirm_password':'Confirm password','create_admin':'Create administrator','studio_title':'Release Studio','studio_desc':'Your private workspace for product announcements.','new_release':'Create release','total':'Total releases','published':'Published','drafts':'Drafts','products':'Products','all_releases':'All releases','status':'Status','date':'Release date','product':'Product','title':'Title','type':'Update type','summary':'Short summary','content':'Release details','version':'Version','save_draft':'Save draft','publish':'Publish update','unpublish':'Move to draft','archive':'Archive','edit':'Edit','delete':'Delete','cancel':'Cancel','guide_title':'Publishing guide','guide_desc':'A clear workflow for consistent, useful release notes.','step1':'Choose the product and version','step1d':'Select the Hippo product, release date and update category.','step2':'Write for the customer','step2d':'Explain what changed, who benefits and where to find it. Keep internal details out.','step3':'Preview and publish','step3d':'Check spelling, links and product selection before publishing. Published updates appear on the public journal.','help':'Need help?','no_access':'This page is available to the administrator only.','not_found':'Page not found','server_error':'Something went wrong','logout_done':'You have signed out.','saved':'Release saved.','published_msg':'Release published.','draft_msg':'Release moved to drafts.','archived_msg':'Release archived.','login_failed':'Incorrect username or password.','setup_done':'Administrator created. Sign in to continue.','required':'Please fill in all required fields.','bad_confirm':'Passwords do not match.','weak_password':'Use at least 12 characters for the password.','slug':'Permanent link','no_results':'No updates match your search.','status_published':'Published','status_draft':'Draft','status_archived':'Archived','type_feature':'New feature','type_improvement':'Improvement','type_fix':'Bug fix','type_security':'Security','type_announcement':'Announcement','read_more':'Explore update','footer':'A clear view of what is changing across Hippo.','studio_subtitle':'Manage every product update in one place.','table_subtitle':'Create, edit, publish or permanently remove releases.','records':'RECORDS','all_releases_sub':'All release notes','live_label':'Visible in public journal','draft_label':'Private until published','connected_products':'Products in the ecosystem','empty_admin':'No releases yet','empty_admin_desc':'Create the first product update to get started.','editor_intro':'Write a useful update and review it before publishing.','release_info':'Release information','release_info_desc':'Choose where this update belongs.','story':'Tell the story','story_desc':'Clear, concise and helpful for the customer.','story_placeholder':'A clear description of what changed','summary_help':'Shown on the public updates page. Keep it under 300 characters.','content_help':'Plain text is supported. Separate paragraphs with a blank line.','checklist':'PUBLISHING CHECKLIST','product_selected':'Product selected','product_selected_desc':'Make sure the correct Hippo product is chosen.','customer_benefit':'Customer benefit','customer_benefit_desc':'Explain the impact, not just the implementation.','no_internal':'No internal information','no_internal_desc':'Keep internal links, credentials and private details out.','proofread':'Final proofread','proofread_desc':'Check wording, date and version before publishing.','visibility':'VISIBILITY','draft_visibility':'Visible only in your admin studio.','published_visibility':'Visible on the public journal.','search_button':'Search','admin_only':'ADMIN ONLY','delete_confirm':'Delete this release permanently? This cannot be undone.','deleted_msg':'Release deleted permanently.','delete_release':'Delete release','public_title':'Hippo Product Updates','public_subtitle':'Product news, improvements and fixes — in one place.'},
'ru': {'brand_sub':'ЖУРНАЛ ОБНОВЛЕНИЙ','nav_updates':'Обновления','nav_products':'Продукты','nav_guide':'Инструкция','nav_admin':'Админ-панель','nav_login':'Вход администратора','nav_logout':'Выйти','hero_eyebrow':'ЭКОСИСТЕМА ПРОДУКТОВ HIPPO','hero_title':'Каждое улучшение.\nВ одном месте.','hero_desc':'Обновления, улучшения и исправления продуктов Hippo — в одном понятном журнале.','search':'Поиск обновлений','all_products':'Все продукты','all_types':'Все типы обновлений','feature':'Важное','latest':'Последние обновления','empty_title':'Пока нет опубликованных обновлений','empty_desc':'Новые обновления появятся здесь сразу после публикации.','read_update':'Читать обновление','back':'К обновлениям','login_title':'С возвращением','login_desc':'Войдите в закрытую студию публикаций.','username':'Логин','password':'Пароль','sign_in':'Войти','setup_title':'Настройка закрытой студии','setup_desc':'Создайте единственную учётную запись администратора. После настройки регистрация будет закрыта.','confirm_password':'Повторите пароль','create_admin':'Создать администратора','studio_title':'Release Studio','studio_desc':'Ваше закрытое рабочее пространство для публикации обновлений.','new_release':'Создать релиз','total':'Всего релизов','published':'Опубликовано','drafts':'Черновики','products':'Продукты','all_releases':'Все релизы','status':'Статус','date':'Дата релиза','product':'Продукт','title':'Заголовок','type':'Тип обновления','summary':'Краткое описание','content':'Подробности релиза','version':'Версия','save_draft':'Сохранить черновик','publish':'Опубликовать','unpublish':'Вернуть в черновики','archive':'В архив','edit':'Редактировать','delete':'Удалить','cancel':'Отмена','guide_title':'Инструкция по публикации','guide_desc':'Понятный процесс для качественных и единообразных релиз-ноутов.','step1':'Выберите продукт и версию','step1d':'Укажите продукт Hippo, дату релиза и категорию обновления.','step2':'Пишите для клиента','step2d':'Объясните, что изменилось, кому это поможет и где найти функцию. Не включайте внутренние данные.','step3':'Проверьте и опубликуйте','step3d':'Проверьте текст, ссылки и продукт. После публикации обновление появится в публичном журнале.','help':'Нужна помощь?','no_access':'Эта страница доступна только администратору.','not_found':'Страница не найдена','server_error':'Что-то пошло не так','logout_done':'Вы вышли из системы.','saved':'Релиз сохранён.','published_msg':'Релиз опубликован.','draft_msg':'Релиз возвращён в черновики.','archived_msg':'Релиз перемещён в архив.','login_failed':'Неверный логин или пароль.','setup_done':'Администратор создан. Теперь войдите в систему.','required':'Заполните все обязательные поля.','bad_confirm':'Пароли не совпадают.','weak_password':'Пароль должен содержать не менее 12 символов.','slug':'Постоянная ссылка','no_results':'По вашему запросу ничего не найдено.','status_published':'Опубликовано','status_draft':'Черновик','status_archived':'В архиве','type_feature':'Новая функция','type_improvement':'Улучшение','type_fix':'Исправление ошибки','type_security':'Безопасность','type_announcement':'Объявление','read_more':'Подробнее','footer':'Всё важное об изменениях в экосистеме Hippo.','studio_subtitle':'Управляйте всеми обновлениями продуктов в одном месте.','table_subtitle':'Создавайте, редактируйте, публикуйте и удаляйте релизы.','records':'ЗАПИСЕЙ','all_releases_sub':'Все релиз-ноуты','live_label':'Видно в публичном журнале','draft_label':'Скрыто до публикации','connected_products':'Продукты экосистемы','empty_admin':'Релизов пока нет','empty_admin_desc':'Создайте первое обновление продукта.','editor_intro':'Оформите обновление и проверьте его перед публикацией.','release_info':'Информация о релизе','release_info_desc':'Выберите продукт и параметры обновления.','story':'Описание изменений','story_desc':'Понятно, кратко и полезно для клиента.','summary_help':'Отображается на публичной странице. До 300 символов.','content_help':'Поддерживается обычный текст. Разделяйте абзацы пустой строкой.','checklist':'ПРОВЕРКА ПУБЛИКАЦИИ','product_selected':'Продукт выбран','product_selected_desc':'Убедитесь, что выбран нужный продукт Hippo.','customer_benefit':'Польза для клиента','customer_benefit_desc':'Опишите результат, а не только реализацию.','no_internal':'Без внутренних данных','no_internal_desc':'Не добавляйте внутренние ссылки, пароли и закрытые данные.','proofread':'Финальная проверка','proofread_desc':'Проверьте текст, дату и версию.','visibility':'ВИДИМОСТЬ','draft_visibility':'Видно только в админ-панели.','published_visibility':'Видно в публичном журнале.','search_button':'Найти','admin_only':'ТОЛЬКО АДМИНИСТРАТОР','delete_confirm':'Удалить этот релиз навсегда? Это действие нельзя отменить.','deleted_msg':'Релиз удалён безвозвратно.','delete_release':'Удалить релиз','public_title':'Обновления продуктов Hippo','public_subtitle':'Новости, улучшения и исправления продуктов — в одном месте.'},
'uz': {'brand_sub':'YANGILANISHLAR JURNALI','nav_updates':'Yangilanishlar','nav_products':'Mahsulotlar','nav_guide':'Qo‘llanma','nav_admin':'Admin paneli','nav_login':'Admin kirishi','nav_logout':'Chiqish','hero_eyebrow':'HIPPO MAHSULOTLARI EKOTIZIMI','hero_title':'Har bir yangilik.\nBitta joyda.','hero_desc':'Hippo mahsulotlaridagi yangilanishlar, yaxshilanishlar va tuzatishlar — yagona tushunarli jurnalda.','search':'Yangilanishlarni qidirish','all_products':'Barcha mahsulotlar','all_types':'Barcha yangilanish turlari','feature':'Muhim','latest':'So‘nggi yangilanishlar','empty_title':'Hozircha e’lon qilingan yangilanishlar yo‘q','empty_desc':'Yangi yangilanishlar e’lon qilingach shu yerda ko‘rinadi.','read_update':'Yangilanishni o‘qish','back':'Yangilanishlarga qaytish','login_title':'Xush kelibsiz','login_desc':'Yopiq nashr studiyasiga kiring.','username':'Login','password':'Parol','sign_in':'Kirish','setup_title':'Yopiq studiyani sozlash','setup_desc':'Yagona administrator hisobini yarating. Sozlashdan keyin ro‘yxatdan o‘tish yopiladi.','confirm_password':'Parolni qayta kiriting','create_admin':'Administrator yaratish','studio_title':'Release Studio','studio_desc':'Mahsulot yangiliklarini nashr qilish uchun shaxsiy ish maydoningiz.','new_release':'Reliz yaratish','total':'Jami relizlar','published':'E’lon qilingan','drafts':'Qoralamalar','products':'Mahsulotlar','all_releases':'Barcha relizlar','status':'Holat','date':'Reliz sanasi','product':'Mahsulot','title':'Sarlavha','type':'Yangilanish turi','summary':'Qisqa izoh','content':'Reliz tafsilotlari','version':'Versiya','save_draft':'Qoralama saqlash','publish':'E’lon qilish','unpublish':'Qoralamaga qaytarish','archive':'Arxivlash','edit':'Tahrirlash','delete':'O‘chirish','cancel':'Bekor qilish','guide_title':'Nashr qilish qo‘llanmasi','guide_desc':'Aniq va foydali reliz yozuvlari uchun sodda jarayon.','step1':'Mahsulot va versiyani tanlang','step1d':'Hippo mahsuloti, reliz sanasi va yangilanish toifasini tanlang.','step2':'Mijoz uchun yozing','step2d':'Nima o‘zgargani, kimga foyda berishi va funksiyani qayerdan topishni tushuntiring. Ichki ma’lumotlarni kiritmang.','step3':'Tekshiring va e’lon qiling','step3d':'Matn, havolalar va mahsulotni tekshiring. E’lon qilingach yangilanish ochiq jurnalda ko‘rinadi.','help':'Yordam kerakmi?','no_access':'Bu sahifa faqat administrator uchun.','not_found':'Sahifa topilmadi','server_error':'Xatolik yuz berdi','logout_done':'Tizimdan chiqdingiz.','saved':'Reliz saqlandi.','published_msg':'Reliz e’lon qilindi.','draft_msg':'Reliz qoralamaga qaytarildi.','archived_msg':'Reliz arxivlandi.','login_failed':'Login yoki parol noto‘g‘ri.','setup_done':'Administrator yaratildi. Endi tizimga kiring.','required':'Barcha majburiy maydonlarni to‘ldiring.','bad_confirm':'Parollar mos kelmaydi.','weak_password':'Parol kamida 12 ta belgidan iborat bo‘lsin.','slug':'Doimiy havola','no_results':'Qidiruvingiz bo‘yicha yangilanish topilmadi.','status_published':'E’lon qilingan','status_draft':'Qoralama','status_archived':'Arxivda','type_feature':'Yangi funksiya','type_improvement':'Yaxshilanish','type_fix':'Xatolik tuzatildi','type_security':'Xavfsizlik','type_announcement':'E’lon','read_more':'Batafsil','footer':'Hippo ekotizimidagi o‘zgarishlar haqida yagona manba.','studio_subtitle':'Barcha mahsulot yangilanishlarini bir joyda boshqaring.','table_subtitle':'Relizlarni yarating, tahrirlang, e’lon qiling yoki butunlay o‘chiring.','records':'TA YOZUV','all_releases_sub':'Barcha reliz yozuvlari','live_label':'Ochiq jurnalda ko‘rinadi','draft_label':'E’lon qilinmaguncha yopiq','connected_products':'Ekotizim mahsulotlari','empty_admin':'Hozircha relizlar yo‘q','empty_admin_desc':'Birinchi mahsulot yangilanishini yarating.','editor_intro':'Yangilanishni yozing va e’lon qilishdan oldin tekshiring.','release_info':'Reliz ma’lumotlari','release_info_desc':'Mahsulot va yangilanish parametrlarini tanlang.','story':'O‘zgarishlar tavsifi','story_desc':'Mijoz uchun aniq, qisqa va foydali yozing.','summary_help':'Ochiq sahifada ko‘rinadi. 300 belgidan oshmasin.','content_help':'Oddiy matn qo‘llanadi. Abzatslarni bo‘sh qator bilan ajrating.','checklist':'NASHR OLDIDAN TEKSHIRUV','product_selected':'Mahsulot tanlandi','product_selected_desc':'To‘g‘ri Hippo mahsuloti tanlanganini tekshiring.','customer_benefit':'Mijoz uchun foyda','customer_benefit_desc':'Faqat amalga oshirishni emas, natijani tushuntiring.','no_internal':'Ichki ma’lumotlar yo‘q','no_internal_desc':'Ichki havolalar, parollar va maxfiy ma’lumotlarni kiritmang.','proofread':'Yakuniy tekshiruv','proofread_desc':'Matn, sana va versiyani tekshiring.','visibility':'KO‘RINISH HOLATI','draft_visibility':'Faqat admin panelida ko‘rinadi.','published_visibility':'Ochiq jurnalda ko‘rinadi.','search_button':'Qidirish','admin_only':'FAQAT ADMIN','delete_confirm':'Bu reliz butunlay o‘chirilsinmi? Buni ortga qaytarib bo‘lmaydi.','deleted_msg':'Reliz butunlay o‘chirildi.','delete_release':'Relizni o‘chirish','public_title':'Hippo mahsulot yangiliklari','public_subtitle':'Mahsulot yangiliklari, yaxshilanishlar va tuzatishlar — bir joyda.'}
}

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute('CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY CHECK(id=1), username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL)')
        con.execute('''CREATE TABLE IF NOT EXISTS releases (id INTEGER PRIMARY KEY AUTOINCREMENT, product TEXT NOT NULL, version TEXT DEFAULT '', category TEXT NOT NULL, title TEXT NOT NULL, summary TEXT NOT NULL, content TEXT NOT NULL, release_date TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'draft', created_at TEXT NOT NULL, updated_at TEXT NOT NULL)''')
        con.execute('CREATE INDEX IF NOT EXISTS idx_releases_status_date ON releases(status, release_date DESC)')
init_db()

def tr(key):
    lang = session.get('lang', 'ru')
    return I18N.get(lang, I18N['ru']).get(key, I18N['en'].get(key, key))
app.jinja_env.globals['tr'] = tr
app.jinja_env.globals['products'] = PRODUCTS
app.jinja_env.globals['type_keys'] = ['feature','improvement','fix','security','announcement']
app.jinja_env.globals['status_keys'] = ['published','draft','archived']
app.jinja_env.globals['lang_name'] = {'en':'EN','ru':'RU','uz':'UZ'}
app.jinja_env.globals['now_year'] = datetime.date.today().year
app.jinja_env.globals['today'] = datetime.date.today().isoformat()

@app.before_request
def language():
    chosen = request.args.get('lang')
    if chosen in I18N:
        session['lang'] = chosen

def admin_exists():
    with db() as con:
        return con.execute('SELECT 1 FROM admin WHERE id=1').fetchone() is not None

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get('admin_id'):
            return redirect(url_for('login', next=request.path))
        return fn(*args, **kwargs)
    return wrapped

def csrf_token():
    if '_csrf' not in session:
        session['_csrf'] = secrets.token_urlsafe(32)
    return session['_csrf']
app.jinja_env.globals['csrf_token'] = csrf_token

@app.before_request
def protect_post():
    if request.method == 'POST':
        token = request.form.get('_csrf', '')
        if not token or not secrets.compare_digest(token, session.get('_csrf', '')):
            abort(400, 'Invalid security token. Refresh the page and try again.')

@app.route('/language/<lang>')
def set_language(lang):
    if lang not in I18N: abort(404)
    session['lang'] = lang
    return redirect(request.referrer or url_for('home'))

@app.route('/')
def home():
    q = request.args.get('q','').strip()
    product = request.args.get('product','')
    category = request.args.get('category','')
    sql = "SELECT * FROM releases WHERE status='published'"
    args = []
    if q:
        sql += ' AND (title LIKE ? OR summary LIKE ? OR content LIKE ?)'
        args += [f'%{q}%']*3
    if product:
        sql += ' AND product=?'; args.append(product)
    if category:
        sql += ' AND category=?'; args.append(category)
    sql += ' ORDER BY release_date DESC, id DESC'
    with db() as con: rows = con.execute(sql,args).fetchall()
    return render_template('home.html', releases=rows, q=q, selected_product=product, selected_category=category)

@app.route('/release/<int:release_id>')
def release_detail(release_id):
    with db() as con: row = con.execute('SELECT * FROM releases WHERE id=? AND status=\'published\'', (release_id,)).fetchone()
    if not row: abort(404)
    return render_template('detail.html', release=row)

@app.route('/setup', methods=['GET','POST'])
def setup():
    if admin_exists(): return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        confirm = request.form.get('confirm_password','')
        if not username or not password: flash(tr('required'),'error')
        elif len(password) < 12: flash(tr('weak_password'),'error')
        elif password != confirm: flash(tr('bad_confirm'),'error')
        else:
            with db() as con:
                con.execute('INSERT INTO admin(id, username, password_hash, created_at) VALUES(1,?,?,?)', (username, generate_password_hash(password), datetime.datetime.now().isoformat(timespec='seconds')))
            flash(tr('setup_done'),'success')
            return redirect(url_for('login'))
    return render_template('setup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if not admin_exists(): return redirect(url_for('setup'))
    if session.get('admin_id'): return redirect(url_for('studio'))
    if request.method == 'POST':
        attempts = session.get('login_attempts', 0)
        last = session.get('login_attempt_time', 0)
        import time
        if attempts >= 8 and time.time()-last < 300:
            flash('Too many attempts. Wait five minutes and try again.','error')
        else:
            username = request.form.get('username','').strip()
            password = request.form.get('password','')
            with db() as con: user = con.execute('SELECT * FROM admin WHERE id=1 AND username=?',(username,)).fetchone()
            if user and check_password_hash(user['password_hash'], password):
                session.clear(); session['admin_id'] = 1; session['admin_name'] = user['username']; session['lang'] = session.get('lang','ru')
                return redirect(url_for('studio'))
            session['login_attempts'] = attempts + 1; session['login_attempt_time'] = time.time()
            flash(tr('login_failed'),'error')
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear(); flash(tr('logout_done'),'success'); return redirect(url_for('home'))

@app.route('/admin')
def admin_entry():
    return redirect(url_for('studio') if session.get('admin_id') else url_for('login'))

@app.route('/studio')
@login_required
def studio():
    with db() as con:
        all_rows = con.execute('SELECT * FROM releases ORDER BY updated_at DESC, id DESC').fetchall()
    counts = {'total':len(all_rows),'published':sum(r['status']=='published' for r in all_rows),'drafts':sum(r['status']=='draft' for r in all_rows),'products':len(PRODUCTS)}
    return render_template('studio.html', releases=all_rows, counts=counts)

@app.route('/studio/new', methods=['GET','POST'])
@app.route('/studio/edit/<int:release_id>', methods=['GET','POST'])
@login_required
def editor(release_id=None):
    existing = None
    if release_id:
        with db() as con: existing = con.execute('SELECT * FROM releases WHERE id=?',(release_id,)).fetchone()
        if not existing: abort(404)
    if request.method == 'POST':
        product = request.form.get('product','')
        version = request.form.get('version','').strip()
        category = request.form.get('category','feature')
        title = request.form.get('title','').strip()
        summary = request.form.get('summary','').strip()
        content = request.form.get('content','').strip()
        release_date = request.form.get('release_date','').strip() or datetime.date.today().isoformat()
        status = request.form.get('action','draft')
        if status not in ('draft','published'): status='draft'
        if product not in [p[0] for p in PRODUCTS] or category not in ['feature','improvement','fix','security','announcement'] or not title or not summary or not content:
            flash(tr('required'),'error')
            return render_template('editor.html', release=existing)
        now = datetime.datetime.now().isoformat(timespec='seconds')
        with db() as con:
            if existing:
                con.execute('UPDATE releases SET product=?,version=?,category=?,title=?,summary=?,content=?,release_date=?,status=?,updated_at=? WHERE id=?', (product,version,category,title,summary,content,release_date,status,now,release_id))
            else:
                con.execute('INSERT INTO releases(product,version,category,title,summary,content,release_date,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)', (product,version,category,title,summary,content,release_date,status,now,now))
        flash(tr('published_msg') if status=='published' else tr('saved'),'success')
        return redirect(url_for('studio'))
    return render_template('editor.html', release=existing)

@app.route('/studio/status/<int:release_id>/<action>', methods=['POST'])
@login_required
def change_status(release_id, action):
    statuses = {'publish':'published','draft':'draft','archive':'archived'}
    if action not in statuses: abort(404)
    with db() as con:
        row = con.execute('SELECT id FROM releases WHERE id=?',(release_id,)).fetchone()
        if not row: abort(404)
        con.execute('UPDATE releases SET status=?, updated_at=? WHERE id=?',(statuses[action],datetime.datetime.now().isoformat(timespec='seconds'),release_id))
    key = {'publish':'published_msg','draft':'draft_msg','archive':'archived_msg'}[action]
    flash(tr(key),'success')
    return redirect(url_for('studio'))

@app.route('/guide')
@login_required
def guide(): return render_template('guide.html')

@app.route('/studio/delete/<int:release_id>', methods=['POST'])
@login_required
def delete_release(release_id):
    with db() as con:
        row = con.execute('SELECT id FROM releases WHERE id=?', (release_id,)).fetchone()
        if not row: abort(404)
        con.execute('DELETE FROM releases WHERE id=?', (release_id,))
    flash(tr('deleted_msg'), 'success')
    return redirect(url_for('studio'))

@app.errorhandler(400)
def bad_request(e): return render_template('error.html', code=400, message=str(e.description)), 400
@app.errorhandler(404)
def not_found(e): return render_template('error.html', code=404, message=tr('not_found')), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)

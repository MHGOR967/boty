import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity, LabeledPrice
import sqlite3
import json
import os
import time
import logging

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = "8866684441:AAFrzPZztyUjkgby3FeFySFWnZJauSHEbY0"
ADMIN_ID = 5653088167
DB_FILE = "fokhm_bot.db"
CONFIG_FILE = "bot_config.json"
WEBAPP_URL = "https://your-webapp-domain.com" # استبدله برابط موقعك على fokhm.com

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# ==================== إعداد قاعدة البيانات (SQLite) ====================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TIMESTAMP,
            invited_by INTEGER,
            referral_count INTEGER DEFAULT 0,
            stars_donated INTEGER DEFAULT 0,
            is_vip INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def add_user_to_db(user_id, username, first_name, invited_by=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, username, first_name, joined_at, invited_by) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, first_name, time.time(), invited_by)
        )
        if invited_by and invited_by != user_id:
            cursor.execute("UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?", (invited_by,))
        conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT referral_count, stars_donated, is_vip FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    if res:
        return {"referrals": res[0], "stars": res[1], "vip": bool(res[2])}
    return {"referrals": 0, "stars": 0, "vip": False}

def get_total_users_count():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# ==================== إدارة الإعدادات والرسائل ====================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "welcome_message": (
            "🏴‍☠️ <b>أهلاً بك يا {name} في نظام g5wbot الماسي</b>\n"
            "--------------------------------------------------\n"
            "🔥 <b>بوابة تلغيم، تخصيص وتوقيع تطبيقات الاختراق وأمان الهواتف.</b>\n"
            "--------------------------------------------------\n"
            "⏳ <b>حالة الحساب:</b> مفعل ومؤمن بالكامل عبر منصة fokhm.com ⚡\n"
            "--------------------------------------------------\n"
            "اختر إحدى الخدمات أدناه للبدء فوراً:"
        ),
        "welcome_entities": [],
        "buttons": {
            "inject": "⚡ حقن وتلغيم تطبيق",
            "account": "🥷 معلومات حسابي",
            "invite": "🔗 دعوة صديق (ربح)",
            "vip": "💎 قسم VIP",
            "help": "❓ مساعدة",
            "donate": "⭐ تبرع للبوت"
        }
    }

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

config = load_config()

def dict_to_entities(ent_dicts):
    if not ent_dicts:
        return None
    entities = []
    for ed in ent_dicts:
        ent = MessageEntity(
            type=ed.get('type'),
            offset=ed.get('offset'),
            length=ed.get('length'),
            custom_emoji_id=ed.get('custom_emoji_id')
        )
        entities.append(ent)
    return entities

# ==================== تصميم لوحات المفاتيح (Keyboards) ====================
def get_main_keyboard():
    b = config["buttons"]
    markup = InlineKeyboardMarkup()
    
    # السطر الأول: حقن وتلغيم تطبيق (مستقل لوحده)
    btn_inject = InlineKeyboardButton(b.get("inject", "⚡ حقن وتلغيم تطبيق"), web_app=telebot.types.WebAppInfo(url=WEBAPP_URL))
    markup.row(btn_inject)
    
    # السطر الثاني: معلومات حسابي + دعوة صديق (ربح)
    btn_account = InlineKeyboardButton(b.get("account", "🥷 معلومات حسابي"), callback_data="my_account")
    btn_invite = InlineKeyboardButton(b.get("invite", "🔗 دعوة صديق (ربح)"), callback_data="invite_friends")
    markup.row(btn_account, btn_invite)
    
    # السطر الثالث: قسم VIP + مساعدة
    btn_vip = InlineKeyboardButton(b.get("vip", "💎 قسم VIP"), callback_data="vip_section")
    btn_help = InlineKeyboardButton(b.get("help", "❓ مساعدة"), callback_data="help_section")
    markup.row(btn_vip, btn_help)
    
    # السطر الرابع: تبرع للبوت
    btn_donate = InlineKeyboardButton(b.get("donate", "⭐ تبرع للبوت"), callback_data="start_donation")
    markup.row(btn_donate)
    
    return markup

def get_number_pad_keyboard(current_value="5"):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("1", callback_data="num_1"),
        InlineKeyboardButton("2", callback_data="num_2"),
        InlineKeyboardButton("3", callback_data="num_3")
    )
    markup.row(
        InlineKeyboardButton("4", callback_data="num_4"),
        InlineKeyboardButton("5", callback_data="num_5"),
        InlineKeyboardButton("6", callback_data="num_6")
    )
    markup.row(
        InlineKeyboardButton("7", callback_data="num_7"),
        InlineKeyboardButton("8", callback_data="num_8"),
        InlineKeyboardButton("9", callback_data="num_9")
    )
    markup.row(
        InlineKeyboardButton("🗑 مسح", callback_data="num_clear"),
        InlineKeyboardButton("0", callback_data="num_0"),
        InlineKeyboardButton("❌ إلغاء", callback_data="num_cancel")
    )
    markup.row(
        InlineKeyboardButton(f"✅ تأكيد التبرع ({current_value} ⭐)", callback_data="num_confirm")
    )
    return markup

def get_admin_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📊 إحصائيات البوت", callback_data="admin_stats"))
    markup.row(InlineKeyboardButton("📝 تعديل رسالة الترحيب", callback_data="admin_edit_welcome"))
    markup.row(InlineKeyboardButton("🔘 تعديل أسماء الأزرار", callback_data="admin_edit_buttons"))
    markup.row(InlineKeyboardButton("📢 إذاعة عامة للأعضاء", callback_data="admin_broadcast"))
    markup.row(InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="admin_home"))
    return markup

# تخزين مؤقت لإدخال النجوم لكل مستخدم
donation_sessions = {}

# ==================== معالجة رسائل البوت الأساسية ====================
@bot.message_handler(commands=['start'])
def handle_start(message):
    user = message.from_user
    args = message.text.split()
    invited_by = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            invited_by = int(args[1].replace("ref_", ""))
        except:
            pass
            
    add_user_to_db(user.id, user.username, user.first_name, invited_by)
    
    name = user.first_name
    welcome_template = config.get("welcome_message", "")
    welcome_text = welcome_template.format(name=name)
    ent_dicts = config.get("welcome_entities", [])
    entities = dict_to_entities(ent_dicts)
    
    # إرسال الرسالة مع دعم الكيانات والإيموجي المميزة
    try:
        requests_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": message.chat.id,
            "text": welcome_text,
            "parse_mode": "HTML",
            "reply_markup": get_main_keyboard().to_json()
        }
        if entities:
            payload["entities"] = entities
        import requests
        requests.post(requests_url, json=payload)
    except Exception as e:
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

# ==================== لوحة تحكم الآدمن المتقدمة ====================
@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ هذا الأمر مخصص للآدمن الرئيسي فقط يا فخم.")
        return
    bot.send_message(
        message.chat.id,
        "🛠 <b>لوحة تحكم الآدمن الماسية (fokhm.com):</b>\nاختر القسم المطلوب للتحكم الكامل بالنظام:",
        reply_markup=get_admin_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callbacks(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ غير مسموح لك!", show_alert=True)
        return
        
    action = call.data.replace("admin_", "")
    bot.answer_callback_query(call.id)
    
    if action == "stats":
        total_users = get_total_users_count()
        bot.edit_message_text(
            f"📊 <b>إحصائيات بوت fokhm.com:</b>\n\n"
            f"👥 إجمالي المشتركين: <b>{total_users}</b> عضو\n"
            f"⚡ حالة الخادم: يعمل بكفاءة عالية (Stable)\n"
            f"👑 المشرف العام: <code>{ADMIN_ID}</code>",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=get_admin_keyboard()
        )
    elif action == "edit_welcome":
        msg = bot.edit_message_text(
            "✍️ أرسل رسالة الترحيب الجديدة مع إيموجياتك المميزة البريميوم.\n"
            "ملاحظة: يمكنك استخدام `{name}` لاسم المستخدم تلقائياً:",
            call.message.chat.id,
            call.message.message_id
        )
        bot.register_next_step_handler(msg, process_admin_new_welcome)
    elif action == "edit_buttons":
        msg = bot.edit_message_text(
            "🔘 أرسل أسماء الأزرار الستة الجديدة مفصولة بفاصلة `,` بالترتيب التالي:\n\n"
            "<code>حقن وتلغيم,معلومات حسابي,دعوة صديق,قسم VIP,مساعدة,تبرع للبوت</code>",
            call.message.chat.id,
            call.message.message_id
        )
        bot.register_next_step_handler(msg, process_admin_new_buttons)
    elif action == "broadcast":
        msg = bot.edit_message_text(
            "📢 أرسل نص الإذاعة أو الإعلان الذي تريد إرساله لجميع الأعضاء دفعة واحدة:",
            call.message.chat.id,
            call.message.message_id
        )
        bot.register_next_step_handler(msg, process_admin_broadcast)
    elif action == "home":
        bot.edit_message_text(
            "🛠 <b>لوحة تحكم الآدمن الماسية (fokhm.com):</b>\nاختر القسم المطلوب للتحكم الكامل بالنظام:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=get_admin_keyboard()
        )

def process_admin_new_welcome(message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text or message.caption or ""
    raw_entities = message.json.get('entities') or message.json.get('caption_entities') or []
    
    entities_list = []
    for ent in raw_entities:
        ent_data = {
            "type": ent.get("type"),
            "offset": ent.get("offset"),
            "length": ent.get("length")
        }
        if ent.get("custom_emoji_id"):
            ent_data["custom_emoji_id"] = ent.get("custom_emoji_id")
        entities_list.append(ent_data)
        
    config["welcome_message"] = text
    config["welcome_entities"] = entities_list
    save_config(config)
    bot.send_message(message.chat.id, "✅ تم تحديث رسالة الترحيب بنجاح يا فخم!", reply_markup=get_admin_keyboard())

def process_admin_new_buttons(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = [p.strip() for p in message.text.split(',')]
    keys = ["inject", "account", "invite", "vip", "help", "donate"]
    if len(parts) >= 6:
        for i, k in enumerate(keys):
            config["buttons"][k] = parts[i]
        save_config(config)
        bot.send_message(message.chat.id, "✅ تم تحديث الأزرار بنجاح يا فخم!", reply_markup=get_admin_keyboard())
    else:
        bot.send_message(message.chat.id, "❌ الصيغة غير صحيحة. يجب إرسال 6 أسماء مفصولة بـ `,`.", reply_markup=get_admin_keyboard())

def process_admin_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    
    success = 0
    failed = 0
    status_msg = bot.send_message(message.chat.id, f"🚀 جاري بدء الإذاعة إلى {len(users)} مشترك...")
    
    for u in users:
        try:
            bot.send_message(u[0], f"📢 <b>إعلان رسمي من إدارة fokhm.com:</b>\n\n{text}")
            success += 1
            time.sleep(0.05) # تجنب حدود التليجرام
        except:
            failed += 1
            
    bot.edit_message_text(
        f"✅ <b>تمت الإذاعة بنجاح يا فخم!</b>\n\n"
        f"📤 المرسل لهم: <b>{success}</b>\n"
        f"❌ فشل الإرسال: <b>{failed}</b>",
        message.chat.id,
        status_msg.message_id,
        reply_markup=get_admin_keyboard()
    )

# ==================== نظام التبرع التفاعلي بالنجوم (Telegram Stars) ====================
@bot.callback_query_handler(func=lambda call: call.data == "start_donation")
def start_donation(call):
    bot.answer_callback_query(call.id)
    donation_sessions[call.from_user.id] = "5"
    bot.edit_message_text(
        "⭐ <b>نظام الدعم والتبرع بالنجوم لمنصة fokhm.com</b>\n\n"
        "اختر عدد النجوم التي تود التبرع بها عبر لوحة الأرقام أدناه، ثم اضغط زر التأكيد:\n\n"
        "📌 <b>الكمية المحددة حالياً:</b> <code>5</code> نجوم",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=get_number_pad_keyboard("5")
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("num_"))
def handle_number_pad_donation(call):
    user_id = call.from_user.id
    action = call.data.replace("num_", "")
    current = donation_sessions.get(user_id, "5")
    
    if action.isdigit():
        if current == "5":
            current = action
        else:
            current += action
    elif action == "clear":
        current = "0"
    elif action == "cancel":
        if user_id in donation_sessions:
            del donation_sessions[user_id]
        bot.edit_message_text(
            "❌ تم إلغاء عملية التبرع بنجاح.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=get_main_keyboard()
        )
        bot.answer_callback_query(call.id)
        return
    elif action == "confirm":
        try:
            amount = int(current or "1")
            if amount <= 0:
                amount = 1
        except:
            amount = 5
            
        if user_id in donation_sessions:
            del donation_sessions[user_id]
            
        bot.edit_message_text(
            f"✅ <b>جاري إصدار فاتورة التبرع بمبلغ {amount} نجمة (Telegram Stars)...</b>\n"
            f"شكراً لدعمك المستمر لمنصة fokhm.com ⚡",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id)
        
        # إرسال فاتورة النجوم الحقيقية عبر تليجرام
        bot.send_invoice(
            chat_id=call.message.chat.id,
            title="تبرع لدعم منصة fokhm.com ⚡",
            description=f"مساهمة مالية بقيمة {amount} نجمة لدعم وتطوير أدوات التلغيم.",
            payload=f"donation_{user_id}_{amount}",
            currency="XTR", # عملة النجوم الرسمية في تليجرام
            prices=[LabeledPrice(label=f"دعم {amount} نجمة", amount=amount)]
        )
        return
        
    donation_sessions[user_id] = current
    bot.edit_message_text(
        "⭐ <b>نظام الدعم والتبرع بالنجوم لمنصة fokhm.com</b>\n\n"
        "اختر عدد النجوم التي تود التبرع بها عبر لوحة الأرقام أدناه، ثم اضغط زر التأكيد:\n\n"
        f"📌 <b>الكمية المحددة حالياً:</b> <code>{current}</code> نجوم",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=get_number_pad_keyboard(current)
    )
    bot.answer_callback_query(call.id)

@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    payment = message.successful_payment
    payload = payment.invoice_payload
    user_id = message.from_user.id
    
    amount = 5
    if payload.startswith("donation_"):
        try:
            amount = int(payload.split("_")[2])
        except:
            pass
            
    # تحديث إحصائيات التبرع في قاعدة البيانات
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET stars_donated = stars_donated + ?, is_vip = 1 WHERE user_id = ?", (amount, user_id))
    cursor.execute("INSERT INTO donations (user_id, amount, created_at) VALUES (?, ?, ?)", (user_id, amount, time.time()))
    conn.commit()
    conn.close()
    
    bot.send_message(
        message.chat.id,
        f"🎉 <b>تم استلام تبرعك بـ {amount} نجمة بنجاح يا فخم!</b>\n"
        f"👑 تم ترقية حسابك إلى رتبة (VIP) تلقائياً على منصة fokhm.com ⚡ شكراً لدعمك الخارق!",
        reply_markup=get_main_keyboard()
    )

# ==================== معالجة باقي الأزرار التفاعلية ====================
@bot.callback_query_handler(func=lambda call: True)
def handle_general_callbacks(call):
    user_id = call.from_user.id
    if call.data == "my_account":
        bot.answer_callback_query(call.id)
        stats = get_user_stats(user_id)
        vip_status = "💎 عضو مميز (VIP)" if stats["vip"] or user_id == ADMIN_ID else "🛡 عضو عادي"
        bot.send_message(
            call.message.chat.id,
            f"🥷 <b>معلومات حسابك الشخصي:</b>\n\n"
            f"🆔 المعرّف: <code>{user_id}</code>\n"
            f"⚡ الرتبة: {vip_status}\n"
            f"👥 عدد الدعوات: <b>{stats['referrals']}</b> شخص\n"
            f"⭐ إجمالي التبرعات: <b>{stats['stars']}</b> نجمة\n"
            f"🌐 المنصة: <b>fokhm.com</b>"
        )
    elif call.data == "invite_friends":
        bot.answer_callback_query(call.id)
        bot_info = bot.get_me()
        invite_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
        bot.send_message(
            call.message.chat.id,
            f"🔗 <b>نظام الدعوات والأرباح الماسي:</b>\n\n"
            f"شارك رابط الدعوة الخاص بك مع أصدقائك لتحصل على نقاط وصلاحيات VIP:\n\n"
            f"<code>{invite_link}</code>"
        )
    elif call.data == "vip_section":
        bot.answer_callback_query(call.id, "💎 قسم VIP يمنحك صلاحيات حصرية. قم بدعوة 5 أشخاص أو تبرع بالنجوم لفتحه فوراً!", show_alert=True)
    elif call.data == "help_section":
        bot.answer_callback_query(call.id, "❓ للدعم الفني والتواصل المباشر تفضل بزيارة موقعنا: fokhm.com", show_alert=True)

if __name__ == "__main__":
    print(f"🤖 Production Bot for fokhm.com is running smoothly for Admin {ADMIN_ID}...")
    bot.infinity_polling(skip_pending=True)

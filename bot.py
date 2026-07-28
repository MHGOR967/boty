import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity
import json
import os

TOKEN = "8605564070:AAHr2VkjU9XUhABvL7UNLS7Mlhk7Vkj_0zc"
ADMIN_ID = 5653088167
CONFIG_FILE = "bot_config.json"
WEBAPP_URL = "https://pywahm.onrender.com" # رابط موقعك على Render مثلاً fokhm.com

bot = telebot.TeleBot(TOKEN)

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

def get_main_keyboard():
    b = config["buttons"]
    markup = InlineKeyboardMarkup(row_width=2)
    
    # السطر الأول: حقن وتلغيم تطبيق (لوحده)
    btn_inject = InlineKeyboardButton(b.get("inject", "⚡ حقن وتلغيم تطبيق"), web_app=telebot.types.WebAppInfo(url=WEBAPP_URL))
    markup.add(btn_inject)
    
    # السطر الثاني: معلومات حسابي + دعوة صديق
    btn_account = InlineKeyboardButton(b.get("account", "🥷 معلومات حسابي"), callback_data="my_account")
    btn_invite = InlineKeyboardButton(b.get("invite", "🔗 دعوة صديق (ربح)"), callback_data="invite_friends")
    markup.add(btn_account, btn_invite)
    
    # السطر الثالث: قسم VIP + مساعدة
    btn_vip = InlineKeyboardButton(b.get("vip", "💎 قسم VIP"), callback_data="vip_section")
    btn_help = InlineKeyboardButton(b.get("help", "❓ مساعدة"), callback_data="help_section")
    markup.add(btn_vip, btn_help)
    
    # السطر الرابع: تبرع للبوت
    btn_donate = InlineKeyboardButton(b.get("donate", "⭐ تبرع للبوت"), callback_data="start_donation")
    markup.add(btn_donate)
    
    return markup

def send_telegram_message(chat_id, text, entities=None, reply_markup=None):
    import requests
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if entities:
        payload["entities"] = entities
    if reply_markup:
        payload["reply_markup"] = reply_markup.to_json()
    requests.post(url, json=payload)

@bot.message_handler(commands=['start'])
def handle_start(message):
    name = message.from_user.first_name
    welcome_template = config.get("welcome_message", "")
    welcome_text = welcome_template.format(name=name)
    ent_dicts = config.get("welcome_entities", [])
    entities = dict_to_entities(ent_dicts)
    
    send_telegram_message(message.chat.id, welcome_text, entities=entities, reply_markup=get_main_keyboard())

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ هذا الأمر مخصص للآدمن فقط يا فخم.")
        return
        
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📝 تعديل رسالة الترحيب", callback_data="edit_welcome"),
        InlineKeyboardButton("🔘 تعديل أسماء الأزرار", callback_data="edit_buttons")
    )
    bot.send_message(
        message.chat.id,
        "🛠 <b>لوحة تحكم الآدمن الماسية (fokhm.com):</b>\nاختر ما تريد تعديله:",
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == "edit_welcome")
def edit_welcome_callback(call):
    if call.from_user.id != ADMIN_ID:
        return
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        "✍️ أرسل رسالة الترحيب الجديدة مع إيموجياتك المميزة.\nملاحظة: يمكنك استخدام `{name}` لاسم المستخدم تلقائياً:"
    )
    bot.register_next_step_handler(msg, process_new_welcome)

def process_new_welcome(message):
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
    bot.send_message(message.chat.id, "✅ تم تحديث رسالة الترحيب بنجاح يا فخم!", reply_markup=get_main_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "edit_buttons")
def edit_buttons_callback(call):
    if call.from_user.id != ADMIN_ID:
        return
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        "🔘 أرسل أسماء الأزرار الستة الجديدة مفصولة بفاصلة `,` بالترتيب التالي:\n\n"
        "<code>حقن وتلغيم,معلومات حسابي,دعوة صديق,قسم VIP,مساعدة,تبرع للبوت</code>",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, process_new_buttons)

def process_new_buttons(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = [p.strip() for p in message.text.split(',')]
    keys = ["inject", "account", "invite", "vip", "help", "donate"]
    if len(parts) >= 6:
        for i, k in enumerate(keys):
            config["buttons"][k] = parts[i]
        save_config(config)
        bot.send_message(message.chat.id, "✅ تم تحديث الأزرار بنجاح يا فخم!", reply_markup=get_main_keyboard())
    else:
        bot.send_message(message.chat.id, "❌ الصيغة غير صحيحة. يجِب إرسال 6 أسماء مفصولة بـ `,`.")

@bot.callback_query_handler(func=lambda call: call.data == "start_donation")
def start_donation(call):
    bot.answer_callback_query(call.id)
    # إرسال فاتورة نجوم تليجرام الافتراضية
    bot.send_invoice(
        chat_id=call.message.chat.id,
        title="تبرع لدعم منصة fokhm.com ⚡",
        description="مساهمة مالية لتطوير خدمات التلغيم والحقن الآمن.",
        payload="donation_stars_payload",
        currency="XTR",
        prices=[telebot.types.LabeledPrice(label="نجوم الدعم", amount=10)]
    )

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id, "🎉 <b>تم استلام تبرعك بنجاح يا فخم!</b> شكراً لدعمك المستمر لمنصة fokhm.com ⚡", parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    if call.data == "my_account":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🥷 <b>معلومات حسابك:</b>\n🆔 المعرّف: <code>{user_id}</code>\n⚡ الحالة: عضو مميز\n🌐 المنصة: fokhm.com", parse_mode='HTML')
    elif call.data == "invite_friends":
        bot.answer_callback_query(call.id)
        invite_link = f"https://t.me/g5wbot/wahmapk?startapp=ref_{user_id}"
        bot.send_message(call.message.chat.id, f"🔗 <b>نظام الدعوات والأرباح:</b>\nشارك رابطك الخاص:\n<code>{invite_link}</code>", parse_mode='HTML')
    elif call.data == "vip_section":
        bot.answer_callback_query(call.id, "💎 قسم VIP غير محدود متاح عبر دعوة 5 أشخاص أو التبرع بالنجوم!", show_alert=True)
    elif call.data == "help_section":
        bot.answer_callback_query(call.id, "❓ للدعم الفني والاستفسارات تواصل عبر منصة fokhm.com", show_alert=True)

if __name__ == "__main__":
    print(f"🤖 Stable Telebot for fokhm.com is running for {ADMIN_ID}...")
    bot.infinity_polling()

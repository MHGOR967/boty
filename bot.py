
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

TOKEN = '8866684441:AAFrzPZztyUjkgby3FeFySFWnZJauSHEbY0'
ADMIN_ID = 5653088167

# استخدام HTML لضمان قبول الإيموجي المميزة وكیانات تليجرام البريميوم بدقة
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
WEBAPP_URL = 'https://your-webapp-domain.com'

SETTINGS_FILE = 'bot_settings.json'

default_settings = {
    "welcome_message": "🏴‍☠️ <b>أهلاً بك يا فخم في نظام g5wbot الماسي</b>\n--------------------------------------------------\n🔥 <b>بوابة تلغيم، تخصيص وتوقيع تطبيقات الاختراق والأمان باحترافية تامة.</b>\n--------------------------------------------------\n⏳ <b>حالة الحساب:</b> مفعل ومؤمن بالكامل عبر منصة fokhm.com ⚡\n--------------------------------------------------\nاختر إحدى الخدمات أدناه للبدء فوراً:",
    "btn_inject": "⚡ حقن وتلغيم تطبيق",
    "btn_account": "🥷 حسابي وVIP",
    "btn_invite": "🔗 دعوة صديق (ربح)",
    "btn_site": "🌐 موقع فخم الرسمي"
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_settings
    return default_settings

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

def get_main_keyboard(user_id):
    settings = load_settings()
    markup = InlineKeyboardMarkup(row_width=2)
    
    btn_inject = InlineKeyboardButton(settings["btn_inject"], web_app=telebot.types.WebAppInfo(url=WEBAPP_URL))
    btn_account = InlineKeyboardButton(settings["btn_account"], callback_data="my_account")
    btn_invite = InlineKeyboardButton(settings["btn_invite"], callback_data="invite_friends")
    btn_site = InlineKeyboardButton(settings["btn_site"], url="https://fokhm.com")
    
    markup.add(btn_inject)
    markup.add(btn_account, btn_invite)
    markup.add(btn_site)
    
    if user_id == ADMIN_ID:
        btn_admin = InlineKeyboardButton("🛠 لوحة تحكم الآدمن", callback_data="admin_panel")
        markup.add(btn_admin)
        
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    settings = load_settings()
    
    personalized_msg = f"👋 أهلاً بك يا <b>{first_name}</b>!\n\n" + settings["welcome_message"]
    bot.send_message(
        message.chat.id,
        personalized_msg,
        reply_markup=get_main_keyboard(user_id)
    )

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ هذا الأمر مخصص للآدمن فقط يا فخم.")
        return
        
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📝 تعديل رسالة الترحيب", callback_data="set_welcome"),
        InlineKeyboardButton("🔘 تعديل أسماء الأزرار", callback_data="set_buttons"),
        InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_home")
    )
    bot.send_message(
        message.chat.id,
        "🛠 <b>لوحة تحكم الآدمن الماسية (fokhm.com):</b>\n\nاختر ما تريد تعديله لإضافة إيموجياتك المميزة:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data == "my_account":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"🥷 <b>معلومات حسابك الشخصي:</b>\n\n🆔 المعرّف (ID): <code>{user_id}</code>\n⚡ الحالة: عضو مميز في شبكة g5wbot\n🌐 المنصة: fokhm.com",
            parse_mode='HTML'
        )
        
    elif call.data == "invite_friends":
        bot.answer_callback_query(call.id)
        invite_link = f"https://t.me/g5wbot/wahmapk?startapp=ref_{user_id}"
        bot.send_message(
            call.message.chat.id,
            f"🔗 <b>نظام دعوة الأعضاء (g5wbot):</b>\n\nشارك رابطك الخاص أدناه مع أصدقائك. عند دعوة 5 أشخاص عبر الـ Web App، سيتم تفعيل الصنع اللانهائي لحسابك فوراً:\n\n<code>{invite_link}</code>",
            parse_mode='HTML'
        )
        
    elif call.data == "admin_panel" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("📝 تعديل رسالة الترحيب", callback_data="set_welcome"),
            InlineKeyboardButton("🔘 تعديل أسماء الأزرار", callback_data="set_buttons"),
            InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_home")
        )
        bot.edit_message_text(
            "🛠 <b>لوحة تحكم الآدمن الماسية (fokhm.com):</b>\n\nاختر ما تريد تعديله لإضافة إيموجياتك المميزة:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
        
    elif call.data == "set_welcome" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        msg = bot.send_message(
            call.message.chat.id,
            "✍️ أرسل النص الجديد لرسالة الترحيب الآن (مع إيموجياتك المميزة وبصيغة HTML لو أردت):"
        )
        bot.register_next_step_handler(msg, save_new_welcome)

    elif call.data == "set_buttons" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        msg = bot.send_message(
            call.message.chat.id,
            "🔘 أرسل أسماء الأزرار الأربعة الجديدة مفصولة بفاصلة `,` بالشكل التالي:\n\n<code>زر الحقن,زر الحساب,زر الدعوة,زر الموقع</code>"
        )
        bot.register_next_step_handler(msg, save_new_buttons)

    elif call.data == "back_home":
        bot.answer_callback_query(call.id)
        settings = load_settings()
        bot.edit_message_text(
            f"👋 القائمة الرئيسية:\n\n" + settings["welcome_message"],
            call.message.chat.id,
            call.message.message_id,
            reply_markup=get_main_keyboard(user_id)
        )

def save_new_welcome(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    # استخراج النص أو الكيانات (Entities) البرمجية لدعم الإيموجي المميزة والبريميوم بدقة
    if message.content_type == 'text':
        # استخدام html_text للحفاظ على الإيموجي المميزة وكيانات تليجرام
        new_text = message.html_text if hasattr(message, 'html_text') else message.text
        settings = load_settings()
        settings["welcome_message"] = new_text
        save_settings(settings)
        bot.send_message(message.chat.id, "✅ <b>تم تحديث رسالة الترحيب مع الإيموجي المميزة بنجاح يا فخم!</b>", parse_mode='HTML', reply_markup=get_main_keyboard(ADMIN_ID))
    else:
        bot.send_message(message.chat.id, "❌ يجِب إرسال نص يحتوي على الكلمات والإيموجي المطلوبة.")

def save_new_buttons(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(',')
    if len(parts) == 4:
        settings = load_settings()
        settings["btn_inject"] = parts[0].strip()
        settings["btn_account"] = parts[1].strip()
        settings["btn_invite"] = parts[2].strip()
        settings["btn_site"] = parts[3].strip()
        save_settings(settings)
        bot.send_message(message.chat.id, "✅ <b>تم تحديث أسماء الأزرار والإيموجي المميزة بنجاح يا زعيم!</b>", parse_mode='HTML', reply_markup=get_main_keyboard(ADMIN_ID))
    else:
        bot.send_message(message.chat.id, "❌ الصيغة غير صحيحة. تأكد من إرسال 4 أسماء مفصولة بـ `,`.", parse_mode='HTML', reply_markup=get_main_keyboard(ADMIN_ID))

if __name__ == '__main__':
    print(f"🤖 Bot with Custom Emoji support is running for {ADMIN_ID}...")
    bot.infinity_polling()

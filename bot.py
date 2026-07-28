
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

TOKEN = '8866684441:AAFrzPZztyUjkgby3FeFySFWnZJauSHEbY0'
ADMIN_ID = 5653088167

bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')
WEBAPP_URL = 'https://your-webapp-domain.com'

SETTINGS_FILE = 'bot_settings.json'

default_settings = {
    "welcome_message": "🏴‍☠️ **أهلاً بك يا فخم في نظام g5wbot الماسي**\n--------------------------------------------------\n🔥 **بوابة تلغيم، تخصيص وتوقيع تطبيقات الاختراق والأمان باحترافية تامة.**\n--------------------------------------------------\n⏳ **حالة الحساب:** مفعل ومؤمن بالكامل عبر منصة fokhm.com ⚡\n--------------------------------------------------\nاختر إحدى الخدمات أدناه للبدء فوراً:",
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
    
    personalized_msg = f"👋 أهلاً بك يا *{first_name}*!\n\n" + settings["welcome_message"]
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
        "🛠 **لوحة تحكم الآدمن الماسية (fokhm.com):**\n\nاختر ما تريد تعديله لإضافة إيموجياتك المميزة:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data == "my_account":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"🥷 **معلومات حسابك الشخصي:**\n\n🆔 المعرّف (ID): `{user_id}`\n⚡ الحالة: عضو مميز في شبكة g5wbot\n🌐 المنصة: fokhm.com",
            parse_mode='Markdown'
        )
        
    elif call.data == "invite_friends":
        bot.answer_callback_query(call.id)
        invite_link = f"https://t.me/g5wbot/wahmapk?startapp=ref_{user_id}"
        bot.send_message(
            call.message.chat.id,
            f"🔗 **نظام دعوة الأعضاء (g5wbot):**\n\nشارك رابطك الخاص أدناه مع أصدقائك. عند دعوة 5 أشخاص عبر الـ Web App، سيتم تفعيل الصنع اللانهائي لحسابك فوراً:\n\n`{invite_link}`",
            parse_mode='Markdown'
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
            "🛠 **لوحة تحكم الآدمن الماسية (fokhm.com):**\n\nاختر ما تريد تعديله لإضافة إيموجياتك المميزة:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
        
    elif call.data == "set_welcome" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        msg = bot.send_message(
            call.message.chat.id,
            "✍️ أرسل النص الجديد لرسالة الترحيب الآن (يمكنك إدراج الإيموجي المميزة براحتك):"
        )
        bot.register_next_step_handler(msg, save_new_welcome)

    elif call.data == "set_buttons" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        msg = bot.send_message(
            call.message.chat.id,
            "🔘 أرسل أسماء الأزرار الأربعة الجديدة مفصولة بفاصلة `,` بالشكل التالي:\n\n`زر الحقن,زر الحساب,زر الدعوة,زر الموقع`"
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
    settings = load_settings()
    settings["welcome_message"] = message.text
    save_settings(settings)
    bot.send_message(message.chat.id, "✅ **تم تحديث رسالة الترحيب بنجاح يا فخم!**", reply_markup=get_main_keyboard(ADMIN_ID))

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
        bot.send_message(message.chat.id, "✅ **تم تحديث أسماء الأزرار والإيموجي بنجاح يا زعيم!**", reply_markup=get_main_keyboard(ADMIN_ID))
    else:
        bot.send_message(message.chat.id, "❌ الصيغة غير صحيحة. تأكد من إرسال 4 أسماء مفصولة بـ `,`.", reply_markup=get_main_keyboard(ADMIN_ID))

if __name__ == '__main__':
    print(f"🤖 Bot with /admin command is running for {ADMIN_ID}...")
    bot.infinity_polling()

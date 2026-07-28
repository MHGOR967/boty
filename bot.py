
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# توكن البوت الجديد الذي أرسلته
TOKEN = '8866684441:AAFrzPZztyUjkgby3FeFySFWnZJauSHEbY0'
ADMIN_ID = 5653088167  # أيدي الآدمن الخاص بك

bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

# رابط الـ Web App الخاص بمنصتك fokhm.com
WEBAPP_URL = 'https://your-webapp-domain.com'

# رسالة الترحيب المخصصة مع الإيموجي المميزة
WELCOME_MESSAGE = """
🏴‍☠️ **أهلاً بك يا فخم في نظام g5wbot الماسي**
--------------------------------------------------
🔥 **بوابة تلغيم، تخصيص وتوقيع تطبيقات الاختراق والأمان باحترافية تامة.**
--------------------------------------------------
⏳ **حالة الحساب:** مفعل ومؤمن بالكامل عبر منصة fokhm.com ⚡
--------------------------------------------------
اختر إحدى الخدمات أدناه للبدء فوراً:
"""

def get_main_keyboard(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    
    # الأزرار الرئيسية بالتسميات المخصصة
    btn_inject = InlineKeyboardButton("⚡ حقن وتلغيم تطبيق", web_app=telebot.types.WebAppInfo(url=WEBAPP_URL))
    btn_account = InlineKeyboardButton("🥷 حسابي وVIP", callback_data="my_account")
    btn_invite = InlineKeyboardButton("🔗 دعوة صديق (ربح)", callback_data="invite_friends")
    btn_site = InlineKeyboardButton("🌐 موقع فخم الرسمي", url="https://fokhm.com")
    
    markup.add(btn_inject)
    markup.add(btn_account, btn_invite)
    markup.add(btn_site)
    
    # إذا كان المستخدم هو الآدمن، نظهر له زر لوحة التحكم الإدارية
    if user_id == ADMIN_ID:
        btn_admin = InlineKeyboardButton("🛠 لوحة تحكم الآدمن", callback_data="admin_panel")
        markup.add(btn_admin)
        
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    personalized_msg = f"👋 أهلاً بك يا *{first_name}*!\n" + WELCOME_MESSAGE
    bot.send_message(
        message.chat.id,
        personalized_msg,
        reply_markup=get_main_keyboard(user_id)
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
        bot.send_message(
            call.message.chat.id,
            "🛠 **أهلاً بك يا فخم في لوحة تحكم الآدمن:**\n\nصلاحياتك مفعلة بالكامل كمدير لمنصة fokhm.com و g5wbot.",
            parse_mode='Markdown'
        )

if __name__ == '__main__':
    print(f"🤖 Bot is running successfully for admin {ADMIN_ID}...")
    bot.infinity_polling()


import asyncio
import sys
import subprocess
import json
import os

try:
    import aiogram
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiogram"])
    import aiogram

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = "8866684441:AAFrzPZztyUjkgby3FeFySFWnZJauSHEbY0"
ADMIN_ID = 5653088167
CONFIG_FILE = "bot_config.json"
WEBAPP_URL = "https://your-webapp-domain.com" # استبدله برابط موقعك على Render مثلاً fokhm.com

class AdminState(StatesGroup):
    waiting_for_welcome_message = State()
    waiting_for_buttons = State()

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "welcome_message": (
            "🏴‍☠️ <b>أهلاً بك يا فخم في نظام g5wbot الماسي</b>\n"
            "--------------------------------------------------\n"
            "🔥 <b>بوابة تلغيم، تخصيص وتوقيع تطبيقات الاختراق وأمان الهواتف.</b>\n"
            "--------------------------------------------------\n"
            "⏳ <b>حالة الحساب:</b> مفعل ومؤمن بالكامل عبر منصة fokhm.com ⚡\n"
            "--------------------------------------------------\n"
            "اختر إحدى الخدمات أدناه للبدء فوراً:"
        ),
        "buttons": [
            {"text": "⚡ حقن وتلغيم تطبيق", "callback_data": "inject_action", "icon_custom_emoji_id": None},
            {"text": "🥷 حسابي وVIP", "callback_data": "my_account", "icon_custom_emoji_id": None},
            {"text": "🔗 دعوة صديق (ربح)", "callback_data": "invite_friends", "icon_custom_emoji_id": None},
            {"text": "🌐 موقع فخم الرسمي", "callback_data": "fokhm_site", "icon_custom_emoji_id": None}
        ]
    }

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

config = load_config()

def parse_message_with_emojis(message: types.Message):
    text = message.html_text
    text = text.replace("<emoji ", "<tg-emoji ").replace("</emoji>", "</tg-emoji>")
    return text

async def start_bot():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def handle_start(message: types.Message):
        user_id = message.from_user.id
        builder = InlineKeyboardBuilder()
        
        # زر الحقن الموجه للـ Web App
        builder.row(types.InlineKeyboardButton(
            text=config["buttons"][0]["text"],
            web_app=types.WebAppInfo(url=WEBAPP_URL),
            icon_custom_emoji_id=config["buttons"][0].get("icon_custom_emoji_id")
        ))
        
        # باقي الأزرار
        for btn_data in config["buttons"][1:]:
            builder.row(types.InlineKeyboardButton(
                text=btn_data["text"],
                callback_data=btn_data["callback_data"],
                icon_custom_emoji_id=btn_data.get("icon_custom_emoji_id")
            ))
            
        try:
            await message.answer(
                config["welcome_message"],
                reply_markup=builder.as_markup()
            )
        except Exception as e:
            print(f"Error sending welcome message: {e}")
            await message.answer(config["welcome_message"])

    @dp.message(Command("admin"), F.from_user.id == ADMIN_ID)
    async def admin_panel(message: types.Message):
        builder = InlineKeyboardBuilder()
        builder.button(text="📝 تعديل رسالة الترحيب", callback_data="edit_welcome")
        builder.button(text="🔘 تعديل أسماء الأزرار", callback_data="edit_buttons")
        builder.adjust(1)
        await message.answer("🛠 <b>لوحة تحكم الآدمن الماسية (fokhm.com):</b>\nاختر ما تريد تعديله:", reply_markup=builder.as_markup())

    @dp.callback_query(F.data == "edit_welcome", F.from_user.id == ADMIN_ID)
    async def edit_welcome_callback(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.message.edit_text("✍️ أرسل رسالة الترحيب الجديدة مع إيموجياتك المميزة (بريميوم):")
        await state.set_state(AdminState.waiting_for_welcome_message)
        await callback_query.answer()

    @dp.message(AdminState.waiting_for_welcome_message, F.from_user.id == ADMIN_ID)
    async def process_new_welcome(message: types.Message, state: FSMContext):
        global config
        config["welcome_message"] = parse_message_with_emojis(message)
        save_config(config)
        await message.answer("✅ تم تحديث رسالة الترحيب مع الإيموجي المميزة بنجاح يا فخم!")
        await state.clear()
        await admin_panel(message)

    @dp.callback_query(F.data == "edit_buttons", F.from_user.id == ADMIN_ID)
    async def edit_buttons_callback(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.message.edit_text(
            "🔘 أرسل أسماء الأزرار الأربعة الجديدة مفصولة بفاصلة `,` بالشكل التالي:\n\n"
            "<code>زر الحقن,زر الحساب,زر الدعوة,زر الموقع</code>\n\n"
            "ملاحظة: يمكنك إرسال رموز تعبيرية مميزة بجانب الاسم."
        )
        await state.set_state(AdminState.waiting_for_buttons)
        await callback_query.answer()

    @dp.message(AdminState.waiting_for_buttons, F.from_user.id == ADMIN_ID)
    async def process_new_buttons(message: types.Message, state: FSMContext):
        global config
        parts = message.text.split(',')
        if len(parts) >= 4:
            for i in range(min(4, len(parts))):
                custom_emoji_id = None
                if message.entities:
                    for entity in message.entities:
                        if entity.type == "custom_emoji":
                            custom_emoji_id = entity.custom_emoji_id
                            break
                config["buttons"][i]["text"] = parts[i].strip()
                if custom_emoji_id:
                    config["buttons"][i]["icon_custom_emoji_id"] = custom_emoji_id
            save_config(config)
            await message.answer("✅ تم تحديث الأزرار بنجاح يا فخم!")
        else:
            await message.answer("❌ الصيغة خاطئة. تأكد من إرسال 4 أسماء مفصولة بـ `,`.")
        await state.clear()
        await admin_panel(message)

    @dp.callback_query(F.data == "my_account")
    async def callback_account(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        await callback_query.answer()
        await callback_query.message.answer(f"🥷 معلومات حسابك:\n🆔 المعرّف: <code>{user_id}</code>\n🌐 المنصة: fokhm.com")

    @dp.callback_query(F.data == "invite_friends")
    async def callback_invite(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        await callback_query.answer()
        invite_link = f"https://t.me/g5wbot/wahmapk?startapp=ref_{user_id}"
        await callback_query.message.answer(f"🔗 نظام الدعوات:\nشارك رابطك:\n<code>{invite_link}</code>")

    @dp.callback_query(F.data == "fokhm_site")
    async def callback_site(callback_query: types.CallbackQuery):
        await callback_query.answer("🌐 موقع فخم الرسمي: https://fokhm.com", show_alert=True)

    @dp.callback_query()
    async def handle_other_callbacks(callback_query: types.CallbackQuery):
        await callback_query.answer()

    print("🤖 Aiogram Bot with full Custom Emoji support is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())

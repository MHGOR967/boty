import asyncio
import sys
import subprocess
import json
import os
import sqlite3
import time

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
DB_FILE = "fokhm_bot.db"
WEBAPP_URL = "https://your-webapp-domain.com" # استبدله برابط موقعك على Render مثلاً fokhm.com

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
            "🏴‍☠️ <b>أهلاً بك يا {name} في نظام g5wbot الماسي</b>\n"
            "--------------------------------------------------\n"
            "🔥 <b>بوابة تلغيم، تخصيص وتوقيع تطبيقات الاختراق وأمان الهواتف.</b>\n"
            "--------------------------------------------------\n"
            "⏳ <b>حالة الحساب:</b> مفعل ومؤمن بالكامل عبر منصة fokhm.com ⚡\n"
            "--------------------------------------------------\n"
            "اختر إحدى الخدمات أدناه للبدء فوراً:"
        ),
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

def parse_message_with_emojis(message: types.Message):
    text = message.html_text
    text = text.replace("<emoji ", "<tg-emoji ").replace("</emoji>", "</tg-emoji>")
    return text

def get_main_keyboard():
    b = config["buttons"]
    builder = InlineKeyboardBuilder()
    
    builder.row(types.InlineKeyboardButton(
        text=b.get("inject", "⚡ حقن وتلغيم تطبيق"),
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    ))
    builder.row(
        types.InlineKeyboardButton(text=b.get("account", "🥷 معلومات حسابي"), callback_data="my_account"),
        types.InlineKeyboardButton(text=b.get("invite", "🔗 دعوة صديق (ربح)"), callback_data="invite_friends")
    )
    builder.row(
        types.InlineKeyboardButton(text=b.get("vip", "💎 قسم VIP"), callback_data="vip_section"),
        types.InlineKeyboardButton(text=b.get("help", "❓ مساعدة"), callback_data="help_section")
    )
    builder.row(types.InlineKeyboardButton(
        text=b.get("donate", "⭐ تبرع للبوت"),
        callback_data="start_donation"
    ))
    return builder.as_markup()

def get_number_pad_keyboard(current_value="5"):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="1", callback_data="num_1"),
        types.InlineKeyboardButton(text="2", callback_data="num_2"),
        types.InlineKeyboardButton(text="3", callback_data="num_3")
    )
    builder.row(
        types.InlineKeyboardButton(text="4", callback_data="num_4"),
        types.InlineKeyboardButton(text="5", callback_data="num_5"),
        types.InlineKeyboardButton(text="6", callback_data="num_6")
    )
    builder.row(
        types.InlineKeyboardButton(text="7", callback_data="num_7"),
        types.InlineKeyboardButton(text="8", callback_data="num_8"),
        types.InlineKeyboardButton(text="9", callback_data="num_9")
    )
    builder.row(
        types.InlineKeyboardButton(text="🗑 مسح", callback_data="num_clear"),
        types.InlineKeyboardButton(text="0", callback_data="num_0"),
        types.InlineKeyboardButton(text="❌ إلغاء", callback_data="num_cancel")
    )
    builder.row(
        types.InlineKeyboardButton(text=f"✅ تأكيد التبرع ({current_value} ⭐)", callback_data="num_confirm")
    )
    return builder.as_markup()

async def start_bot():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def handle_start(message: types.Message):
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
        welcome_text = config["welcome_message"].format(name=name)
        try:
            await message.answer(welcome_text, reply_markup=get_main_keyboard())
        except Exception as e:
            await message.answer(welcome_text.replace("<tg-emoji", "").replace("</tg-emoji>", ""), reply_markup=get_main_keyboard())

    @dp.message(Command("admin"), F.from_user.id == ADMIN_ID)
    async def admin_panel(message: types.Message):
        builder = InlineKeyboardBuilder()
        builder.button(text="📝 تعديل رسالة الترحيب", callback_data="edit_welcome")
        builder.button(text="🔘 تعديل أسماء الأزرار", callback_data="edit_buttons")
        builder.adjust(1)
        await message.answer("🛠 <b>لوحة تحكم الآدمن الماسية (fokhm.com):</b>\nاختر ما تريد تعديله:", reply_markup=builder.as_markup())

    @dp.callback_query(F.data == "edit_welcome", F.from_user.id == ADMIN_ID)
    async def edit_welcome_callback(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.message.edit_text("✍️ أرسل رسالة الترحيب الجديدة مع إيموجياتك المميزة (بريميوم).\nملاحظة: يمكنك استخدام `{name}` لاسم المستخدم تلقائياً:")
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
            "🔘 أرسل أسماء الأزرار الستة الجديدة مفصولة بفاصلة `,` بالترتيب التالي:\n\n"
            "<code>حقن وتلغيم,معلومات حسابي,دعوة صديق,قسم VIP,مساعدة,تبرع للبوت</code>"
        )
        await state.set_state(AdminState.waiting_for_buttons)
        await callback_query.answer()

    @dp.message(AdminState.waiting_for_buttons, F.from_user.id == ADMIN_ID)
    async def process_new_buttons(message: types.Message, state: FSMContext):
        global config
        parts = [p.strip() for p in message.text.split(',')]
        keys = ["inject", "account", "invite", "vip", "help", "donate"]
        if len(parts) >= 6:
            for i, k in enumerate(keys):
                config["buttons"][k] = parts[i]
            save_config(config)
            await message.answer("✅ تم تحديث الأزرار بنجاح يا فخم!")
        else:
            await message.answer("❌ الصيغة غير صحيحة. يجب إرسال 6 أسماء مفصولة بـ `,`.")
        await state.clear()
        await admin_panel(message)

    @dp.callback_query(F.data == "start_donation")
    async def start_donation(callback_query: types.CallbackQuery, state: FSMContext):
        await state.update_data(donation_amount="5")
        await callback_query.message.edit_text(
            "⭐ <b>نظام الدعم والتبرع بالنجوم لمنصة fokhm.com</b>\n\n"
            "اختر عدد النجوم عبر لوحة الأرقام أدناه، ثم اضغط زر التأكيد:\n\n"
            "📌 <b>الكمية المحددة:</b> <code>5</code> نجوم",
            reply_markup=get_number_pad_keyboard("5")
        )
        await callback_query.answer()

    @dp.callback_query(F.data.startswith("num_"))
    async def handle_number_pad(callback_query: types.CallbackQuery, state: FSMContext):
        action = callback_query.data.split("_")[1]
        data = await state.get_data()
        current = data.get("donation_amount", "5")

        if action.isdigit():
            if current == "5":
                current = action
            else:
                current += action
        elif action == "clear":
            current = "0"
        elif action == "cancel":
            await callback_query.message.edit_text("❌ تم إلغاء عملية التبرع.", reply_markup=get_main_keyboard())
            await state.clear()
            await callback_query.answer()
            return
        elif action == "confirm":
            amount = int(current or "1")
            await state.clear()
            await callback_query.message.edit_text(
                f"✅ <b>تم توليد الفاتورة بنجاح يا فخم!</b>\n\n"
                f"تتم عملية الدفع الآمن بقيمة <b>{amount}</b> نجمة (Telegram Stars) عبر تليجرام فوراً.",
                reply_markup=get_main_keyboard()
            )
            await bot.send_invoice(
                chat_id=callback_query.message.chat.id,
                title="تبرع لدعم منصة fokhm.com ⚡",
                description=f"مساهمة مالية بقيمة {amount} نجمة لدعم وتطوير خدمات التلغيم.",
                payload=f"donation_{callback_query.from_user.id}_{amount}",
                currency="XTR",
                prices=[types.LabeledPrice(label=f"دعم {amount} نجمة", amount=amount)]
            )
            await callback_query.answer()
            return

        await state.update_data(donation_amount=current)
        await callback_query.message.edit_text(
            f"⭐ <b>نظام الدعم والتبرع بالنجوم لمنصة fokhm.com</b>\n\n"
            f"اختر عدد النجوم عبر لوحة الأرقام أدناه، ثم اضغط زر التأكيد:\n\n"
            f"📌 <b>الكمية المحددة:</b> <code>{current}</code> نجوم",
            reply_markup=get_number_pad_keyboard(current)
        )
        await callback_query.answer()

    @dp.pre_checkout_query()
    async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    @dp.message(F.successful_payment)
    async def successful_payment(message: types.Message):
        user_id = message.from_user.id
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_vip = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        await message.answer("🎉 <b>تم استلام تبرعك بنجاح يا فخم!</b> شكراً لدعمك المستمر لمنصة fokhm.com ⚡ وتم ترقية حسابك إلى VIP.")

    @dp.callback_query(F.data == "my_account")
    async def callback_account(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        stats = get_user_stats(user_id)
        vip_status = "💎 عضو مميز (VIP)" if stats["vip"] or user_id == ADMIN_ID else "🛡 عضو عادي"
        await callback_query.answer()
        await callback_query.message.answer(f"🥷 <b>معلومات حسابك:</b>\n🆔 المعرّف: <code>{user_id}</code>\n⚡ الرتبة: {vip_status}\n👥 الدعوات: <b>{stats['referrals']}</b>\n🌐 المنصة: fokhm.com")

    @dp.callback_query(F.data == "invite_friends")
    async def callback_invite(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        bot_info = await bot.get_me()
        invite_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
        await callback_query.answer()
        await callback_query.message.answer(f"🔗 <b>نظام الدعوات:</b>\nشارك رابطك الخاص:\n<code>{invite_link}</code>")

    @dp.callback_query(F.data == "vip_section")
    async def callback_vip(callback_query: types.CallbackQuery):
        await callback_query.answer("💎 قسم VIP متاح عبر دعوة 5 أشخاص أو التبرع بالنجوم!", show_alert=True)

    @dp.callback_query(F.data == "help_section")
    async def callback_help(callback_query: types.CallbackQuery):
        await callback_query.answer("❓ للدعم الفني تواصل عبر موقعنا: fokhm.com", show_alert=True)

    @dp.callback_query()
    async def handle_other_callbacks(callback_query: types.CallbackQuery):
        await callback_query.answer()

    print("🤖 Aiogram 3 Production Bot for fokhm.com is running smoothly...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())

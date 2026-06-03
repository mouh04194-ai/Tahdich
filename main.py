import os
import json
import time
import re
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

# ================= FORCE SUBSCRIPTION CHANNELS =================
FORCE_CHANNEL_1 = "@mouhammed_ma"
FORCE_CHANNEL_1_LINK = "https://t.me/mouhammed_ma"
FORCE_CHANNEL_2 = "@Illegal_tools"
FORCE_CHANNEL_2_LINK = "https://t.me/Illegal_tools"

FORCE_SUB_MSG = (
    "📢 <b>𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗥𝗲𝗾𝘂𝗶𝗿𝗲𝗱</b>\n\n"
    "🚫 يجب الاشتراك في القنوات التالية لاستخدام البوت\n\n"
    "➊ <a href='{link1}'>القناة الأولى</a>\n"
    "➋ <a href='{link2}'>القناة الثانية</a>\n\n"
    "✅ بعد إكمال الاشتراك اضغط على زر التحقق"
)

# ================= SETTINGS FILE (للمالك) =================
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "check_cost": 5,          # عدد النقاط التي تخصم لكل فحص بطاقة
    "referral_reward": 5,     # النقاط التي يحصل عليها الداعي عند دعوة شخص جديد
    "referral_bonus": 10,     # النقاط الإضافية التي يحصل عليها المدعو الجديد (فوق الأساسية)
    "bot_active": True,       # حالة تشغيل البوت (True = يعمل، False = مقفل)
    "blocked_users": []       # قائمة معرفات المستخدمين المحظورين
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

def is_bot_active():
    return load_settings().get("bot_active", True)

def is_user_blocked(user_id):
    return str(user_id) in load_settings().get("blocked_users", [])

# ================= DB (مع نظام الدعوات والإعدادات) =================
CREDITS_FILE = "credits.json"
DEFAULT_CREDITS = 10  # الهدية الأساسية للمستخدم الجديد

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

def ensure_user(user_id, referrer_id=None):
    db = load_db()
    uid = str(user_id)
    if uid not in db:
        settings = load_settings()
        reward = settings.get("referral_reward", 5)
        bonus = settings.get("referral_bonus", 10)
        db[uid] = {
            "credits": DEFAULT_CREDITS,
            "invited_by": None,
            "invite_count": 0
        }
        if referrer_id and str(referrer_id) != uid:
            referrer = str(referrer_id)
            if referrer in db:
                # إضافة مكافأة للداعي حسب الإعدادات
                db[referrer]["credits"] = db[referrer].get("credits", 0) + reward
                db[referrer]["invite_count"] = db[referrer].get("invite_count", 0) + 1
                # إضافة مكافأة للمدعو الجديد
                db[uid]["credits"] += bonus
                db[uid]["invited_by"] = referrer
                try:
                    bot.send_message(int(referrer), f"🎉 <b>New Referral!</b>\n\n+{reward} Credits\nTotal Referrals: {db[referrer]['invite_count']}", parse_mode="HTML")
                except:
                    pass
        save_db(db)
    return db

def add_credits_to_user(user_id, amount):
    db = load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {"credits": 0, "invited_by": None, "invite_count": 0}
    db[uid]["credits"] = db[uid].get("credits", 0) + amount
    save_db(db)
    return db[uid]["credits"]

def spend_credit_or_block(message, cost=None):
    user_id = message.from_user.id
    if is_user_blocked(user_id):
        bot.reply_to(message, "🚫 You are blocked from using this bot.")
        return None
    if cost is None:
        cost = load_settings().get("check_cost", 5)
    db = ensure_user(user_id)
    uid = str(user_id)
    if db[uid]["credits"] < cost:
        bot.reply_to(message, f"❌ رصيدك غير كافٍ. تحتاج {cost} نقطة.\n💡 احصل على نقاط عبر /invite.")
        return None
    db[uid]["credits"] -= cost
    save_db(db)
    return db[uid]["credits"]

# ================= FORCE SUBSCRIPTION FUNCTIONS =================
def is_subscribed(user_id):
    def check_channel(channel):
        try:
            member = bot.get_chat_member(channel, user_id)
            return member.status in ["member", "administrator", "creator"]
        except Exception as e:
            print(f"⚠️ فشل التحقق من القناة {channel}: {e}")
            return False
    sub1 = check_channel(FORCE_CHANNEL_1)
    sub2 = check_channel(FORCE_CHANNEL_2)
    return sub1 and sub2

def send_force_sub_message(chat_id, user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("📢 اشترك في القناة 1", url=FORCE_CHANNEL_1_LINK)
    btn2 = InlineKeyboardButton("📢 اشترك في القناة 2", url=FORCE_CHANNEL_2_LINK)
    check_btn = InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data=f"check_sub_{user_id}")
    keyboard.add(btn1, btn2)
    keyboard.add(check_btn)
    text = FORCE_SUB_MSG.format(link1=FORCE_CHANNEL_1_LINK, link2=FORCE_CHANNEL_2_LINK)
    bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)

def subscription_required(func):
    def wrapper(message):
        user_id = message.from_user.id
        if is_user_blocked(user_id):
            bot.reply_to(message, "🚫 You are blocked.")
            return
        if not is_bot_active() and user_id not in ADMIN_IDS:
            bot.reply_to(message, "🔴 البوت في وضع الصيانة حالياً. يرجى المحاولة لاحقاً.")
            return
        if not is_subscribed(user_id):
            send_force_sub_message(message.chat.id, user_id)
            return
        return func(message)
    return wrapper

# ================= CALLBACK HANDLER للتحقق من الاشتراك =================
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
            parse_mode="HTML"
        )
        send_main_menu(call.message.chat.id, user_id)
    else:
        bot.answer_callback_query(call.id, "❌ لم يتم الاشتراك بعد، تأكد من الاشتراك في القناتين ثم اضغط تحقق.", show_alert=True)
        send_force_sub_message(call.message.chat.id, user_id)

# ================= القائمة الرئيسية (مع زر للمالك) =================
def send_main_menu(chat_id, user_id):
    db = ensure_user(user_id)
    credits = db[str(user_id)]["credits"]
    invite_count = db[str(user_id)].get("invite_count", 0)
    try:
        user = bot.get_chat(user_id)
        username = user.username or "NoUsername"
    except:
        username = "NoUsername"

    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_chk = InlineKeyboardButton("🛡️ Check Card", callback_data="cmd_chk")
    btn_invite = InlineKeyboardButton("🎁 Invite & Earn", callback_data="cmd_invite")
    btn_stats = InlineKeyboardButton("👤 My Stats", callback_data="cmd_stats")
    btn_support = InlineKeyboardButton("📞 Support", url="https://t.me/mouhamed_ma")
    keyboard.add(btn_chk, btn_invite)
    keyboard.add(btn_stats, btn_support)
    
    # إضافة زر لوحة التحكم للمالكين فقط
    if user_id in ADMIN_IDS:
        btn_admin = InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")
        keyboard.add(btn_admin)

    text = (
        f"✨ <b>Welcome back, @{username}!</b> ✨\n\n"
        f"💎 <b>Credits:</b> <code>{credits}</code>\n"
        f"👥 <b>Referrals:</b> <code>{invite_count}</code>\n\n"
        f"🔽 <b>Use the buttons below:</b>"
    )
    bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")

# ================= قائمة الدعوات =================
def send_invite_menu(chat_id, user_id, edit_msg_id=None):
    db = ensure_user(user_id)
    invite_count = db[str(user_id)].get("invite_count", 0)
    bot_username = bot.get_me().username
    invite_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    settings = load_settings()
    reward = settings.get("referral_reward", 5)
    bonus = settings.get("referral_bonus", 10)
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn_link = InlineKeyboardButton("🔗 Copy Invite Link", callback_data="copy_link")
    btn_back = InlineKeyboardButton("◀️ Back to Main Menu", callback_data="main_menu")
    keyboard.add(btn_link, btn_back)
    
    text = (
        "🎁 <b>Invite & Earn System</b>\n\n"
        "➡️ <b>Your Invite Link:</b>\n"
        f"<code>{invite_link}</code>\n\n"
        "📌 <b>How it works?</b>\n"
        f"• Each friend who joins using your link gives you <b>+{reward} Credits</b>.\n"
        f"• Your friend gets <b>+{bonus} Bonus Credits</b> on signup.\n\n"
        f"👥 <b>Total Referrals:</b> <code>{invite_count}</code>\n\n"
        "🔗 <i>Share your link and earn unlimited credits!</i>"
    )
    if edit_msg_id:
        bot.edit_message_text(text, chat_id, edit_msg_id, reply_markup=keyboard, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")

# ================= عرض الإحصائيات =================
def send_my_stats(chat_id, user_id, edit_msg_id=None):
    db = ensure_user(user_id)
    credits = db[str(user_id)]["credits"]
    invite_count = db[str(user_id)].get("invite_count", 0)
    invited_by = db[str(user_id)].get("invited_by")
    
    invited_by_text = "No one"
    if invited_by:
        try:
            inviter = bot.get_chat(int(invited_by))
            inviter_name = f"@{inviter.username}" if inviter.username else invited_by
            invited_by_text = inviter_name
        except:
            invited_by_text = invited_by
    
    keyboard = InlineKeyboardMarkup()
    btn_back = InlineKeyboardButton("◀️ Back to Main Menu", callback_data="main_menu")
    keyboard.add(btn_back)
    
    text = (
        "📊 <b>Your Statistics</b>\n\n"
        f"💎 <b>Credits Balance:</b> <code>{credits}</code>\n"
        f"👥 <b>Referrals Count:</b> <code>{invite_count}</code>\n"
        f"🔗 <b>Invited By:</b> {invited_by_text}\n\n"
        "💡 <i>Invite friends to earn more credits!</i>"
    )
    if edit_msg_id:
        bot.edit_message_text(text, chat_id, edit_msg_id, reply_markup=keyboard, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")

# ================= لوحة تحكم المالك =================
def send_admin_panel(chat_id, user_id, edit_msg_id=None):
    if user_id not in ADMIN_IDS:
        return
    settings = load_settings()
    bot_active = settings.get("bot_active", True)
    check_cost = settings.get("check_cost", 5)
    referral_reward = settings.get("referral_reward", 5)
    referral_bonus = settings.get("referral_bonus", 10)
    blocked_count = len(settings.get("blocked_users", []))
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_toggle = InlineKeyboardButton("🔓 Activate" if not bot_active else "🔒 Deactivate", callback_data="admin_toggle")
    btn_set_cost = InlineKeyboardButton(f"💰 Check Cost: {check_cost}", callback_data="admin_set_cost")
    btn_set_reward = InlineKeyboardButton(f"🎁 Referral Reward: {referral_reward}", callback_data="admin_set_reward")
    btn_set_bonus = InlineKeyboardButton(f"✨ Referral Bonus: {referral_bonus}", callback_data="admin_set_bonus")
    btn_blocked = InlineKeyboardButton(f"🚫 Blocked Users: {blocked_count}", callback_data="admin_blocked_list")
    btn_back = InlineKeyboardButton("◀️ Back to Main Menu", callback_data="main_menu")
    keyboard.add(btn_toggle, btn_set_cost)
    keyboard.add(btn_set_reward, btn_set_bonus)
    keyboard.add(btn_blocked, btn_back)
    
    text = (
        "⚙️ <b>Admin Control Panel</b>\n\n"
        f"📌 Bot Status: {'🟢 Active' if bot_active else '🔴 Inactive'}\n"
        f"💳 Check Cost: <code>{check_cost}</code> credits\n"
        f"👥 Referral Reward: <code>{referral_reward}</code> credits\n"
        f"🎁 Referral Bonus: <code>{referral_bonus}</code> credits\n"
        f"🚫 Blocked Users: <code>{blocked_count}</code>\n\n"
        "Click any button to modify."
    )
    if edit_msg_id:
        bot.edit_message_text(text, chat_id, edit_msg_id, reply_markup=keyboard, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")

# ================= معالجة أزرار المالك =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callback(call: CallbackQuery):
    user_id = call.from_user.id
    if user_id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "🚫 You are not an admin.", show_alert=True)
        return
    action = call.data.split("_")[1]
    settings = load_settings()
    
    if action == "toggle":
        settings["bot_active"] = not settings.get("bot_active", True)
        save_settings(settings)
        bot.answer_callback_query(call.id, f"✅ Bot is now {'ACTIVE' if settings['bot_active'] else 'INACTIVE'}.", show_alert=True)
        send_admin_panel(call.message.chat.id, user_id, call.message.message_id)
    elif action == "set":
        sub = call.data.split("_")[2]  # cost, reward, bonus
        bot.answer_callback_query(call.id, f"Send new value for {sub} as a number.", show_alert=False)
        # سنستخدم next_step_handler لتلقي القيمة
        msg = bot.send_message(call.message.chat.id, f"✏️ Please send the new value for <b>{sub}</b>:\n(integer number)", parse_mode="HTML")
        bot.register_next_step_handler(msg, process_admin_setting, sub, call.message.chat.id, call.message.message_id)
    elif action == "blocked":
        # عرض قائمة المحظورين مع خيارات إضافة/إزالة
        blocked = settings.get("blocked_users", [])
        if not blocked:
            bot.answer_callback_query(call.id, "📭 No blocked users.", show_alert=True)
            return
        keyboard = InlineKeyboardMarkup()
        for uid in blocked:
            btn = InlineKeyboardButton(f"Unblock {uid}", callback_data=f"admin_unblock_{uid}")
            keyboard.add(btn)
        btn_back = InlineKeyboardButton("◀️ Back", callback_data="admin_panel")
        keyboard.add(btn_back)
        text = "🚫 <b>Blocked Users</b>\n\nClick on a user to unblock:"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode="HTML")
        bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_unblock_"))
def admin_unblock_callback(call: CallbackQuery):
    user_id = call.from_user.id
    if user_id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "🚫 Not admin.", show_alert=True)
        return
    target = call.data.split("_")[2]
    settings = load_settings()
    if target in settings.get("blocked_users", []):
        settings["blocked_users"].remove(target)
        save_settings(settings)
        bot.answer_callback_query(call.id, f"✅ User {target} unblocked.", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "User not found in block list.", show_alert=True)
    # العودة إلى لوحة التحكم
    send_admin_panel(call.message.chat.id, user_id, call.message.message_id)

def process_admin_setting(message, setting_key, chat_id, original_msg_id):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        new_value = int(message.text.strip())
        if new_value < 0:
            raise ValueError
        settings = load_settings()
        if setting_key == "cost":
            settings["check_cost"] = new_value
        elif setting_key == "reward":
            settings["referral_reward"] = new_value
        elif setting_key == "bonus":
            settings["referral_bonus"] = new_value
        else:
            return
        save_settings(settings)
        bot.send_message(chat_id, f"✅ {setting_key} updated to {new_value}.")
    except:
        bot.send_message(chat_id, "❌ Invalid number. Operation cancelled.")
    send_admin_panel(chat_id, message.from_user.id, original_msg_id)

# ================= معالجة أزرار القائمة الرئيسية =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("cmd_"))
def menu_callback(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if is_user_blocked(user_id):
        bot.answer_callback_query(call.id, "🚫 You are blocked.", show_alert=True)
        return
    if not is_bot_active() and user_id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "🔴 Bot is under maintenance.", show_alert=True)
        return
    if not is_subscribed(user_id):
        bot.answer_callback_query(call.id, "❌ يرجى الاشتراك في القناتين أولاً", show_alert=True)
        send_force_sub_message(chat_id, user_id)
        return
    
    cmd = call.data.split("_")[1]
    
    if cmd == "chk":
        msg = bot.send_message(
            chat_id,
            "<blockquote>💳 <b>إرسال بيانات البطاقة</b>\n\n"
            "📌 يرجى إرسال البطاقة بالتنسيق التالي:\n"
            "<code>رقم البطاقة|الشهر|السنة|رمز الأمان</code>\n\n"
            "📝 مثال:\n"
            "<code>XXXXXXXXXXXXXXXX|12|26|123</code>\n\n"
            "⚠️ لا تشارك هذه البيانات مع أي شخص آخر.</blockquote>",
            parse_mode="HTML"
        )
        bot.register_next_step_handler(msg, process_cc_input, user_id)
        bot.answer_callback_query(call.id)
    elif cmd == "invite":
        send_invite_menu(chat_id, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
    elif cmd == "stats":
        send_my_stats(chat_id, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
    elif cmd == "support":
        bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def admin_panel_callback(call: CallbackQuery):
    user_id = call.from_user.id
    if user_id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "🚫 Not admin.", show_alert=True)
        return
    send_admin_panel(call.message.chat.id, user_id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def back_to_main(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if not is_subscribed(user_id):
        send_force_sub_message(chat_id, user_id)
    else:
        send_main_menu(chat_id, user_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "copy_link")
def copy_invite_link(call: CallbackQuery):
    bot_username = bot.get_me().username
    user_id = call.from_user.id
    link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    bot.answer_callback_query(call.id, f"🔗 الرابط: {link}\n\nيمكنك نسخه الآن.", show_alert=True)

def process_cc_input(message, user_id):
    if message.from_user.id != user_id:
        return
    message.text = f"/chk {message.text.strip()}"
    check_card(message)

# ================= الأوامر النصية =================
@bot.message_handler(commands=["start"])
def start_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if is_user_blocked(user_id):
        bot.reply_to(message, "🚫 You are blocked.")
        return
    referrer_id = None
    text = message.text.strip()
    match = re.search(r'ref_(\d+)', text)
    if match:
        referrer_id = int(match.group(1))
    ensure_user(user_id, referrer_id)
    if not is_subscribed(user_id):
        send_force_sub_message(chat_id, user_id)
    else:
        send_main_menu(chat_id, user_id)

@bot.message_handler(commands=["invite"])
@subscription_required
def invite_cmd(message):
    send_invite_menu(message.chat.id, message.from_user.id)

@bot.message_handler(commands=["mystats", "info"])
@subscription_required
def stats_cmd(message):
    send_my_stats(message.chat.id, message.from_user.id)

@bot.message_handler(commands=["request"])
@subscription_required
def request_cmd(message):
    user_id = message.from_user.id
    try:
        username = bot.get_chat(user_id).username or "NoUsername"
    except:
        username = "NoUsername"
    bot.reply_to(message, "✅ تم إرسال طلبك إلى المدير. يمكنك أيضاً كسب نقاط عبر /invite.")
    for admin_id in ADMIN_IDS:
        bot.send_message(
            admin_id,
            f"📩 <b>طلب رصيد جديد</b>\n\nالمستخدم: @{username}\nالرقم: <code>{user_id}</code>",
            parse_mode="HTML"
        )

@bot.message_handler(commands=["addcredits"])
def add_credits_admin(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not admin.")
        return
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "Usage:\n/addcredits <user_id> <amount>")
        return
    target_id = args[1]
    try:
        amount = int(args[2])
    except:
        bot.reply_to(message, "Amount must be a number.")
        return
    if amount <= 0:
        bot.reply_to(message, "Amount must be > 0.")
        return
    new_balance = add_credits_to_user(target_id, amount)
    bot.reply_to(message, f"✅ Credits Added\nUser ID: {target_id}\nAdded: {amount}\nNew Balance: {new_balance}")
    try:
        bot.send_message(
            int(target_id),
            f"🎉 <b>Credits Added!</b>\n+{amount}\nBalance: <b>{new_balance}</b>",
            parse_mode="HTML"
        )
    except:
        pass

# ================= CHK COMMAND =================
@bot.message_handler(commands=['chk'])
@subscription_required
def check_card(message):
    msg_id = None
    try:
        remaining = spend_credit_or_block(message)  # يستخدم السعر من الإعدادات
        if remaining is None:
            return

        text = message.text or ""
        parts = text.split('/chk', 1)
        cc = parts[1].strip() if len(parts) > 1 else ""

        username = message.from_user.username or "NoUsername"

        msg = bot.reply_to(message, "🔄 جاري فحص البطاقة...")
        msg_id = msg.message_id
        start_time = time.time()

        if not cc:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text="❌ التنسيق غير صحيح. استخدم: cc|mm|yy|cvv",
                parse_mode="HTML"
            )
            return

        try:
            last = str(Tele(cc))
        except:
            last = 'API Error'

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
                text="⚠️ حدث خطأ أثناء معالجة طلبك."
            )
        print("CHK ERROR:", e)

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

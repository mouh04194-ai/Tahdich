import os
import json
import time
import re
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from gatet import Tele
from hit_sender import send

# ================= ADMIN الأساسي =================
MASTER_ADMIN_IDS = [6891530912]  # @mouhamed_ma

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

# ================= ملف الأدمن الإضافيين =================
ADMINS_FILE = "extra_admins.json"

def load_extra_admins():
    if not os.path.exists(ADMINS_FILE):
        return []
    try:
        with open(ADMINS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_extra_admins(admins):
    with open(ADMINS_FILE, "w") as f:
        json.dump(admins, f, indent=2)

def is_admin(user_id):
    return user_id in MASTER_ADMIN_IDS or user_id in load_extra_admins()

# ================= SETTINGS FILE =================
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "check_cost": 5,
    "referral_reward": 5,
    "referral_bonus": 10,
    "bot_active": True,
    "blocked_users": []
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

# ================= DB =================
CREDITS_FILE = "credits.json"
DEFAULT_CREDITS = 10

def load_db():
    if not os.path.exists(CREDITS_FILE):
        return {}
    try:
        with open(CREDITS_FILE, "r") as f:
            return json.load(f)
    except:
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
                db[referrer]["credits"] = db[referrer].get("credits", 0) + reward
                db[referrer]["invite_count"] = db[referrer].get("invite_count", 0) + 1
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
        bot.reply_to(message, "🚫 You are blocked.")
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

# ================= اشتراك إجباري =================
def is_subscribed(user_id):
    def check_channel(channel):
        try:
            member = bot.get_chat_member(channel, user_id)
            return member.status in ["member", "administrator", "creator"]
        except:
            return False
    return check_channel(FORCE_CHANNEL_1) and check_channel(FORCE_CHANNEL_2)

def send_force_sub_message(chat_id, user_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("📢 اشترك في القناة 1", url=FORCE_CHANNEL_1_LINK)
    btn2 = InlineKeyboardButton("📢 اشترك في القناة 2", url=FORCE_CHANNEL_2_LINK)
    check_btn = InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data=f"check_sub_{user_id}")
    keyboard.add(btn1, btn2, check_btn)
    text = FORCE_SUB_MSG.format(link1=FORCE_CHANNEL_1_LINK, link2=FORCE_CHANNEL_2_LINK)
    bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)

def subscription_required(func):
    def wrapper(message):
        user_id = message.from_user.id
        if is_user_blocked(user_id):
            bot.reply_to(message, "🚫 You are blocked.")
            return
        if not is_bot_active() and not is_admin(user_id):
            bot.reply_to(message, "🔴 البوت في وضع الصيانة حالياً.")
            return
        if not is_subscribed(user_id):
            send_force_sub_message(message.chat.id, user_id)
            return
        return func(message)
    return wrapper

# ================= القائمة الرئيسية والأزرار =================
def send_main_menu(chat_id, user_id):
    db = ensure_user(user_id)
    credits = db[str(user_id)]["credits"]
    invite_count = db[str(user_id)].get("invite_count", 0)
    try:
        username = bot.get_chat(user_id).username or "NoUsername"
    except:
        username = "NoUsername"

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🛡️ Check Card", callback_data="cmd_chk"),
        InlineKeyboardButton("🎁 Invite & Earn", callback_data="cmd_invite")
    )
    keyboard.add(
        InlineKeyboardButton("👤 My Stats", callback_data="cmd_stats"),
        InlineKeyboardButton("📞 Support", url="https://t.me/mouhamed_ma")
    )
    if is_admin(user_id):
        keyboard.add(InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel"))

    text = (f"✨ <b>Welcome back, @{username}!</b> ✨\n\n"
            f"💎 <b>Credits:</b> <code>{credits}</code>\n"
            f"👥 <b>Referrals:</b> <code>{invite_count}</code>\n\n"
            f"🔽 <b>Use the buttons below:</b>")
    bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")

def send_invite_menu(chat_id, user_id, edit_msg_id=None):
    db = ensure_user(user_id)
    invite_count = db[str(user_id)].get("invite_count", 0)
    bot_username = bot.get_me().username
    invite_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    settings = load_settings()
    reward = settings.get("referral_reward", 5)
    bonus = settings.get("referral_bonus", 10)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("🔗 Copy Invite Link", callback_data="copy_link"),
        InlineKeyboardButton("◀️ Back", callback_data="main_menu")
    )
    text = (f"🎁 <b>Invite & Earn System</b>\n\n"
            f"➡️ <b>Your Invite Link:</b>\n<code>{invite_link}</code>\n\n"
            f"📌 <b>How it works?</b>\n• Each friend joins → you get <b>+{reward}</b>\n• Your friend gets <b>+{bonus}</b>\n\n"
            f"👥 <b>Total Referrals:</b> <code>{invite_count}</code>")
    if edit_msg_id:
        bot.edit_message_text(text, chat_id, edit_msg_id, reply_markup=keyboard, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")

def send_my_stats(chat_id, user_id, edit_msg_id=None):
    db = ensure_user(user_id)
    credits = db[str(user_id)]["credits"]
    invite_count = db[str(user_id)].get("invite_count", 0)
    invited_by = db[str(user_id)].get("invited_by")
    invited_by_text = "No one"
    if invited_by:
        try:
            inviter = bot.get_chat(int(invited_by))
            invited_by_text = f"@{inviter.username}" if inviter.username else invited_by
        except:
            invited_by_text = invited_by
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("◀️ Back", callback_data="main_menu"))
    text = (f"📊 <b>Your Statistics</b>\n\n"
            f"💎 <b>Credits Balance:</b> <code>{credits}</code>\n"
            f"👥 <b>Referrals Count:</b> <code>{invite_count}</code>\n"
            f"🔗 <b>Invited By:</b> {invited_by_text}")
    if edit_msg_id:
        bot.edit_message_text(text, chat_id, edit_msg_id, reply_markup=keyboard, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")

# ================= لوحة تحكم المالك =================
def send_admin_panel(chat_id, user_id, edit_msg_id=None):
    if not is_admin(user_id):
        return
    settings = load_settings()
    extra_admins = load_extra_admins()
    text = (f"⚙️ <b>Admin Control Panel</b>\n\n"
            f"📌 Bot Status: {'🟢 Active' if settings['bot_active'] else '🔴 Inactive'}\n"
            f"💰 Check Cost: <code>{settings['check_cost']}</code>\n"
            f"🎁 Referral Reward: <code>{settings['referral_reward']}</code>\n"
            f"✨ Referral Bonus: <code>{settings['referral_bonus']}</code>\n"
            f"🚫 Blocked Users: <code>{len(settings['blocked_users'])}</code>\n"
            f"👥 Extra Admins: <code>{len(extra_admins)}</code>\n\n"
            f"Click a button to manage.")
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔓 Toggle Bot" if settings['bot_active'] else "🔒 Toggle Bot", callback_data="admin_toggle"),
        InlineKeyboardButton("💰 Set Check Cost", callback_data="admin_set_cost")
    )
    keyboard.add(
        InlineKeyboardButton("🎁 Set Referral Reward", callback_data="admin_set_reward"),
        InlineKeyboardButton("✨ Set Referral Bonus", callback_data="admin_set_bonus")
    )
    keyboard.add(
        InlineKeyboardButton("🚫 Manage Blocks", callback_data="admin_blocked_list"),
        InlineKeyboardButton("👥 Manage Admins", callback_data="admin_admins_list")
    )
    keyboard.add(
        InlineKeyboardButton("💸 Send Credits", callback_data="admin_send_credits"),
        InlineKeyboardButton("◀️ Back to Main Menu", callback_data="main_menu")
    )
    if edit_msg_id:
        bot.edit_message_text(text, chat_id, edit_msg_id, reply_markup=keyboard, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="HTML")

# ================= إدارة الأدمن =================
def send_admins_list(chat_id, user_id, edit_msg_id):
    if not is_admin(user_id):
        return
    extra = load_extra_admins()
    keyboard = InlineKeyboardMarkup(row_width=1)
    for aid in extra:
        keyboard.add(InlineKeyboardButton(f"❌ Remove {aid}", callback_data=f"admin_remove_admin_{aid}"))
    keyboard.add(InlineKeyboardButton("➕ Add Admin", callback_data="admin_add_admin"))
    keyboard.add(InlineKeyboardButton("◀️ Back", callback_data="admin_panel"))
    text = f"👥 <b>Extra Admins</b> (total {len(extra)}):\n" + ("\n".join([f"• {a}" for a in extra]) if extra else "No extra admins.")
    bot.edit_message_text(text, chat_id, edit_msg_id, reply_markup=keyboard, parse_mode="HTML")

def send_add_admin_prompt(chat_id, user_id, original_msg_id):
    msg = bot.send_message(chat_id, "✏️ Send the user ID of the new admin (integer):")
    bot.register_next_step_handler(msg, process_add_admin, chat_id, original_msg_id)

def process_add_admin(message, chat_id, original_msg_id):
    if not is_admin(message.from_user.id):
        return
    try:
        new_admin = int(message.text.strip())
        if new_admin in MASTER_ADMIN_IDS:
            bot.send_message(chat_id, "❌ Cannot remove or add master admin.")
            send_admin_panel(chat_id, message.from_user.id, original_msg_id)
            return
        extra = load_extra_admins()
        if new_admin in extra:
            bot.send_message(chat_id, "⚠️ Already an extra admin.")
        else:
            extra.append(new_admin)
            save_extra_admins(extra)
            bot.send_message(chat_id, f"✅ User {new_admin} added as admin.")
    except:
        bot.send_message(chat_id, "❌ Invalid ID.")
    send_admin_panel(chat_id, message.from_user.id, original_msg_id)

# ================= إرسال نقاط =================
def send_credits_prompt(chat_id, user_id, original_msg_id):
    msg = bot.send_message(chat_id, "✏️ Send the user ID and amount separated by space:\nExample: `123456789 50`", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_send_credits, chat_id, original_msg_id)

def process_send_credits(message, chat_id, original_msg_id):
    if not is_admin(message.from_user.id):
        return
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            raise ValueError
        target_id = int(parts[0])
        amount = int(parts[1])
        if amount <= 0:
            raise ValueError
        new_balance = add_credits_to_user(target_id, amount)
        bot.send_message(chat_id, f"✅ Added {amount} credits to user {target_id}. New balance: {new_balance}")
        try:
            bot.send_message(target_id, f"🎉 <b>Credits Added!</b>\n+{amount}\nBalance: <b>{new_balance}</b>", parse_mode="HTML")
        except:
            pass
    except:
        bot.send_message(chat_id, "❌ Invalid format. Use: `user_id amount`", parse_mode="Markdown")
    send_admin_panel(chat_id, message.from_user.id, original_msg_id)

# ================= إدارة الحظر =================
def blocked_list(call):
    settings = load_settings()
    blocked = settings.get("blocked_users", [])
    keyboard = InlineKeyboardMarkup(row_width=1)
    for uid in blocked:
        keyboard.add(InlineKeyboardButton(f"Unblock {uid}", callback_data=f"admin_unblock_{uid}"))
    keyboard.add(InlineKeyboardButton("➕ Block User", callback_data="admin_add_block"))
    keyboard.add(InlineKeyboardButton("◀️ Back", callback_data="admin_panel"))
    text = f"🚫 <b>Blocked Users</b> ({len(blocked)}):\n" + ("\n".join(blocked) if blocked else "No blocked users.")
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode="HTML")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_unblock_"))
def unblock_callback(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "Not admin.", show_alert=True)
        return
    target = call.data.split("_")[2]
    settings = load_settings()
    if target in settings["blocked_users"]:
        settings["blocked_users"].remove(target)
        save_settings(settings)
        bot.answer_callback_query(call.id, f"User {target} unblocked.", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "Not blocked.", show_alert=True)
    blocked_list(call)

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_block")
def add_block_prompt(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    msg = bot.send_message(call.message.chat.id, "✏️ Send user ID to block:")
    bot.register_next_step_handler(msg, process_add_block, call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

def process_add_block(message, chat_id, original_msg_id):
    if not is_admin(message.from_user.id):
        return
    try:
        uid = str(int(message.text.strip()))
        settings = load_settings()
        if uid not in settings["blocked_users"]:
            settings["blocked_users"].append(uid)
            save_settings(settings)
            bot.send_message(chat_id, f"✅ User {uid} blocked.")
        else:
            bot.send_message(chat_id, "Already blocked.")
    except:
        bot.send_message(chat_id, "Invalid user ID.")
    send_admin_panel(chat_id, message.from_user.id, original_msg_id)

# ================= معالجات الأزرار الشاملة (تم إصلاح admin_panel) =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callback(call: CallbackQuery):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "🚫 Not admin.", show_alert=True)
        return
    data = call.data.split("_")
    action = data[1]
    settings = load_settings()

    if action == "toggle":
        settings["bot_active"] = not settings["bot_active"]
        save_settings(settings)
        bot.answer_callback_query(call.id, f"Bot {'ACTIVE' if settings['bot_active'] else 'INACTIVE'}.", show_alert=True)
        send_admin_panel(call.message.chat.id, user_id, call.message.message_id)
    elif action == "set":
        key = data[2]
        bot.answer_callback_query(call.id, f"Send new value for {key}:", show_alert=False)
        msg = bot.send_message(call.message.chat.id, f"✏️ Send new <b>{key}</b> (integer):", parse_mode="HTML")
        bot.register_next_step_handler(msg, process_admin_setting, key, call.message.chat.id, call.message.message_id)
    elif action == "panel":  # ✅ تمت إضافة هذا الشرط لمعالجة زر Admin Panel
        send_admin_panel(call.message.chat.id, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
    elif action == "blocked":
        blocked_list(call)
    elif action == "admins":
        send_admins_list(call.message.chat.id, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
    elif action == "send":
        send_credits_prompt(call.message.chat.id, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
    elif action == "add":
        send_add_admin_prompt(call.message.chat.id, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
    elif action == "remove":
        target = int(data[3])
        extra = load_extra_admins()
        if target in extra:
            extra.remove(target)
            save_extra_admins(extra)
            bot.answer_callback_query(call.id, f"Admin {target} removed.", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Not found.", show_alert=True)
        send_admins_list(call.message.chat.id, user_id, call.message.message_id)

def process_admin_setting(message, setting_key, chat_id, original_msg_id):
    if not is_admin(message.from_user.id):
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
        bot.send_message(chat_id, "❌ Invalid number.")
    send_admin_panel(chat_id, message.from_user.id, original_msg_id)

# ================= أزرار القائمة الرئيسية =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("cmd_"))
def menu_callback(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if is_user_blocked(user_id):
        bot.answer_callback_query(call.id, "🚫 You are blocked.", show_alert=True)
        return
    if not is_bot_active() and not is_admin(user_id):
        bot.answer_callback_query(call.id, "🔴 Bot is under maintenance.", show_alert=True)
        return
    if not is_subscribed(user_id):
        bot.answer_callback_query(call.id, "❌ يرجى الاشتراك في القناتين أولاً", show_alert=True)
        send_force_sub_message(chat_id, user_id)
        return
    cmd = call.data.split("_")[1]
    if cmd == "chk":
        msg = bot.send_message(chat_id, "<blockquote>💳 <b>إرسال بيانات البطاقة</b>\n\n📌 التنسيق:\n<code>رقم البطاقة|الشهر|السنة|رمز الأمان</code>\n\n📝 مثال:\n<code>XXXXXXXXXXXXXXXX|12|26|123</code>\n\n⚠️ لا تشارك هذه البيانات مع أي شخص آخر.</blockquote>", parse_mode="HTML")
        bot.register_next_step_handler(msg, process_cc_input, user_id)
        bot.answer_callback_query(call.id)
    elif cmd == "invite":
        send_invite_menu(chat_id, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
    elif cmd == "stats":
        send_my_stats(chat_id, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)

# ================= معالج منفصل لـ admin_panel لم يعد ضرورياً (تم دمجه في admin_callback) =================
# (تم التعليق عليه أو إزالته لمنع التداخل)
# @bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
# def admin_panel_callback(call: CallbackQuery):
#     ...

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
    link = f"https://t.me/{bot_username}?start=ref_{call.from_user.id}"
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
    match = re.search(r'ref_(\d+)', message.text.strip())
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
    username = bot.get_chat(user_id).username or "NoUsername"
    bot.reply_to(message, "✅ تم إرسال طلبك إلى المدير.")
    for admin_id in MASTER_ADMIN_IDS + load_extra_admins():
        bot.send_message(admin_id, f"📩 <b>طلب رصيد جديد</b>\n\nالمستخدم: @{username}\nالرقم: <code>{user_id}</code>", parse_mode="HTML")

# ================= أمر CHK =================
@bot.message_handler(commands=['chk'])
@subscription_required
def check_card(message):
    msg_id = None
    try:
        remaining = spend_credit_or_block(message)
        if remaining is None:
            return
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "❌ التنسيق غير صحيح. استخدم: /chk cc|mm|yy|cvv")
            return
        cc = parts[1].strip()
        if not cc or '|' not in cc:
            bot.reply_to(message, "❌ التنسيق غير صحيح. استخدم: cc|mm|yy|cvv")
            return
        username = message.from_user.username or "NoUsername"
        msg = bot.reply_to(message, "🔄 جاري فحص البطاقة...")
        msg_id = msg.message_id
        start_time = time.time()
        try:
            last = str(Tele(cc))
        except Exception as e:
            print("Tele error:", e)
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
        bot.edit_message_text(send_response, chat_id=message.chat.id, message_id=msg_id, parse_mode="HTML")
    except Exception as e:
        print("CHK ERROR:", e)
        if msg_id:
            bot.edit_message_text("⚠️ حدث خطأ أثناء معالجة طلبك.", chat_id=message.chat.id, message_id=msg_id)
        else:
            bot.reply_to(message, "⚠️ حدث خطأ.")

def log_charged_only(message, result_text, full_message):
    try:
        t = (result_text or "").lower()
        if any(x in t for x in ("charged", "𝐂𝐡𝐚𝐫𝐠𝐞𝐝".lower(), "donation successful")):
            bot.send_message(LOG_CHANNEL, full_message, parse_mode="HTML", disable_web_page_preview=True)
            print("✅ CHARGED LOG SENT")
    except Exception as e:
        print("CHARGED LOG ERROR:", e)

# ================= بدء البوت =================
if __name__ == "__main__":
    print("Bot started...")
    bot.infinity_polling(timeout=25, long_polling_timeout=25)


#mouhamed_ma
import requests
import random

def escape_html(s):
    if s is None:
        return ""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))

def random_email():
    return f"momo{random.randint(1000,9999)}@gmail.com"

def send(cc, last, username, time_taken, remaining):
    ii = (cc or "")[:6]
    cents = random.randint(50, 99)

    bank = "Unknown"
    country = "Unknown"
    emj = "🏳️"

    try:
        r = requests.get(f"https://bins.antipublic.cc/bins/{ii}", timeout=10)
        r.raise_for_status()
        data = r.json()
        bank = data.get("bank", bank)
        country = data.get("country", country)
        emj = data.get("country_flag", emj)
    except Exception as e:
        print("BIN API ERROR:", e)

    # تحديد الأيقونة حسب النتيجة
    u = (last or "").upper()
    if any(x in u for x in ("LIVE", "APPROVED", "CHARG")):
        icon = "🟢"
        status_text = "LIVE ✅"
    elif any(x in u for x in ("DECLINED", "DEAD")):
        icon = "🔴"
        status_text = "DECLINED ❌"
    else:
        icon = "🟡"
        status_text = "UNKNOWN ⚠️"

    # تهريب النصوص لأمان HTML
    cc_e = escape_html(cc)
    last_e = escape_html(last)
    bank_e = escape_html(bank)
    country_e = escape_html(country)
    user_e = escape_html(username or "NoUsername")
    taken_e = escape_html(time_taken)
    email_e = escape_html(random_email())
    remaining_e = escape_html(remaining)

    # تنسيق الرسالة النهائية (محاكاة شكل الصورة + اقتباسات)
    msg = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔷 <b>𝐌𝐎𝐔𝐇𝐀𝐌𝐄𝐃</b> 🔷\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        f"✨ <b>𝗥𝗘𝗦𝗨𝗟𝗧</b> ➜ {icon} {status_text}\n"
        f"💸 <b>𝗔𝗠𝗢𝗨𝗡𝗧</b> ➜ <code>0.{cents:02d}$</code>\n"
        f"⏱ <b>𝗧𝗜𝗠𝗘</b> ➜ <code>{taken_e} s</code>\n"
        f"📧 <b>𝗘𝗠𝗔𝗜𝗟</b> ➜ <code>{email_e}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "💳 <b>𝗖𝗔𝗥𝗗 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡</b>\n"
        f"<blockquote><code>{cc_e}</code></blockquote>\n\n"

        "🏦 <b>𝗕𝗜𝗡 𝗗𝗘𝗧𝗔𝗜𝗟𝗦</b>\n"
        f"<blockquote>"
        f"🏛 𝗕𝗮𝗻𝗸 ➜ {bank_e}\n"
        f"🌍 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ➜ {country_e} {emj}\n"
        f"🔢 𝗕𝗜𝗡 ➜ {escape_html(ii)}"
        f"</blockquote>\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>𝗨𝗦𝗘𝗥</b> ➜ @{user_e}\n"
        f"⭐ <b>𝗦𝗧𝗔𝗧𝗨𝗦</b> ➜ PREMIUM\n"
        f"💎 <b>𝗖𝗥𝗘𝗗𝗜𝗧𝗦</b> ➜ <code>{remaining_e}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🐱 @mouhamed_ma"
    )
    return msg
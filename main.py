TOKEN = "8512398866:AAGzlS3dcEFZh71iu4n5ZyI8dxa-DdjZZcY"

bot = telebot.TeleBot(TOKEN)

# دیتابیس موقت در حافظه برای ذخیره اطلاعات کاربران و وضعیت چت
users_profile = {}  # {user_id: {'name': '', 'age': '', 'province': '', 'status': ''}}
online_queue = []   # لیست کاربران در صف انتظار برای چت تصادفی
active_chats = {}   # {user_id: partner_id}

# شروع کار با ربات
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.chat.id
    
    # اگر کاربر قبلاً ثبت نام نکرده باشد، فرآیند ثبت‌نام شروع می‌شود
    if user_id not in users_profile:
        users_profile[user_id] = {'name': '', 'age': '', 'province': '', 'status': 'register_name'}
        bot.send_message(user_id, "✨ به ربات چت ناشناس خوش آمدید!\n\nبرای شروع، لطفاً نام یا نام مستعار خود را وارد کنید:")
    else:
        show_main_menu(user_id)

# مدیریت فرآیند ثبت‌نام و چت ناشناس
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.chat.id
    text = message.text

    # بررسی ثبت‌نام - گام اول: دریافت نام
    if user_id in users_profile and users_profile[user_id]['status'] == 'register_name':
        users_profile[user_id]['name'] = text
        users_profile[user_id]['status'] = 'register_age'
        bot.send_message(user_id, "🎯 عالیه! حالا لطفاً سن خود را به عدد وارد کنید (مثال: 22):")
        return

    # بررسی ثبت‌نام - گام دوم: دریافت سن
    if user_id in users_profile and users_profile[user_id]['status'] == 'register_age':
        if not text.isdigit():
            bot.send_message(user_id, "⚠️ لطفاً فقط عدد انگلیسی یا دیجیتال بفرستید:")
            return
        users_profile[user_id]['age'] = text
        users_profile[user_id]['status'] = 'register_province'
        bot.send_message(user_id, "📍 لطفاً نام ولایت یا استان خود را وارد کنید:")
        return

    # بررسی ثبت‌نام - گام سوم: دریافت ولایت و اتمام ثبت‌نام
    if user_id in users_profile and users_profile[user_id]['status'] == 'register_province':
        users_profile[user_id]['province'] = text
        users_profile[user_id]['status'] = 'idle'
        bot.send_message(user_id, "🎉 ثبت نام شما با موفقیت انجام شد!")
        show_main_menu(user_id)
        return

    # مدیریت دکمه‌های منوی اصلی چت ناشناس
    if text == "❓ اتصال به ناشناس ❓":
        if user_id in active_chats:
            bot.send_message(user_id, "⚠️ شما در حال حاضر در یک گفتگو هستید.")
            return
        
        if user_id in online_queue:
            bot.send_message(user_id, "🔍 شما در صف انتظار هستید. لطفاً صبور باشید.")
            return

        # بررسی وجود همصحبت در صف
        if online_queue:
            partner_id = online_queue.pop(0)
            active_chats[user_id] = partner_id
            active_chats[partner_id] = user_id
            
            # ارسال پیام اتصال موفق به هر دو طرف
            bot.send_message(user_id, "🎉 به یک ناشناس متصل شدید!\nبرای قطع چت از دستور /stop استفاده کنید.")
            bot.send_message(partner_id, "🎉 به یک ناشناس متصل شدید!\nبرای قطع چت از دستور /stop استفاده کنید.")
        else:
            online_queue.append(user_id)
            bot.send_message(user_id, "🔍 در حال جستجو برای پیدا کردن یک همصحبت آنلاین...\nلطفاً کمی منتظر بمانید.")
            
    elif text == "🔴 اتصال به هم ولایتی 🔴 (۲ سکه)":
        user_prov = users_profile.get(user_id, {}).get('province', '')
        # جستجو در صف برای پیدا کردن فردی با همان ولایت
        found = False
        for partner_id in online_queue:
            if users_profile.get(partner_id, {}).get('province') == user_prov and partner_id != user_id:
                online_queue.remove(partner_id)
                active_chats[user_id] = partner_id
                active_chats[partner_id] = user_id
                bot.send_message(user_id, f"🎉 به یک هم‌ولایتی از {user_prov} متصل شدید!")
                bot.send_message(partner_id, f"🎉 به یک هم‌ولایتی از {user_prov} متصل شدید!")
                found = True
                break
        if not found:
            bot.send_message(user_id, "⏰ در این ساعت همصحبت هم‌ولایتی پیدا نشد.\nشما در صف انتظار قرار گرفتید.")
            if user_id not in online_queue:
                online_queue.append(user_id)

    elif text == "👤 پروفایل من":
        profile = users_profile.get(user_id, {})
        msg = f"👤 مشخصات شما:\n\n📝 نام: {profile.get('name')}\n🔢 سن: {profile.get('age')}\n📍 ولایت: {profile.get('province')}"
        bot.send_message(user_id, msg)

    elif text == "🔗 لینک ناشناس من" or text == "🎁 معرفی به دوستان (سکه رایگان)" or text == "🔍 جستجوی کاربر" or text == "📞 پشتیبانی 🧑‍💻":
        bot.send_message(user_id, "ℹ️ این بخش به زودی در نسخه‌های بعدی فعال می‌شود.")

    # ارسال پیام بین دو کاربر متصل شده
    else:
        if user_id in active_chats:
            partner_id = active_chats[user_id]
            try:
                bot.send_message(partner_id, text)
            except:
                end_chat(user_id)
        else:
            bot.send_message(user_id, "⚠️ شما به کسی متصل نیستید. از دکمه‌های زیر برای اتصال استفاده کنید.")

# دستور قطع چت
@bot.message_handler(commands=['stop'])
def stop_command(message):
    end_chat(message.chat.id)

def end_chat(user_id):
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        del active_chats[user_id]
        if partner_id in active_chats:
            del active_chats[partner_id]
        bot.send_message(user_id, "❌ گفتگو بسته شد.")
        bot.send_message(partner_id, "❌ همصحبت شما گفتگو را قطع کرد و گفتگو بسته شد.")
        show_main_menu(user_id)
        show_main_menu(partner_id)
    elif user_id in online_queue:
        online_queue.remove(user_id)
        bot.send_message(user_id, "🚫 جستجو لغو شد.")
        show_main_menu(user_id)

# تابع نمایش منوی اصلی دقیقاً مثل عکس شما
def show_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("❓ اتصال به ناشناس ❓")
    btn2 = types.KeyboardButton("🔴 اتصال به هم ولایتی 🔴 (۲ سکه)")
    btn3 = types.KeyboardButton("🔗 لینک ناشناس من")
    btn4 = types.KeyboardButton("👤 پروفایل من")
    btn5 = types.KeyboardButton("🎁 معرفی به دوستان (سکه رایگان)")
    btn6 = types.KeyboardButton("🔍 جستجوی کاربر")
    btn7 = types.KeyboardButton("📞 پشتیبانی 🧑‍💻")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)
    markup.add(btn7)
    
    bot.send_message(user_id, "📱 یک گزینه را از منوی زیر انتخاب کنید:", reply_markup=markup)

# اجرای مداوم ربات
bot.polling(none_stop=True)
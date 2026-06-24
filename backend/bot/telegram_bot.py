# telegram_bot.py
import os
import sys
from dotenv import load_dotenv
from telegram import Update,KeyboardButton,ReplyKeyboardMarkup
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.qr_generator import create_qr_code
import asyncio



load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DONATE_QR_ID =  os.getenv("DONATE_QR_FILE_ID")


def get_main_keyboard ():
    keyboard = [
        [KeyboardButton("🚀 បង្កើត QR code ថ្មី")],
        [KeyboardButton("☕️ ឧបត្ថម្ភ (Donate)"), KeyboardButton("❓ ជំនួយ")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    

async def start (update : Update ,context : ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "សួស្តី! 👋 ខ្ញុំគឺជា QR Code Bot។\n"
        "សូមផ្ញើអត្ថបទ ឬតំណភ្ជាប់ (URL) ណាមួយមកកាន់ខ្ញុំ នោះខ្ញុំនឹងបម្លែងវាជា QR Code ជូនអ្នកភ្លាមៗ! 🚀"
    )
    await update.message.reply_text(welcome_text)




async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ទាញយកទីតាំងនៃ Folder 'bot' បច្ចុប្បន្ន
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # តភ្ជាប់ទីតាំងនោះទៅកាន់ 'images/donate_qr.png'
    qr_image_path = os.path.join(current_dir, "images", "donate_qr.png")
    
    try:
        # សំខាន់បំផុត៖ ត្រូវប្រើ open() ជាមួយ 'rb' ដើម្បីអានរូបភាពជាទម្រង់ Binary
        with open(qr_image_path, 'rb') as photo_file:
            await update.message.reply_photo(
                photo=photo_file,
                caption="សូមអរគុណសម្រាប់ការគាំទ្រដល់ការអភិវឌ្ឍ Bot របស់យើង! 🙏"
            )
    except FileNotFoundError:
        print(f"រកមិនឃើញរូបភាពនៅទីតាំង៖ {qr_image_path}")
        await update.message.reply_text("សុំទោស! ខ្ញុំរកមិនឃើញរូបភាព QR Code សម្រាប់ឧបត្ថម្ភនៅក្នុងប្រព័ន្ធទេ។")
    except Exception as e:
        print(f"Error sending donate QR: {e}")
        await update.message.reply_text("មិនអាចផ្ញើ QR Code បានទេ សូមព្យាយាមម្តងទៀត។")

async def help_command(update :Update,context :ContextTypes.DEFAULT_TYPE):
    help_text = (
        "នេះជាវិធីប្រើប្រាស់ QR Code Bot:\n\n"
        "1. **បង្កើត QR Code ថ្មី:**\n"
        "   - ចុចប៊ូតុង '🚀 បង្កើត QR code ថ្មី' ឬផ្ញើអត្ថបទ/តំណភ្ជាប់ (URL) មកកាន់ខ្ញុំ។\n"
        "   - ខ្ញុំនឹងបង្កើត QR Code ជូនអ្នកភ្លាមៗ។\n\n"
        "2. **ឧបត្ថម្ភ (Donate):**\n"
        "   - ចុចប៊ូតុង '☕️ ឧបត្ថម្ភ (Donate)' ដើម្បីផ្ញើការគាំទ្រដល់ការអភិវឌ្ឍ Bot របស់យើង។\n\n"
        "3. **ជំនួយ:**\n"
        "   - ចុចប៊ូតុង '❓ ជំនួយ' ដើម្បីមើលពាក្យបញ្ជាដែលមាន។"
    )
    
    await update.message.reply_text(help_text,reply_markup=get_main_keyboard())
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # ពិនិត្យមើលប៊ូតុង
    if text == "☕️ ឧបត្ថម្ភ (Donate)":
        await donate(update, context)
        return
    elif text == "❓ ជំនួយ":
        await help_command(update, context)
        return
    elif text == "🚀 បង្កើត QR code ថ្មី":
        await update.message.reply_text(
            "សូមវាយបញ្ចូលអត្ថបទ ឬតំណភ្ជាប់ (URL) ដែលអ្នកចង់បម្លែងជា QR Code៖",
            reply_markup=get_main_keyboard()
        )
        return

    # ១. ផ្ញើសារដំបូង
    processing_msg = await update.message.reply_text("⏳ កំពុងរៀបចំ...")

    try:
        # ២. ធ្វើចលនាលោតភាគរយ (Progress Bar Animation)
        # យើងឲ្យវាលោតពី 20, 50, 80, រហូតដល់ 100
        for percent in [20, 50, 80, 100]:
            bars = "█" * (percent // 10)
            empty = "░" * (10 - (percent // 10))
            progress_text = f"⏳ កំពុងបង្កើត QR Code ({percent}%)\n{bars}{empty}"
            
            # កែប្រែសារចាស់ឲ្យទៅជាភាគរយថ្មី
            await context.bot.edit_message_text(
                chat_id=update.message.chat_id,
                message_id=processing_msg.message_id,
                text=progress_text
            )
            await asyncio.sleep(0.4) # សម្រាក 0.4 វិនាទី ទើបលោតភាគរយបន្តទៀត
            
        # ៣. ហៅមុខងារបង្កើត QR Code ពិតប្រាកដ
        img_buffer = create_qr_code(text)
        
        # ៤. ផ្ញើរូបភាពទៅកាន់អ្នកប្រើប្រាស់
        await update.message.reply_photo(
            photo=img_buffer,
            caption="នេះគឺជា QR Code របស់អ្នក! 🚀\n\nបង្កើតដោយ: @ឈ្មោះBotរបស់អ្នក",
            reply_markup=get_main_keyboard()
        )
        
        # ៥. លុបសារ Progress bar (100%) នោះចោលវិញ ដើម្បីកុំឲ្យរញ៉េរញ៉ៃ
        await processing_msg.delete()
        
    except Exception as e:
        print(f"Error generating QR: {e}")
        await context.bot.edit_message_text(
            chat_id=update.message.chat_id,
            message_id=processing_msg.message_id,
            text="សុំទោស! មានបញ្ហាក្នុងការបង្កើត QR Code។ សូមព្យាយាមម្តងទៀត។"
        )

async def update_progress(update, context, processing_msg, state):
    last_percent = -1
    
    while state['status'] == "progress":
        current_percent = int(state['progress'])
        
        if current_percent != last_percent:
            # បង្កើត Progress Bar
            bars = "█" * (current_percent // 10)
            empty = "░" * (10 - (current_percent // 10))
            progress_text = f"⏳ កំពុងបង្កើត QR Code ({current_percent}%)\n{bars}{empty}"

            try:
                await context.bot.edit_message_text(
                    chat_id=update.message.chat_id,
                    message_id=processing_msg.message_id,
                    text=progress_text
                )
                last_percent = current_percent
            except Exception as e:
                # បង្ការពេល Telegram លោត Error (ឧទាហរណ៍ Edit អក្សរដដែល ឬ Edit លឿនពេក)
                print(f"មិនអាចកែប្រែសារបានទេ (Progress Bar): {e}")

        # ចំណុចសំខាន់បំផុត៖ ត្រូវឲ្យវាសម្រាក ០.៥ វិនាទី មុននឹងវិលត្រឡប់ទៅឆែកម្តងទៀត
        await asyncio.sleep(0.5)

def main():
    if not TOKEN:
        print("Error: មិនទាន់មាន TELEGRAM_BOT_TOKEN នៅក្នុងឯកសារ .env ទេ!")
        sys.exit(1)

    # បង្កើត Application (ខួរក្បាលរបស់ Bot)
    app = Application.builder().token(TOKEN).build()

    # ភ្ជាប់មុខងារ (Commands) ទៅកាន់ Bot
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("donate", donate))
    
    # ភ្ជាប់មុខងារអានសារធម្មតា (មិនមែនជា Command /)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Telegram Bot កំពុងដំណើរការហើយ... (ចុច Ctrl+C ដើម្បីបញ្ឈប់)")
    
    # ចាប់ផ្តើមស្តាប់សារពីអ្នកប្រើប្រាស់
    app.run_polling()

if __name__ == "__main__":
    main()
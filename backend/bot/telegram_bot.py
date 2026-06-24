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


def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🚀 បង្កើត QR code ថ្មី"), KeyboardButton("🎨 QR ដាក់ Logo")],
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
    
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """មុខងារសម្រាប់ចាប់យករូបភាពដែលអ្នកប្រើប្រាស់ផ្ញើមក"""
    
    # ពិនិត្យមើលថាតើ Bot កំពុងរង់ចាំ Logo ដែរឬទេ
    if context.user_data.get('state') == 'waiting_for_logo':
        # ទាញយករូបភាពដែលមានគុណភាពច្បាស់ជាងគេ (index ចុងក្រោយគេ)
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)
        
        # ទាញយករូបភាពនោះមកទុកក្នុង Memory ជាទម្រង់ Bytes
        photo_bytes = await photo_file.download_as_bytearray()
        
        # រក្សាទុករូបភាពនេះទៅក្នុងទិន្នន័យបណ្តោះអាសន្នរបស់អ្នកប្រើប្រាស់ម្នាក់ៗ
        context.user_data['logo_bytes'] = bytes(photo_bytes)
        context.user_data['state'] = 'waiting_for_text_with_logo' # ប្តូរគោលដៅទៅរង់ចាំអត្ថបទវិញ
        
        await update.message.reply_text(
            "ទទួលបាន Logo ហើយ! ✅\n\nឥឡូវនេះ សូមបញ្ជូនអត្ថបទ ឬ Link ដែលអ្នកចង់បម្លែងជា QR Code៖",
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text("ប្រសិនបើអ្នកចង់បង្កើត QR Code ដាក់ Logo សូមចុចប៊ូតុង '🎨 QR ដាក់ Logo' ជាមុនសិន។")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # ១. ពិនិត្យមើលការចុចប៊ូតុង
    if text == "☕️ ឧបត្ថម្ភ (Donate)":
        await donate(update, context)
        return
    elif text == "❓ ជំនួយ":
        await help_command(update, context)
        return
    elif text == "🚀 បង្កើត QR code ថ្មី":
        context.user_data.clear() # លុបចោលប្រវត្តិទិន្នន័យចាស់
        await update.message.reply_text("សូមវាយបញ្ចូលអត្ថបទ ឬតំណភ្ជាប់ (URL) ដែលអ្នកចង់បម្លែងជា QR Code៖")
        return
    elif text == "🎨 QR ដាក់ Logo":
        context.user_data['state'] = 'waiting_for_logo' # កំណត់ចំណាំថា Bot កំពុងរង់ចាំ Logo
        await update.message.reply_text("សូមផ្ញើរូបភាព Logo ដែលអ្នកចង់ដាក់នៅកណ្តាល QR Code មកកាន់ខ្ញុំ 🖼️\n*(សូមផ្ញើជាទម្រង់រូបភាពធម្មតា មិនមែនជា File)*", parse_mode="Markdown")
        return

    # ២. ដំណើរការបង្កើត QR Code (មាន Logo ឬ គ្មាន Logo)
    processing_msg = await update.message.reply_text("⏳ កំពុងបង្កើត QR Code... សូមរង់ចាំបន្តិច")
    
    try:
        # ឆែកមើលថាតើគាត់មានបានផ្ញើ Logo ទុកមុនដែរឬទេ
        state = context.user_data.get('state')
        logo_bytes = context.user_data.get('logo_bytes') if state == 'waiting_for_text_with_logo' else None
        
        # ហៅមុខងារបង្កើត QR ពី Backend របស់យើង (មាន Logo ឬ គ្មានគឺវាចាត់ចែងដោយស្វ័យប្រវត្តិ)
        img_buffer = create_qr_code(data=text, logo_bytes=logo_bytes)
        
        await update.message.reply_photo(
            photo=img_buffer,
            caption="នេះគឺជា QR Code របស់អ្នក! 🎉",
            reply_markup=get_main_keyboard()
        )
        await processing_msg.delete()
        
    except Exception as e:
        print(f"Error generating QR: {e}")
        await processing_msg.edit_text("សុំទោស! មានបញ្ហាក្នុងការបង្កើត QR Code។ សូមព្យាយាមម្តងទៀត។")
    finally:
        # សំខាន់៖ លុបទិន្នន័យ Logo ចោលវិញពេលបង្កើតរួច ដើម្បីកុំឲ្យជាប់ទៅលើកក្រោយទៀត
        context.user_data.clear()

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
    
    # ភ្ជាប់មុខងារអានសារជារូបភាព (បន្ថែមថ្មី)
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🚀 Telegram Bot កំពុងដំណើរការហើយ... (ចុច Ctrl+C ដើម្បីបញ្ឈប់)")
    
    # ចាប់ផ្តើមស្តាប់សារពីអ្នកប្រើប្រាស់
    app.run_polling()

if __name__ == "__main__":
    main()
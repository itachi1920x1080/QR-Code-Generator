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
        [KeyboardButton("🚀 បង្កើត QR ធម្មតា"), KeyboardButton("🎨 QR ដាក់ Logo")],
        [KeyboardButton("📶 QR សម្រាប់ Wi-Fi"), KeyboardButton("📧 QR សម្រាប់ Email")],
        [KeyboardButton("☕️ ឧបត្ថម្ភ (Donate)"), KeyboardButton("❓ ជំនួយ")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "សួស្តី! 👋 ខ្ញុំគឺជា QR Code Bot។\nសូមជ្រើសរើសមុខងារណាមួយខាងក្រោម៖"
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())




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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "នេះជាវិធីប្រើប្រាស់ QR Code Bot:\n\n"
        "1. **បង្កើត QR Code ធម្មតា:**\n"
        "   - ចុចប៊ូតុង '🚀 បង្កើត QR ធម្មតា' ឬផ្ញើអត្ថបទ/តំណភ្ជាប់ (URL) មកកាន់ខ្ញុំ។\n\n"
        "2. **Wi-Fi និង Email:**\n"
        "   - ជ្រើសរើសប៊ូតុង '📶 QR សម្រាប់ Wi-Fi' ឬ '📧 QR សម្រាប់ Email' ហើយធ្វើតាមការណែនាំ។\n\n"
        "3. **ឧបត្ថម្ភ (Donate):**\n"
        "   - ចុចប៊ូតុង '☕️ ឧបត្ថម្ភ (Donate)' ដើម្បីផ្ញើការគាំទ្រដល់ការអភិវឌ្ឍ Bot របស់យើង។"
    )
    
    await update.message.reply_text(help_text, reply_markup=get_main_keyboard())
    
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('state') == 'waiting_for_logo':
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)
        photo_bytes = await photo_file.download_as_bytearray()
        
        context.user_data['logo_bytes'] = bytes(photo_bytes)
        context.user_data['state'] = 'waiting_for_text_with_logo'
        
        await update.message.reply_text("ទទួលបាន Logo ហើយ! ✅\nសូមបញ្ជូនអត្ថបទ ឬ Link មកកាន់ខ្ញុំ៖", reply_markup=get_main_keyboard())
    else:
        await update.message.reply_text("ប្រសិនបើអ្នកចង់បង្កើត QR ដាក់ Logo សូមចុចប៊ូតុង '🎨 QR ដាក់ Logo' ជាមុនសិន។")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    state = context.user_data.get('state')

    # --- ចាត់ចែងការចុចប៊ូតុង (Menu) ---
    if text == "☕️ ឧបត្ថម្ភ (Donate)":
        await donate(update, context)
        return
    elif text == "❓ ជំនួយ":
        await help_command(update, context)
        return
    elif text == "🚀 បង្កើត QR ធម្មតា":
        context.user_data.clear()
        await update.message.reply_text("សូមវាយបញ្ចូលអត្ថបទ ឬតំណភ្ជាប់ (URL) របស់អ្នក៖")
        return
    elif text == "🎨 QR ដាក់ Logo":
        context.user_data['state'] = 'waiting_for_logo'
        await update.message.reply_text("សូមផ្ញើរូបភាព Logo របស់អ្នកមកកាន់ខ្ញុំ 🖼️")
        return
    elif text == "📶 QR សម្រាប់ Wi-Fi":
        context.user_data['state'] = 'waiting_for_wifi_ssid'
        await update.message.reply_text("សូមវាយបញ្ចូល **ឈ្មោះ Wi-Fi (SSID)** របស់អ្នក៖", parse_mode="Markdown")
        return
    elif text == "📧 QR សម្រាប់ Email":
        context.user_data.clear()
        await update.message.reply_text("មុខងារនេះតម្រូវឲ្យអ្នកវាយតាមទម្រង់នេះ៖\n`mailto:ឈ្មោះអ៊ីមែល@gmail.com`", parse_mode="Markdown")
        return

    # --- ចាត់ចែងការឆ្លើយតបជាជំហានៗ (Step-by-step) ---
    
    # ជំហានសម្រាប់ Wi-Fi
    if state == 'waiting_for_wifi_ssid':
        context.user_data['wifi_ssid'] = text
        context.user_data['state'] = 'waiting_for_wifi_password'
        await update.message.reply_text("សូមវាយបញ្ចូល **លេខសម្ងាត់ Wi-Fi (Password)** របស់អ្នក៖\n*(បើគ្មានលេខសម្ងាត់ សូមវាយពាក្យថា `គ្មាន`)*", parse_mode="Markdown")
        return
        
    elif state == 'waiting_for_wifi_password':
        ssid = context.user_data.get('wifi_ssid')
        password = text if text.lower() != "គ្មាន" else ""
        encryption = "WPA" if password else "nopass"
        
        # ផ្គុំទិន្នន័យ Wi-Fi
        final_text = f"WIFI:T:{encryption};S:{ssid};P:{password};H:false;;"
        caption = f"នេះជា QR Code សម្រាប់ភ្ជាប់ Wi-Fi: **{ssid}** 📶"
        
    else:
        # ប្រសិនបើជាអត្ថបទធម្មតា ឬអត្ថបទសម្រាប់ដាក់ Logo
        final_text = text
        caption = "នេះគឺជា QR Code របស់អ្នក! 🎉"

    # --- ដំណើរការបង្កើត QR Code ---
    processing_msg = await update.message.reply_text("⏳ កំពុងបង្កើត QR Code... សូមរង់ចាំបន្តិច")
    
    try:
        logo_bytes = context.user_data.get('logo_bytes')
        
        # ហៅមុខងារ Backend មកប្រើ (កំណត់ពណ៌តាមចំណូលចិត្តសម្រាប់ Bot)
        img_buffer = create_qr_code(
            data=final_text, 
            logo_bytes=logo_bytes,
            fg_color="#1d1b4b", # អ្នកអាចប្តូរពណ៌នៅទីនេះបាន (ឧ. ពណ៌ខៀវចាស់)
            space=4,
            size=768
        )
        
        await update.message.reply_photo(
            photo=img_buffer,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        await processing_msg.delete()
        
    except Exception as e:
        print(f"Error: {e}")
        await processing_msg.edit_text("សុំទោស! មានបញ្ហាក្នុងការបង្កើត QR Code។")
    finally:
        context.user_data.clear() # លុបទិន្នន័យចោលវិញ

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
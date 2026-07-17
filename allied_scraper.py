import os
import requests
import random
import time
import json
from faker import Faker
from datetime import datetime

fake = Faker()

# ============ CONFIGURATION ============
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8753374221:AAFGfB7Cvjuyd4frwwcIZYNmENTRIG9zBkE')
CHAT_ID = int(os.environ.get('CHAT_ID', -1004436738328))

# ============ TARGET BINS (ONLY THESE 3) ============
TARGET_BINS = [
    '476215',  # ALLIED BANK - PLATINUM
    '486263',  # ALLIED BANK - GOLD
    '486264'   # ALLIED BANK - CLASSIC
]

BIN_INFO = {
    '476215': {
        'bank': 'ALLIED BANK LIMITED',
        'type': 'VISA',
        'level': 'PLATINUM',
        'country': 'PAKISTAN',
        'flag': '🇵🇰'
    },
    '486263': {
        'bank': 'ALLIED BANK LIMITED',
        'type': 'VISA',
        'level': 'GOLD',
        'country': 'PAKISTAN',
        'flag': '🇵🇰'
    },
    '486264': {
        'bank': 'ALLIED BANK LIMITED',
        'type': 'VISA',
        'level': 'CLASSIC',
        'country': 'PAKISTAN',
        'flag': '🇵🇰'
    }
}

# ============ CARD GENERATION ============

def generate_card_with_bin(bin_prefix):
    """Generate valid card number with specific BIN"""
    length = 16
    body = bin_prefix + ''.join([str(random.randint(0, 9)) for _ in range(length - len(bin_prefix) - 1)])
    
    # Luhn algorithm
    digits = [int(d) for d in body]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    total_sum = sum(digits)
    check_digit = (10 - (total_sum % 10)) % 10
    
    return body + str(check_digit)

def luhn_check(card_number):
    """Verify card number using Luhn algorithm"""
    digits = [int(d) for d in card_number]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0

def generate_card():
    """Generate complete card from target BINs"""
    # Randomly select one of the 3 BINs
    bin_prefix = random.choice(TARGET_BINS)
    bin_info = BIN_INFO[bin_prefix]
    
    # Generate card number
    card_number = generate_card_with_bin(bin_prefix)
    
    # Validate
    if not luhn_check(card_number):
        return generate_card()  # Retry
    
    # Generate other details
    month = str(random.randint(1, 12)).zfill(2)
    year = str(random.randint(27, 35)).zfill(2)
    cvv = str(random.randint(100, 999)).zfill(3)
    
    # Generate holder name
    holder = fake.name()
    
    return {
        'card_number': card_number,
        'month': month,
        'year': year,
        'cvv': cvv,
        'bin': bin_prefix,
        'bank': bin_info['bank'],
        'type': bin_info['type'],
        'level': bin_info['level'],
        'country': bin_info['country'],
        'flag': bin_info['flag'],
        'holder': holder
    }

# ============ SEND TO TELEGRAM ============

def send_card_to_telegram(card_data, index=None, total=None):
    """Send card to Telegram with Allied Bank format"""
    telegram_api = f'https://api.telegram.org/bot{BOT_TOKEN}'
    
    # Format card details
    card_details = f"{card_data['card_number']}|{card_data['month']}|20{card_data['year']}|{card_data['cvv']}"
    card_masked = f"{card_data['card_number'][:6]}xxxx|{card_data['month']}|20{card_data['year']}|xxx"
    
    # Create message
    message = (
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>APPROVED - ALLIED BANK</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>CC</b> <code>{card_details}</code>\n"
        f"<b>Gen</b> <code>/gen {card_masked}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>BIN</b>\n"
        f"<code>{card_data['bin']}</code>\n"
        f"<b>Bk</b>\n"
        f"<b>{card_data['bank']}</b>\n"
        f"<b>Bv</b>\n"
        f"{card_data['type']}\n"
        f"<b>Te</b>\n"
        f"CREDIT\n"
        f"<b>Lv</b>\n"
        f"{card_data['level']}\n"
        f"<b>City</b>\n"
        f"{card_data['country']} {card_data['flag']}\n"
        f"<b>Holder</b>\n"
        f"{card_data['holder']}\n"
        f"<b>@{'allied_scraper'}</b>\n"
        f"{datetime.now().strftime('%I:%M %p')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏦 <b>ALLIED BANK LIMITED</b>\n"
        f"📍 PAKISTAN 🇵🇰\n"
    )
    
    # Reply markup with 3 buttons
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "𝚅𝙸𝙿", "url": "https://t.me/+u9cv-q_x57xkNzA1"},
                {"text": "𝙲𝙷𝙰𝚁𝙶𝙴", "url": "https://t.me/+rzRUgyJfia84NjBl"},
                {"text": "Mᴀɪɴ", "url": "https://t.me/atulfroxt"}
            ]
        ]
    }
    
    # Send message
    try:
        data = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'reply_markup': json.dumps(reply_markup)
        }
        response = requests.post(f'{telegram_api}/sendMessage', data=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Sent Allied Bank card: {card_data['card_number'][:6]}xxxx ({card_data['level']})")
            return True
        elif response.status_code == 429:
            retry_after = response.json().get('parameters', {}).get('retry_after', 5)
            print(f"⏳ Rate limited, waiting {retry_after}s...")
            time.sleep(retry_after)
            return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ============ MAIN SCRAPER FUNCTION ============

def scrape_cards(total_cards=1000000, delay=0.5):
    """Main scraper function - ONLY ALLIED BANK BINS"""
    print("="*50)
    print("🏦 ALLIED BANK SCRAPER")
    print(f"📌 BINs: 476215 | 486263 | 486264")
    print(f"📍 Bank: ALLIED BANK LIMITED")
    print(f"🎯 Target: {total_cards} cards")
    print("🔥 Only Allied Bank cards")
    print("="*50 + "\n")
    
    success_count = 0
    stats = {
        '476215': 0,
        '486263': 0,
        '486264': 0
    }
    
    start_time = time.time()
    
    for i in range(1, total_cards + 1):
        # Generate card
        card_data = generate_card()
        
        # Update stats
        stats[card_data['bin']] += 1
        
        # Send to Telegram
        if send_card_to_telegram(card_data, i, total_cards):
            success_count += 1
        
        # Progress update
        if i % 100 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            print(f"\n📊 Progress: {i}/{total_cards} ({i/total_cards*100:.1f}%)")
            print(f"✅ Sent: {success_count} cards")
            print(f"📈 Rate: {rate:.1f} cards/sec")
            print(f"💳 476215: {stats['476215']} | 486263: {stats['486263']} | 486264: {stats['486264']}\n")
        
        # Delay between cards
        time.sleep(delay)
    
    # Final summary
    elapsed = time.time() - start_time
    print("\n" + "="*50)
    print("📊 SCRAPING COMPLETE")
    print(f"✅ Total cards sent: {success_count}")
    print(f"⏱️ Time: {elapsed:.1f} seconds")
    print(f"💳 476215 (PLATINUM): {stats['476215']}")
    print(f"💳 486263 (GOLD): {stats['486263']}")
    print(f"💳 486264 (CLASSIC): {stats['486264']}")
    print(f"🏦 Bank: ALLIED BANK LIMITED")
    print(f"📍 Country: PAKISTAN 🇵🇰")
    print("="*50)

# ============ KEEP ALIVE FUNCTION ============

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>ALLIED BANK SCRAPER</title>
            <style>
                body {
                    background: linear-gradient(135deg, #1a472a, #2d5a27);
                    color: #fff;
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    text-align: center;
                }
                .container {
                    padding: 40px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 20px;
                    border: 1px solid rgba(255,255,255,0.2);
                }
                h1 {
                    font-size: 2.5em;
                    color: #ffd700;
                }
                .status {
                    color: #4ade80;
                    font-size: 1.2em;
                    margin-top: 20px;
                }
                .bins {
                    margin-top: 20px;
                    background: rgba(0,0,0,0.3);
                    padding: 15px;
                    border-radius: 10px;
                }
                .bins code {
                    color: #ffd700;
                    font-size: 1.1em;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏦 ALLIED BANK</h1>
                <h2>SCRAPER BOT</h2>
                <div class="status">🟢 Bot is Online</div>
                <div class="bins">
                    <code>476215 - PLATINUM</code><br>
                    <code>486263 - GOLD</code><br>
                    <code>486264 - CLASSIC</code>
                </div>
                <p style="margin-top:20px;color:#94a3b8;">Scraping Allied Bank Cards</p>
            </div>
        </body>
    </html>
    """

def keep_alive():
    """Keep the bot running"""
    def run():
        app.run(host='0.0.0.0', port=8080)
    
    t = Thread(target=run)
    t.daemon = True
    t.start()

# ============ MAIN ============

if __name__ == '__main__':
    # Start keep-alive
    keep_alive()
    
    # Start scraping
    print("🏦 ALLIED BANK SCRAPER STARTED")
    print("📌 ONLY SCRAPING THESE BINS:")
    print("   🔹 476215 - PLATINUM")
    print("   🔹 486263 - GOLD")
    print("   🔹 486264 - CLASSIC")
    print("🏦 Bank: ALLIED BANK LIMITED")
    print("📍 Country: PAKISTAN\n")
    
    # Get total cards from environment or default
    total_cards = int(os.environ.get('TOTAL_CARDS', 1000000))
    delay = float(os.environ.get('DELAY', 0.5))
    
    # Start scraping
    scrape_cards(total_cards=total_cards, delay=delay)

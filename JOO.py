import pyfiglet
import time
import requests
from playwright.sync_api import sync_playwright

# Print "ABDO" in ASCII Art format
ascii_art = pyfiglet.figlet_format("ABDO")
print(ascii_art)

# Print Telegram contact link
print("Contact me: \033[94mhttp://t.me/abdoshhba\033[0m")

print("GoldEagle Script")
print("Made by General Abdo\n")

PROGRESS_API_URL = "https://gold-eagle-api.fly.dev/user/me/progress"

def load_tokens():
    """Load tokens from data.txt (one token per line)."""
    try:
        with open("data.txt", "r") as file:
            tokens = [line.strip() for line in file if line.strip()]
        print(f"📄 Loaded {len(tokens)} tokens from data.txt.")
        return tokens
    except FileNotFoundError:
        print("❌ data.txt not found!")
        return []

def check_energy(page, token):
    """Retrieve the current energy level from the page."""
    try:
        energy_element = page.query_selector("div._label_15n79_25")
        if energy_element:
            energy_text = energy_element.inner_text().strip()
            energy = int(energy_text.split("/")[0])
            print(f"⚡ Token {token[-10:]} Energy Level: {energy}")
            return energy
    except Exception as e:
        print(f"⚠️ Token {token[-10:]}: Error retrieving energy: {e}")
    return 0  # Default to 0 if unable to fetch

def get_coin_count(page):
    """Retrieve the current coin balance from the page."""
    try:
        coin_element = page.query_selector("div._container_1wzqv_72 span._amount_1wzqv_81")
        if coin_element:
            return int(coin_element.inner_text().strip().replace(",", ""))
    except:
        pass
    return 0

def perform_task(token, page):
    """Perform the tapping cycle for one token."""
    print(f"\n🔄 Starting task for token {token[-10:]}")
    
    try:
        print(f"🌍 Token {token[-10:]}: Navigating to site...")
        page.goto("https://telegram.geagle.online/")
        time.sleep(3)

        print(f"🔑 Token {token[-10:]}: Setting session token...")
        page.evaluate(f"window.localStorage.setItem('session_token', '{token}')")
        page.reload()
        time.sleep(3)

        # Check energy before starting tapping cycle
        energy = check_energy(page, token)
        if energy < 100:
            print(f"🚫 Token {token[-10:]}: Energy too low ({energy}), skipping tapping cycle.")
            return 0  # Return 0 coins for skipped tokens

        # Inject auto-tapping script with 25 taps per second (interval ~40ms)
        print(f"🤖 Token {token[-10:]}: Starting auto-tapping session (25 taps/sec)...")
        page.evaluate("""
            (function(){
                var start = Date.now();
                var tapCount = 0;
                var tapInterval = setInterval(function(){
                    var tapBtn = document.querySelector("div._tapArea_njdmz_15");
                    if(tapBtn){ tapBtn.click(); tapCount++; }
                    if (tapCount >= 900 || Date.now() - start > 300000) { 
                        clearInterval(tapInterval); 
                    } 
                }, 40); // 25 taps per second
            })();
        """)

        # Print coin count immediately (time 0)
        coins = get_coin_count(page)
        current_time = time.strftime("%H:%M:%S")
        print(f"⏳ {current_time} | Token: {token[-10:]} | Coins: {coins}")

        start_time = time.time()
        last_print = start_time
        last_energy_check = start_time

        # Run tapping cycle (max 5 min or stop if energy < 100)
        while time.time() - start_time < 300:
            time.sleep(1)
            # Check energy every 10 seconds; if below 100, break early
            if time.time() - last_energy_check >= 10:
                energy = check_energy(page, token)
                if energy < 100:
                    print(f"🚫 Token {token[-10:]}: Energy dropped to {energy}. Moving to next token.")
                    break
                last_energy_check = time.time()
            # Print coin count every 2 minutes
            if time.time() - last_print >= 120:
                coins = get_coin_count(page)
                current_time = time.strftime("%H:%M:%S")
                print(f"⏳ {current_time} | Token: {token[-10:]} | Coins: {coins}")
                last_print = time.time()

        print(f"🔄 Token {token[-10:]}: Tapping cycle complete.")
        return coins  # Return coin balance after task

    except Exception as e:
        print(f"⚠️ Token {token[-10:]} Error: {e}")
        return 0

def main():
    """Process tokens in an infinite loop, restarting on any error."""
    while True:
        try:
            tokens = load_tokens()
            if not tokens:
                print("❌ No tokens found in data.txt! Exiting...")
                return

            print("\n====================================================")
            print("🚀 Starting a new cycle of token processing.")
            print("====================================================\n")

            total_coins = 0  # Initialize total coin balance

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                for token in tokens:
                    total_coins += perform_task(token, page)  # Add up all coin balances

                print(f"\n💰 Total Coins After Cycle: {total_coins:,}\n")  # Print total balance

                print("\n⏳ All tokens processed! Pausing for 1 minute before refreshing browser...")
                time.sleep(60)  # **1-minute wait before restarting**

                print("\n🔄 Refreshing browser before the next cycle...")
                page.reload()
                time.sleep(3)

                print("\n✅ Cycle complete. Restarting immediately...\n")

                browser.close()  # Close the browser before restarting

        except Exception as e:
            print(f"⚠️ An error occurred: {e}. Restarting the script in 10 seconds...")
            time.sleep(10)  # Pause before restarting in case of error

if __name__ == "__main__":
    main()

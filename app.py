import streamlit as st
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from PIL import Image

# ✅ Configure Selenium to Use ChromeDriver
chrome_options = Options()
chrome_options.binary_location = "/usr/bin/google-chrome"  # ✅ Manually set Chrome binary path
chrome_options.add_argument("--headless")  # Run without UI
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")  # ✅ Manually set ChromeDriver path

def get_fiverr_rank(username, keyword):
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    search_url = f"https://www.fiverr.com/search/gigs?query={keyword.replace(' ', '%20')}"
    driver.get(search_url)

    st.write("🔄 Fetching Fiverr search results... Please wait.")

    gig_position = -1
    found_page = "Not Found"
    gig_screenshot = None

    for page in range(1, 6):  # ✅ Search up to 5 pages
        time.sleep(3)  # ✅ Wait for page to load

        # ✅ Scroll down to load all results
        body = driver.find_element(By.TAG_NAME, "body")
        for _ in range(10):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)

        # ✅ Wait for gigs to load
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href]")))
        except:
            print("⚠️ Warning: No gigs found in search results!")

        # ✅ Extract all Fiverr gig links
        gigs = driver.find_elements(By.CSS_SELECTOR, "a[href]")
        all_gig_urls = [gig.get_attribute("href") for gig in gigs]
        print("✅ Extracted Gig URLs:", all_gig_urls)  # Debugging

        for index, gig_url in enumerate(all_gig_urls, start=1):
            if username in gig_url:
                gig_position = index
                found_page = f"Page {page}"

                # ✅ Take Screenshot
                screenshot_path = f"screenshot_{username}_{keyword.replace(' ', '_')}.png"
                driver.save_screenshot(screenshot_path)
                gig_screenshot = screenshot_path

                break

        if gig_position != -1:
            break  # ✅ Stop searching if gig is found

        # ✅ Click "Next Page" if exists
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a[rel='next']")
            next_button.click()
        except:
            break  # ✅ No more pages

    driver.quit()
    
    return gig_position, found_page, gig_screenshot  # ✅ Now properly indented inside function


# ✅ Streamlit UI Setup
st.title("🎯 Fiverr Gig Rank Checker (Like Fiverrlytics)")
st.write("Check your Fiverr gig ranking by entering your Fiverr username and keyword.")

# ✅ User Inputs
username = st.text_input("👤 Fiverr Username:", placeholder="e.g. mianawaiszafar")
keyword = st.text_input("🔍 Target Keyword:", placeholder="e.g. Google Analytics Setup")

# ✅ Run Fiverr Rank Check
if st.button("Check Rank"):
    if username and keyword:
        rank, page_found, screenshot = get_fiverr_rank(username, keyword)

        if rank != -1:
            st.success(f"🎯 Your gig is at **position {rank}** on **{page_found}**!")
            if screenshot and os.path.exists(screenshot):
                st.image(Image.open(screenshot), caption="📸 Screenshot of Your Gig in Search Results")
        else:
            st.error("❌ Your gig was **not found in the first 5 pages**.")

        # ✅ Disclaimer Message (Like Fiverrlytics)
        st.markdown(
            f"""
            ⚠️ This analysis is based on **5 Fiverr search pages** fetched on **{time.strftime('%Y-%m-%d')}**.
            Results may change due to personalization and other Fiverr metrics.

            **Fiverrlytics does not guarantee accuracy**. Use at your own risk.
            """
        )
    else:
        st.error("⚠️ Please enter both your Fiverr username and target keyword.")

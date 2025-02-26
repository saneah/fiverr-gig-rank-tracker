import streamlit as st
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

def extract_gig_id(gig_url):
    """
    Extracts the Fiverr gig identifier (slug) from the given URL.
    Supports both numeric and non-numeric gig URLs.
    """
    # ✅ Improved regex to capture all Fiverr gig URL types
    match = re.search(r"fiverr\.com/[^/]+/([^/?#]+)", gig_url)

    if match:
        gig_id = match.group(1)
        print("✅ Extracted Gig ID:", gig_id)  # Debugging print
        return gig_id

    print("❌ ERROR: Could not extract Gig ID from:", gig_url)
    return None


# Function to get Fiverr search results and find gig ranking
def get_fiverr_rank(keyword, gig_id):
    chrome_options = Options()

    # ✅ Explicitly set Chrome binary location
    chrome_options.binary_location = "/usr/bin/google-chrome"

    chrome_options.add_argument("--headless")  # Run without UI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # ✅ Force ChromeDriver path
    service = Service("/usr/bin/chromedriver")

    # ✅ Use the correct executable locations
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"❌ ERROR: Could not start ChromeDriver: {e}")
        return "ChromeDriver failed!"

    search_url = f"https://www.fiverr.com/search/gigs?query={keyword}"
    driver.get(search_url)


    gig_found = False
    gig_position = -1

    for page in range(1, 6):  # Check up to 5 pages
        time.sleep(3)

        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        gigs = soup.find_all("a", class_="gig-link")

        for index, gig in enumerate(gigs, start=1):
            if gig_id in gig["href"]:
                gig_found = True
                gig_position = ((page - 1) * len(gigs)) + index
                break

        if gig_found:
            break

        # Click "Next Page" if exists
        try:
            next_page = driver.find_element(By.CSS_SELECTOR, "a[rel='next']")
            next_page.click()
        except:
            break

    driver.quit()
    
    return gig_position if gig_found else "Not in first 5 pages"

# Streamlit UI
st.title("🛠️ Fiverr Gig Rank Tracker")
st.write("Enter your Fiverr Gig URL and the keyword you want to track.")

# User Inputs
gig_url = st.text_input("🔗 Fiverr Gig URL:", placeholder="https://www.fiverr.com/your-gig-url")
keyword = st.text_input("🔍 Keyword to Search:", placeholder="e.g. logo design")

if st.button("Check Rank"):
    if gig_url and keyword:
        gig_id = extract_gig_id(gig_url)
        
        if gig_id:
            st.write("🔄 Searching Fiverr for your gig... (This may take a few seconds)")
            gig_rank = get_fiverr_rank(keyword, gig_id)
            st.success(f"🎯 Your gig is at position: **{gig_rank}**")
        else:
            st.error("⚠️ Invalid Fiverr gig URL. Please enter a correct URL.")
    else:
        st.error("⚠️ Please enter both the Fiverr Gig URL and the keyword.")

import asyncio
import datetime
import subprocess
import streamlit as st
from playwright.async_api import async_playwright
import os
import sys
import nest_asyncio
import glob

# Allow nested event loops
nest_asyncio.apply()

# ---- Streamlit Config ----
st.set_page_config(page_title="TwitterX Spaces Downloader", page_icon="🎙️")

# ---- Paths ----
DATA_DIR = os.getcwd()
COOKIES_PATH = os.path.join(DATA_DIR, "cookies.txt")

# ---- Install Playwright (if missing) ----
if not os.path.exists(os.path.expanduser("~/.cache/ms-playwright")):
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
        st.success("✅ Chromium installed.")
    except Exception as e:
        st.error(f"❌ Playwright install failed: {e}")

# ---- Login Function ----
async def login_to_x(username, password, mfa_code=None):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://x.com/i/flow/login")
            #await page.wait_for_selector("input[name='text']", timeout=20000)
            # After username is entered and "Next" clicked
            try:
                await page.wait_for_selector("input[name='password']", timeout=10000)
            except:
            # Handle possible username confirmation step
                try:
                    confirm_input = await page.wait_for_selector("input[name='text']", timeout=10000)
                    await confirm_input.fill(username)
                    await page.click("div[role='button']:has-text('Next')")
                    st.info("🔁 Username confirmation step handled.")
                    await page.wait_for_selector("input[name='password']", timeout=10000)
                except Exception as e:
                    st.error(f"Login failed during username confirmation step: {e}")
                    return False
            await page.fill("input[name='text']", username)
            await page.click("button:has-text('Next')")
            st.success("✅ Username entered and Next clicked.")

            await page.wait_for_selector("input[name='password']", timeout=20000)
            await page.fill("input[name='password']", password)
            await page.click("button:has-text('Log in')")
            st.success("✅ Password entered and Log in clicked.")

            if mfa_code:
                try:
                    mfa_input = await page.wait_for_selector("input[data-testid='ocfEnterTextTextInput']", timeout=60000)
                    await mfa_input.fill(mfa_code)
                    await page.click("button[data-testid='ocfEnterTextNextButton']")
                    st.success("✅ MFA code entered and Next clicked.")
                except Exception as e:
                    st.warning(f"⚠️ MFA skipped or failed: {e}")

            await page.wait_for_timeout(5000)

            cookies = await context.cookies()
            with open(COOKIES_PATH, "w") as f:
                f.write("# Netscape HTTP Cookie File\n")
                for cookie in cookies:
                    f.write(
                        f"{cookie['domain']}\t"
                        f"{'TRUE' if cookie['domain'].startswith('.') else 'FALSE'}\t"
                        f"{cookie['path']}\t"
                        f"{'TRUE' if cookie.get('secure', False) else 'FALSE'}\t"
                        f"{int(cookie['expires']) if cookie.get('expires') else 0}\t"
                        f"{cookie['name']}\t"
                        f"{cookie['value']}\n"
                    )

            await browser.close()
            return True
    except Exception as e:
        st.error(f"Login failed: {e}")
        return False

# ---- Download Twitter Space ----
def download_twitter_space(url):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"twitter_space_{timestamp}.m4a"
    output_path = os.path.join(DATA_DIR, filename)

    command = [
        "yt-dlp",
        "--verbose",
        "--cookies", COOKIES_PATH,
        "-o", output_path,
        url
    ]

    st.code(" ".join(command), language="bash")

    result = subprocess.run(command, capture_output=True)
    if result.returncode == 0 and os.path.exists(output_path):
        st.success("✅ Download successful.")
        st.text(f"File saved as: {filename}")
        with open(output_path, "rb") as f:
            st.download_button("⬇️ Download Audio File", f, file_name=filename, mime="audio/m4a")
    else:
        st.error("❌ Download failed.")
        st.text(result.stderr.decode())

# ---- UI ----
st.title("🎙️ TwitterX Spaces Downloader")
st.caption("Download Twitter Spaces with yt-dlp + Playwright + Streamlit")

with st.form("login_form"):
    username = st.text_input("TwitterX Username")
    password = st.text_input("TwitterX Password", type="password")
    mfa_code = st.text_input("MFA Code (if applicable)")
    space_url = st.text_input("Twitter Space URL", placeholder="https://x.com/i/spaces/1YpKklAePYBGj")
    submit = st.form_submit_button("Login & Download")

if submit:
    if not username or not password or not space_url:
        st.warning("Please fill in all required fields.")
    else:
        with st.spinner("Logging in..."):
            login_success = asyncio.run(login_to_x(username, password, mfa_code))
        if login_success:
            st.info("Login successful. Starting download...")
            download_twitter_space(space_url)

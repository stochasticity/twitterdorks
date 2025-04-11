import asyncio
import datetime
import subprocess
import streamlit as st
from playwright.async_api import async_playwright
import os
import sys
import nest_asyncio
nest_asyncio.apply()


# ---- Must be FIRST Streamlit command ----
st.set_page_config(page_title="TwitterX Spaces Downloader", page_icon="🎙️")

# ---- Set up output paths ----
DATA_DIR = os.getcwd()
COOKIES_PATH = os.path.join(DATA_DIR, "cookies.txt")
#os.makedirs(DATA_DIR, exist_ok=True)

# ---- Install Playwright Browsers (only if needed) ----
if not os.path.exists(os.path.expanduser("~/.cache/ms-playwright")):
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
        st.success("✅ Chromium installed successfully.")
    except Exception as e:
        st.error(f"❌ Playwright install failed: {e}")

# ---- Async Login Function ----
async def login_to_x(username, password, mfa_code=None):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://x.com/i/flow/login")
            await page.wait_for_selector("input[name='text']", timeout=20000)
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
                    st.warning(f"⚠️ MFA not prompted or failed: {e}")

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

# ---- Download Function ----
def download_twitter_space(url):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_template = os.path.join(DATA_DIR, f"twitter_space_{timestamp}_%(uploader)s_%(upload_date)s_%(id)s.%(ext)s")

    command = [
        "yt-dlp",
        "--verbose",
        "--cookies", COOKIES_PATH,
        "--no-clean-info-json",
        "--write-comments",
        url,
        "-o", output_template
    ]

    st.code(" ".join(command), language="bash")

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        st.success("✅ Download successful.")
        st.text(f"Saved to: {output_template}")
    else:
        st.error("❌ Download failed.")
        st.text(result.stderr)
        with open(os.path.join(DATA_DIR, "yt_dlp_error.log"), "w") as log_file:
            log_file.write("YT-DLP Debug Information\n\n")
            log_file.write("Command:\n" + ' '.join(command) + "\n\n")
            log_file.write("STDERR:\n" + result.stderr)

# ---- Streamlit UI ----
#st.set_page_config(page_title="TwitterX Spaces Downloader", page_icon="🎙️")
st.title("🎙️ TwitterX Spaces Downloader")
st.caption("Download Twitter Spaces with yt-dlp + Playwright + Streamlit")

with st.form("login_form"):
    username = st.text_input("TwitterX Username", max_chars=100)
    password = st.text_input("TwitterX Password", type="password")
    mfa_code = st.text_input("MFA Code (if applicable)", max_chars=10)
    space_url = st.text_input("Twitter Space URL", placeholder="https://x.com/i/spaces/1YpKklAePYBGj")
    submit = st.form_submit_button("Login & Download")

if submit:
    if not username or not password or not space_url:
        st.warning("Please enter all required fields.")
    else:
        with st.spinner("Logging in and downloading space..."):
            asyncio.run(login_to_x(username, password, mfa_code))
            download_twitter_space(space_url)


import asyncio
import datetime
import subprocess
import streamlit as st
from playwright.async_api import async_playwright
import os
import nest_asyncio
<<<<<<< HEAD
import threading
import shutil
import zipfile
=======
>>>>>>> 74f8f5f2dfe2df2ff1feb002da8c20644ce706e4

nest_asyncio.apply()
st.set_page_config(page_title="TwitterX Spaces Downloader", page_icon="🎹")

<<<<<<< HEAD
DATA_DIR = os.getcwd()
COOKIES_PATH = os.path.join(DATA_DIR, "cookies.txt")

=======
st.set_page_config(page_title="TwitterX Spaces Downloader", page_icon="🎙️")

DATA_DIR = os.getcwd()
COOKIES_PATH = os.path.join(DATA_DIR, "cookies.txt")

# ---- Install Playwright if needed ----
>>>>>>> 74f8f5f2dfe2df2ff1feb002da8c20644ce706e4
if not os.path.exists(os.path.expanduser("~/.cache/ms-playwright")):
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
        st.success("✅ Chromium installed successfully.")
    except Exception as e:
        st.error(f"❌ Playwright install failed: {e}")

async def login_to_x(username, password, mfa_code=None, challenge_value=None):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://x.com/i/flow/login", timeout=60000)

            # Capture the landing page for debug
            html_snapshot = await page.content()
            with open("page_debug.html", "w", encoding="utf-8") as f:
                f.write(html_snapshot)
            st.warning("⚠️ Saved page_debug.html for inspection after landing on login page.")

            await page.wait_for_selector("input[name='text']", timeout=15000)
            await page.fill("input[name='text']", username)

            # Fallback attempts to click Next button
            try:
                await page.click("div[role='button']:has-text('Next')", timeout=5000)
            except:
                await page.click("//div[contains(text(), 'Next') and @role='button']", timeout=5000)

            st.success("✅ Username entered and Next clicked.")

<<<<<<< HEAD
            try:
                await page.wait_for_selector("input[name='password']", timeout=8000)
            except:
                st.info("🔁 Detected email/phone challenge. Supplying challenge value...")
                await page.screenshot(path="screenshot_challenge_screen.png")
                await page.wait_for_selector("input[data-testid='ocfEnterTextTextInput']", timeout=10000)
                await page.fill("input[data-testid='ocfEnterTextTextInput']", challenge_value)

                html = await page.content()
                with open("challenge_debug.html", "w", encoding="utf-8") as f:
                    f.write(html)

                try:
                    st.info("🔍 Trying selector: button[data-testid='ocfEnterTextNextButton']")
                    btn = await page.wait_for_selector("button[data-testid='ocfEnterTextNextButton']", timeout=10000)
                    await btn.scroll_into_view_if_needed()
                    await btn.click(force=True)
                    st.success("✅ Clicked challenge Next button.")
                except Exception as e:
                    st.error(f"❌ Challenge screen click failed: {e}")
                    await page.screenshot(path="challenge_next_fail.png")
                    return False

                try:
                    await page.wait_for_selector("input[name='password']", timeout=20000)
                except:
                    error_box = await page.query_selector("//div[contains(text(), 'Incorrect. Please try again.')]")
                    if error_box:
                        st.error("❌ Challenge value rejected by Twitter. Please double-check your phone/email.")
                        await page.screenshot(path="challenge_incorrect_value.png")
                        return False
                    else:
                        st.error("❌ Login failed: Password field not found after challenge.")
                        await page.screenshot(path="challenge_no_password.png")
                        return False

=======
            # Try password input next
            try:
                await page.wait_for_selector("input[name='password']", timeout=10000)
            except:
                try:
                    confirm_input = await page.wait_for_selector("input[name='text']", timeout=10000)
                    await confirm_input.fill(username)
                    await page.click("div[role='button']:has-text('Next')", timeout=5000)
                    st.info("🔁 Username confirmation step handled.")
                    await page.wait_for_selector("input[name='password']", timeout=10000)
                except Exception as e:
                    st.error(f"Login failed during username confirmation step: {e}")
                    return False

>>>>>>> 74f8f5f2dfe2df2ff1feb002da8c20644ce706e4
            await page.fill("input[name='password']", password)

            try:
                await page.click("div[role='button']:has-text('Log in')", timeout=5000)
            except:
                await page.click("//div[contains(text(), 'Log in') and @role='button']", timeout=5000)

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
        st.error(f"❌ Login failed: {e}")
        return False

async def async_download_twitter_space(url):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"twitter_space_{timestamp}"
    audio_path = os.path.join(DATA_DIR, f"{base_filename}.m4a")
    info_path = os.path.join(DATA_DIR, f"{base_filename}.info.json")
    zip_path = os.path.join(DATA_DIR, f"{base_filename}.zip")

    command = [
        "yt-dlp",
        "--verbose",
        "--cookies", COOKIES_PATH,
        "--no-clean-info-json",
        "--write-info-json",
        "--write-comments",
        url,
        "-o", audio_path
    ]
    st.code(" ".join(command), language="bash")

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        st.success("✅ Download successful.")
        st.text(f"Saved to: {audio_path}")

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            if os.path.exists(audio_path):
                zipf.write(audio_path, os.path.basename(audio_path))
                os.remove(audio_path)
            if os.path.exists(info_path):
                zipf.write(info_path, os.path.basename(info_path))
                os.remove(info_path)

        if os.path.exists(zip_path):
            st.session_state["zip_ready"] = zip_path
            st.toast("📦 Download ready", icon="📁")
        else:
            st.error("⚠️ Archive missing after download.")
    else:
        st.error("❌ Download failed.")
        st.text(stderr.decode())
        with open(os.path.join(DATA_DIR, "yt_dlp_error.log"), "w") as log_file:
            log_file.write("YT-DLP Debug Information\n\n")
            log_file.write("Command:\n" + ' '.join(command) + "\n\n")
            log_file.write("STDERR:\n" + stderr.decode())

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

background_loop = asyncio.new_event_loop()
threading.Thread(target=start_background_loop, args=(background_loop,), daemon=True).start()

# ---- Streamlit UI ----
st.title("🎹 TwitterX Spaces Downloader")
st.caption("Download Twitter Spaces with yt-dlp + Playwright + Streamlit")

uploaded_cookie = st.file_uploader("📂 Upload cookies.txt (to skip login)", type=["txt"])
if uploaded_cookie:
    with open(COOKIES_PATH, "wb") as out_file:
        out_file.write(uploaded_cookie.read())
    st.success("✅ Cookies uploaded. Login step will be skipped.")

with st.form("login_form"):
    username = st.text_input("TwitterX Username", max_chars=100)
    password = st.text_input("TwitterX Password", type="password")
    mfa_code = st.text_input("MFA Code (if applicable)", max_chars=10)
    challenge_value = st.text_input("Challenge: Email or Phone (if prompted)", max_chars=100)
    space_url = st.text_input("Twitter Space URL", placeholder="https://x.com/i/spaces/1mnxegnjbMPGX")
    submit = st.form_submit_button("Login & Download")

if submit:
    if not space_url:
        st.warning("Please enter the Space URL.")
    elif uploaded_cookie:
        st.success("🔐 Using uploaded cookies. Starting download...")
        asyncio.run_coroutine_threadsafe(async_download_twitter_space(space_url), background_loop)
    elif not username or not password:
        st.warning("Please enter username and password or upload cookies.")
    else:
        with st.spinner("Logging in..."):
            login_success = asyncio.run(login_to_x(username, password, mfa_code, challenge_value))
        if login_success:
            st.info("Login successful. Starting download in background...")
            asyncio.run_coroutine_threadsafe(async_download_twitter_space(space_url), background_loop)

# Show download button if zip is ready
if "zip_ready" in st.session_state and os.path.exists(st.session_state["zip_ready"]):
    with open(st.session_state["zip_ready"], "rb") as zf:
        st.download_button(
            label="📦 Download Archived Twitter Space",
            data=zf,
            file_name=os.path.basename(st.session_state["zip_ready"]),
            mime="application/zip"
        )

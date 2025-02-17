import os
import time
import threading
import tldextract
from urllib.parse import urlparse
from flask import Flask, request
from utils.db import get_all_websites_names, add_browser_record, get_last_browser_tab, add_website
from utils.icon_extractor import extract_website_icon
from utils.logger import log
import waitress


"""
This module is responsible for recording the user's activity on the browser, by receiving requests from the chrome extension.
"""


PORT = 8049
is_extension_active = False
app = Flask(__name__)
# server for recieving urls from the chrome extension
@app.post("/send_url")
def root() -> dict:
    global curr_domain_name, curr_url, is_extension_active
    is_extension_active = True
    url = request.form.get("url")
    try:
        if domain_name := extract_domain_name(url):
            curr_domain_name = domain_name
        curr_url = extract_base_url(url)
        return {"message": "success"}
    except Exception as e:
        # Log the error and return an error response
        log(e)
        return {"message": "error", "details": str(e)}, 400
@app.get("/check_extension")
def check_extension() -> dict:
    # return if chrome extension is active
    return {"is_extension_active": is_extension_active}
def run_server() -> None:
    waitress.serve(app, host='127.0.0.1', port=PORT)


# curr domain/url represent the last active browser tab (which is saved to db)
curr_domain_name = get_last_browser_tab() or 'BLANK'
curr_url = ''
# batch size represents number of records to be inserted into the database at once
batch_size = 30
batch_records = []
# unique websites names helps identify new websites
unique_websites_names = set(get_all_websites_names())
# icons path
websites_icons_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'Screen_Time_Tracker', 'Websites_Icons')
os.makedirs(websites_icons_dir, exist_ok=True)


def extract_domain_name(url: str) -> str:
    return tldextract.extract(url).domain


def extract_base_url(url: str) -> str:
    return urlparse(url).netloc


def save_new_website(url: str, domain_name: str) -> bool:
    try:
        extract_website_icon(website_url=url, website_name=domain_name, output_path=websites_icons_dir)
        add_website(website_name=domain_name)
    except Exception as e:
        log(f"Error extracting icon: {e}")


def record_active_browser_tab() -> None:
    global batch_records
    if curr_domain_name not in unique_websites_names:
        print(f'New website: {curr_domain_name}')
        unique_websites_names.add(curr_domain_name)
        threading.Thread(target=save_new_website, kwargs={'url': curr_url, 'domain_name': curr_domain_name}).start()
    # add new record to batch
    batch_records.append({
        'timestamp': int(time.time()),
        'domain_name': curr_domain_name
    })
    # insert batch to db if its size reached its threshold
    if len(batch_records) >= batch_size or time.time() - batch_records[0]['timestamp'] >= batch_size:
        for record in batch_records:
            add_browser_record(domain_name=record['domain_name'], timestamp=record['timestamp'])
        batch_records = []


if __name__ == "__main__":
    # Run the server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    # record continuously
    last_recorded = time.time()
    while True:
        try:
            if is_extension_active:
                record_active_browser_tab()
                last_recorded = time.time()
        except Exception as e:
            log(e)
        time.sleep(max(0, 1 - (time.time() - last_recorded)))

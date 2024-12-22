from flask import Flask, request
import time
import tldextract
from utils.db import add_browser_record, get_last_browser_tab
import waitress
import threading


PORT = 8049
app = Flask(__name__)

curr_domain_name = get_last_browser_tab() or 'BLANK'
batch_size = 30
batch_records = []

def record_active_browser_tab() -> None:
    global batch_records
    # add new record to batch
    batch_records.append({'timestamp': int(time.time()), 'domain_name': curr_domain_name})
    print(batch_records[-1])
    # insert batch to db if its size reached its threshold
    if len(batch_records) >= batch_size or time.time() - batch_records[0]['timestamp'] >= batch_size:
        for record in batch_records:
            add_browser_record(domain_name=record['domain_name'], timestamp=record['timestamp'])
        batch_records = []

def extract_domain_name(url: str) -> str:
    return tldextract.extract(url).domain

@app.post("/send_url")
def root() -> dict:
    global curr_domain_name
    url = request.form.get("url")
    try:
        if domain_name := extract_domain_name(url):
            curr_domain_name = domain_name
        return {"message": "success"}
    except Exception as e:
        # Log the error and return an error response
        print(f"Error processing URL: {e}")
        return {"message": "error", "details": str(e)}, 400

def run_server() -> None:
    waitress.serve(app, host='127.0.0.1', port=PORT)


if __name__ == "__main__":
    # Run the server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    # record continuously
    last_recorded = time.time()
    while True:
        record_active_browser_tab()
        last_recorded = time.time()
        time.sleep(max(0, 1 - (time.time() - last_recorded)))

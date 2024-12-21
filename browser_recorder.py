from flask import Flask, request
import time
from urllib.parse import urlparse
from utils.db import add_browser_record


app = Flask(__name__)

@app.post("/send_url")
def root():
    url = request.form.get("url")
    try:
        # Use urlparse to extract domain
        domain_name = urlparse(url).netloc
        # Remove 'www.' if present
        if domain_name.startswith('www.'):
            domain_name = domain_name.replace('www.', '')
        # Add browser record with current timestamp
        current_timestamp = int(time.time())
        if domain_name:
            add_browser_record(domain_name, url, current_timestamp)
        return {"message": "success"}
    except Exception as e:
        # Log the error and return an error response
        print(f"Error processing URL: {e}")
        return {"message": "error", "details": str(e)}, 400


if __name__ == "__main__":
    app.run(debug=False, port=8049)

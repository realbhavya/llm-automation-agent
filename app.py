from flask import Flask, request, jsonify
import os
import subprocess
import json
import sqlite3
from datetime import datetime
import openai
import requests
from PIL import Image
import pytesseract
import csv
import markdown
from bs4 import BeautifulSoup
import whisper
import difflib
import re

app = Flask(__name__)

data_dir = "/data"
os.makedirs(data_dir, exist_ok=True)

openai.api_key = os.environ.get("AIPROXY_TOKEN")

# Task Execution Function
def execute_task(task_description):
    try:
        task_description = task_description.lower()
        if "format" in task_description:
            return format_file()
        elif "count wednesdays" in task_description:
            return count_wednesdays()
        elif "sort contacts" in task_description:
            return sort_contacts()
        elif "query ticket sales" in task_description:
            return query_ticket_sales()
        elif "extract email" in task_description:
            return extract_email()
        elif "extract card number" in task_description:
            return extract_card_number()
        elif "find similar comments" in task_description:
            return find_similar_comments()
        elif "fetch api data" in task_description:
            return fetch_api_data()
        elif "clone git repo" in task_description:
            return clone_git_repo()
        elif "run sql query" in task_description:
            return run_sql_query()
        elif "scrape website" in task_description:
            return scrape_website()
        elif "resize image" in task_description:
            return resize_image()
        elif "transcribe audio" in task_description:
            return transcribe_audio()
        elif "convert markdown" in task_description:
            return convert_markdown()
        elif "filter csv" in task_description:
            return filter_csv()
        elif "generate index" in task_description:
            return generate_markdown_index()
        elif "run datagen" in task_description:
            return run_datagen()
        elif "extract logs" in task_description:
            return extract_recent_logs()
        else:
            return "Task not supported", 400
    except Exception as e:
        return str(e), 500
    
def format_file():
    subprocess.run(["npx", "prettier", "--write", f"{data_dir}/format.md"], check=True)
    return "File formatted", 200

def count_wednesdays():
    with open(f"{data_dir}/dates.txt", "r") as f:
        dates = f.readlines()
    wednesday_count = sum(1 for date in dates if datetime.strptime(date.strip(), "%Y-%m-%d").weekday() == 2)
    with open(f"{data_dir}/dates-wednesdays.txt", "w") as f:
        f.write(str(wednesday_count))
    return "Wednesdays counted", 200

def sort_contacts():
    with open(f"{data_dir}/contacts.json", "r") as f:
        contacts = json.load(f)
    contacts.sort(key=lambda x: (x["last_name"], x["first_name"]))
    with open(f"{data_dir}/contacts-sorted.json", "w") as f:
        json.dump(contacts, f, indent=2)
    return "Contacts sorted", 200

def query_ticket_sales():
    conn = sqlite3.connect(f"{data_dir}/ticket-sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
    total_sales = cursor.fetchone()[0] or 0
    with open(f"{data_dir}/ticket-sales-gold.txt", "w") as f:
        f.write(str(total_sales))
    conn.close()
    return "Ticket sales queried", 200

def extract_email():
    with open(f"{data_dir}/email.txt", "r") as f:
        email_content = f.read()
    response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": f"Extract the sender's email: {email_content}"}])
    email_address = response["choices"][0]["message"]["content"].strip()
    with open(f"{data_dir}/email-sender.txt", "w") as f:
        f.write(email_address)
    return "Email extracted", 200

def extract_card_number():
    img = Image.open(f"{data_dir}/credit-card.png")
    card_number = pytesseract.image_to_string(img).replace(" ", "").strip()
    with open(f"{data_dir}/credit-card.txt", "w") as f:
        f.write(card_number)
    return "Card number extracted", 200

def find_similar_comments():
    with open(f"{data_dir}/comments.txt", "r") as f:
        comments = f.readlines()
    pairs = [(a, b, difflib.SequenceMatcher(None, a, b).ratio()) for a in comments for b in comments if a != b]
    most_similar = max(pairs, key=lambda x: x[2])[:2]
    with open(f"{data_dir}/comments-similar.txt", "w") as f:
        f.write("\n".join(most_similar))
    return "Similar comments found", 200

def fetch_api_data():
    response = requests.get("https://jsonplaceholder.typicode.com/posts")
    with open(f"{data_dir}/api_data.json", "w") as f:
        json.dump(response.json(), f, indent=2)
    return "API data fetched", 200

def clone_git_repo():
    subprocess.run(["git", "clone", "https://github.com/example/repo.git", f"{data_dir}/repo"], check=True)
    return "Git repo cloned", 200

def run_sql_query():
    conn = sqlite3.connect(f"{data_dir}/database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    with open(f"{data_dir}/query_result.txt", "w") as f:
        f.write(str(count))
    conn.close()
    return "SQL query executed", 200

def run_datagen():
    subprocess.run(["uv", "pip", "install", "uv"], check=True)
    subprocess.run(["python3", "datagen.py", os.environ.get("USER_EMAIL")], check=True)
    return "Data generated", 200

def extract_recent_logs():
    log_files = sorted((f for f in os.listdir(f"{data_dir}/logs") if f.endswith(".log")), key=lambda x: os.path.getmtime(f"{data_dir}/logs/{x}"), reverse=True)[:10]
    with open(f"{data_dir}/logs-recent.txt", "w") as f:
        for log in log_files:
            with open(f"{data_dir}/logs/{log}") as lf:
                f.write(lf.readline())
    return "Recent logs extracted", 200

def generate_markdown_index():
    index = {}
    for root, _, files in os.walk(f"{data_dir}/docs"):
        for file in files:
            if file.endswith(".md"):
                with open(os.path.join(root, file), "r") as md_file:
                    for line in md_file:
                        if line.startswith("# "):
                            index[file] = line[2:].strip()
                            break
    with open(f"{data_dir}/docs/index.json", "w") as f:
        json.dump(index, f, indent=2)
    return "Markdown index generated", 200

def convert_markdown():
    input_path = f"{data_dir}/input.md"
    output_path = f"{data_dir}/output.html"
    with open(input_path, "r") as f:
        html_content = markdown.markdown(f.read())
    with open(output_path, "w") as f:
        f.write(html_content)
    return "Markdown converted", 200

def transcribe_audio():
    model = whisper.load_model("base")
    result = model.transcribe(f"{data_dir}/audio.mp3")
    with open(f"{data_dir}/audio-transcript.txt", "w") as f:
        f.write(result["text"])
    return "Audio transcribed", 200

def scrape_website():
    url = "https://example.com"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    with open(f"{data_dir}/scraped_data.txt", "w") as f:
        f.write(soup.prettify())
    return "Website scraped", 200

def resize_image():
    input_path = f"{data_dir}/image.png"
    output_path = f"{data_dir}/image_resized.png"
    img = Image.open(input_path)
    img = img.resize((200, 200))
    img.save(output_path)
    return "Image resized", 200

def filter_csv():
    input_path = f"{data_dir}/data.csv"
    output_path = f"{data_dir}/filtered.json"
    with open(input_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        filtered_data = [row for row in reader if row.get("status") == "active"]
    with open(output_path, "w") as jsonfile:
        json.dump(filtered_data, jsonfile, indent=2)
    return "CSV filtered", 200

@app.route("/run", methods=["POST"])
def run_task():
    task = request.args.get("task")
    if not task:
        return "Missing task description", 400
    return execute_task(task)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

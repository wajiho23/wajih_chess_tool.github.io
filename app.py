from flask import Flask, request, jsonify, send_file
import time
import requests

app = Flask(__name__)

progress_data = {}

def fetch_pgn(username, year, month):
    url = f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02d}/pgn"
    headers = {'User-Agent': 'username: your_username, email: your_email@example.com'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.text
    else:
        return None

def save_pgn_to_file(pgn_data, filename):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(pgn_data)

def get_combined_pgn(username, start_year, start_month, end_year, stop_month):
    output_filename = f"{username}_games.pgn"
    all_pgn = ""
    total_months = ((end_year - start_year) * 12) + (stop_month - start_month + 1)
    processed = 0

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if (year == start_year and month < start_month) or (year == end_year and month > stop_month):
                continue

            print(f"Fetching games for {year}-{month:02d}...")
            pgn = fetch_pgn(username, year, month)
            if pgn:
                all_pgn += pgn + "\n\n"

            processed += 1
            progress_data[username] = int((processed / total_months) * 100)
            time.sleep(1)  
    
    save_pgn_to_file(all_pgn, output_filename)
    progress_data[username] = 100
    return output_filename

@app.route("/download_pgn", methods=["GET"])
def download_pgn():
    username = request.args.get("username")
    start_year = int(request.args.get("start_year", 2024))
    start_month = int(request.args.get("start_month", 1))
    end_year = int(request.args.get("end_year", 2025))
    stop_month = int(request.args.get("stop_month", 12))

    if not username:
        return jsonify({"error": "Missing username"}), 400

    filename = get_combined_pgn(username, start_year, start_month, end_year, stop_month)
    return send_file(filename, as_attachment=True)

@app.route("/progress", methods=["GET"])
def get_progress():
    username = request.args.get("username")
    progress = progress_data.get(username, 0)
    return jsonify({"progress": progress})

if __name__ == "__main__":
    app.run(debug=True)

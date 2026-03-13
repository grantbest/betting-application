from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)
DATA_DIR = "data"

@app.route('/api/v1/teams', methods=['GET'])
def get_teams():
    with open(f"{DATA_DIR}/teams.json", "r") as f:
        return jsonify(json.load(f))

@app.route('/api/v1/schedule', methods=['GET'])
def get_schedule():
    # Ignore the date parameter, always return our snapshot schedule
    with open(f"{DATA_DIR}/schedule.json", "r") as f:
        data = json.load(f)
        # Update the 'dates' to today so the engine thinks they are live
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        if data.get('dates'):
            data['dates'][0]['date'] = today
            for game in data['dates'][0].get('games', []):
                # Set status to 'Live' for all replayed games
                game['status']['abstractGameState'] = 'Live'
        return jsonify(data)

@app.route('/api/v1/game/<game_id>/feed/live', methods=['GET'])
def get_game_feed(game_id):
    path = f"{DATA_DIR}/game_{game_id}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Game not found"}), 404

@app.route('/api/v1/teams/<team_id>/stats', methods=['GET'])
def get_team_stats(team_id):
    path = f"{DATA_DIR}/stats_{team_id}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Stats not found"}), 404

if __name__ == '__main__':
    print("MLB Mock API Running on port 5000...")
    app.run(host='0.0.0.0', port=5000)

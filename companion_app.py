from flask import Flask, jsonify, request
import threading

app = Flask(__name__)

# VR library with type; only 'game' will be exposed
VR_LIBRARY = [
    {"name": "Beat Saber", "package": "com.beatsaber", "type": "game"},
    {"name": "Half-Life: Alyx", "package": "com.hla", "type": "game"},
    {"name": "UG", "package": "com.ug", "type": "game"},
    {"name": "Oculus Settings", "package": "com.oculus.settings", "type": "system"}  # ignored
]

running_games = set()

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "online"}), 200

@app.route('/library', methods=['GET'])
def library():
    """Return only game package names"""
    packages = [g['package'] for g in VR_LIBRARY if g['type'] == 'game']
    return jsonify(packages), 200

@app.route('/launch', methods=['POST'])
def launch():
    data = request.get_json()
    package_name = data.get('package')

    # Validate game
    game = next((g for g in VR_LIBRARY if g['package'].lower() == package_name.lower() and g['type'] == 'game'), None)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Launch asynchronously
    def run_game():
        print(f"Launching {package_name}...")
        running_games.add(package_name)
        import time
        time.sleep(10)  # placeholder for actual launch
        running_games.discard(package_name)

    threading.Thread(target=run_game).start()
    return jsonify({"message": f"Launching {package_name}"}), 200

@app.route('/end', methods=['POST'])
def end():
    data = request.get_json()
    package_name = data.get('package')

    if package_name not in running_games:
        return jsonify({"error": "Game not running"}), 400

    print(f"Ending {package_name}...")
    running_games.discard(package_name)
    return jsonify({"message": f"Ended {package_name}"}), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

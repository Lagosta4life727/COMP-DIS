import socket
import json
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

DATA_SERVICE_HOST = 'data-service'
DATA_SERVICE_PORT = 5000


def socket_request(payload: dict):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((DATA_SERVICE_HOST, DATA_SERVICE_PORT))
        s.sendall(json.dumps(payload).encode('utf-8'))
        s.shutdown(socket.SHUT_WR)

        chunks = []
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
        s.close()

        raw = b''.join(chunks).decode('utf-8')
        return json.loads(raw) if raw else None
    except Exception as e:
        logging.error(f"Socket error: {e}")
        return None

@app.route('/api/users', methods=['GET'])
def get_all_users():
    data = socket_request({"action": "get_all_users"})
    return jsonify(data), 200


@app.route('/api/users/<username>', methods=['GET'])
def get_user(username):
    data = socket_request({"action": "get_user", "username": username})
    if data is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(data), 200


@app.route('/api/users', methods=['POST'])
def create_user():
    body = request.get_json(force=True)
    resp = socket_request({"action": "append_user", "data": body})
    return jsonify(resp), 201


@app.route('/api/users/<username>', methods=['PUT'])
def update_user(username):
    body = request.get_json(force=True)
    resp = socket_request({"action": "update_user", "username": username, "data": body})
    return jsonify(resp), 200


@app.route('/api/lojas', methods=['GET'])
def get_all_lojas():
    data = socket_request({"action": "get_all_lojas"})
    return jsonify(data), 200


@app.route('/api/lojas/<int:loja_id>', methods=['GET'])
def get_loja(loja_id):
    data = socket_request({"action": "get_loja", "id": loja_id})
    if data is None:
        return jsonify({"error": "Loja not found"}), 404
    return jsonify(data), 200


@app.route('/api/lojas', methods=['POST'])
def create_loja():
    body = request.get_json(force=True)
    resp = socket_request({"action": "append_loja", "data": body})
    return jsonify(resp), 201


@app.route('/api/lojas/<int:loja_id>', methods=['PUT'])
def update_loja(loja_id):
    body = request.get_json(force=True)
    resp = socket_request({"action": "update_loja", "id": loja_id, "data": body})
    return jsonify(resp), 200


@app.route('/api/lojas/<int:loja_id>', methods=['DELETE'])
def delete_loja(loja_id):
    resp = socket_request({"action": "delete_loja", "id": loja_id})
    return jsonify(resp), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

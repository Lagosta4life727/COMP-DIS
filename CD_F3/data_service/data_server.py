import socket
import json
import threading

def load_json(file):
    with open(file, encoding='utf-8') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4)

users = load_json('utilizadores.json')
for u in users:
    u['estado'] = 'inativo'
save_json('utilizadores.json', users)

def append_user(file, obj):
    data = load_json(file)
    data.append(obj)
    save_json(file, data)
    
def append_loja(file, loja):
    data = load_json(file)

    if 'lojas' not in data:
        data['lojas'] = []

    data['lojas'].append(loja)
    save_json(file, data)

def handle_client(conn):
    try:
        chunks = []
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
            
        req_str = b''.join(chunks).decode('utf-8')
        if not req_str:
            return
            
        req = json.loads(req_str)
        action = req.get('action')
        
        if action == 'get_all_users':
            resp = load_json('utilizadores.json')
        elif action == 'get_all_lojas':
            resp = load_json('dados.json')
        elif action == 'get_user':
            users = load_json('utilizadores.json')
            username = req.get('username')
            resp = next((u for u in users if u.get('user') == username), None)
        elif action == 'get_loja':
            db = load_json('dados.json')
            lojas = db.get('lojas', [])
            loja_id = req.get('id')
            resp = next((l for l in lojas if l.get('id') == loja_id), None)
        elif action == 'append_user':
            append_user('utilizadores.json', req.get('data'))
            resp = {"status": "ok"}
        elif action == 'append_loja':
            db = load_json('dados.json')
            lojas = db.get('lojas', [])
            novo_id = max((l.get('id', 0) for l in lojas), default=0) + 1
            loja_nova = req.get('data')
            loja_nova['id'] = novo_id
            append_loja('dados.json', loja_nova)
            resp = {"status": "ok", "id": novo_id}
        elif action == 'update_user':
            users = load_json('utilizadores.json')
            for i, u in enumerate(users):
                if u.get('user') == req.get('username'):
                    users[i] = req.get('data')
                    break
            save_json('utilizadores.json', users)
            resp = {"status": "ok"}
        elif action == 'update_loja':
            db = load_json('dados.json')
            for i, l in enumerate(db.get('lojas', [])):
                if l.get('id') == req.get('id'):
                    db['lojas'][i] = req.get('data')
                    break
            save_json('dados.json', db)
            resp = {"status": "ok"}
        elif action == 'delete_loja':
            db = load_json('dados.json')
            db['lojas'] = [l for l in db.get('lojas', []) if l.get('id') != req.get('id')]
            save_json('dados.json', db)
            resp = {"status": "ok"}
        else:
            resp = {"status": "error", "msg": "Unknown action"}
        
        conn.sendall(json.dumps(resp).encode('utf-8'))
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5000))
    server.listen(5)
    print("Socket server listening on port 5000")
    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(conn,))
        t.start()

if __name__ == '__main__':
    main()
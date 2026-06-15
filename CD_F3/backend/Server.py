from flask import Flask, redirect, send_file, request, render_template, session
import os
import logging
import json
import re
import requests as http
import threading
import paho.mqtt.client as mqtt

UPLOAD_FOLDER = './static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

vatRegEx = r"^[\w]{3,20}$"
passwordRegEx = r"^[\w]{3,7}$"

REST_API_BASE = 'http://rest-api:5001/api'

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'chave'

logging.basicConfig(level=logging.DEBUG)

dados_mqtt_socket = {
    "voltage": 0,
    "current": 0,
    "power": 0,
    "energy": 0,
    "frequency": 0,
    "powerFactor": 0,
    "time": "",
    "latitude": 0,
    "longitude": 0
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def api_get(path):
    try:
        r = http.get(f"{REST_API_BASE}{path}", timeout=5)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.error(f"REST GET {path} error: {e}")
        return None


def api_post(path, body):
    try:
        r = http.post(f"{REST_API_BASE}{path}", json=body, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.error(f"REST POST {path} error: {e}")
        return None


def api_put(path, body):
    try:
        r = http.put(f"{REST_API_BASE}{path}", json=body, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.error(f"REST PUT {path} error: {e}")
        return None


def api_delete(path):
    try:
        r = http.delete(f"{REST_API_BASE}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.error(f"REST DELETE {path} error: {e}")
        return None

def on_connect(client, userdata, flags, rc):
    logging.info(f"Conectado ao Broker MQTT com código de resultado: {rc}")
    # Subscreve ao tópico do Socket (energia) descrito no PDF 08-MQTT-IoT
    client.subscribe("/power")

def on_message(client, userdata, msg):
    global dados_mqtt_socket
    try:
        payload = msg.payload.decode('utf-8')
        dados = json.loads(payload)
        dados_mqtt_socket.update(dados)
        logging.debug(f"MQTT Data atualizada: {dados_mqtt_socket}")
    except Exception as e:
        logging.error(f"Erro ao processar mensagem MQTT: {e}")

def iniciar_mqtt():
    cliente_mqtt = mqtt.Client()
    cliente_mqtt.on_connect = on_connect
    cliente_mqtt.on_message = on_message
    try:
        # Endereço do broker fornecido no PDF
        cliente_mqtt.connect("cjsg.ddns.net", 1883, 60)
        cliente_mqtt.loop_forever()
    except Exception as e:
        logging.error(f"Falha ao ligar ao Broker MQTT: {e}")

thread_mqtt = threading.Thread(target=iniciar_mqtt, daemon=True)
thread_mqtt.start()

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/Login')
    username = session['username']
    if not username:
        return redirect('/Login')
    # Renderiza o novo template do dashboard passando o utilizador logado
    return render_template('dashboard.html', username=username)

@app.route('/api/iot/socket')
def api_iot_socket():
    # Endpoint interno para o JavaScript do Front-end ler os dados MQTT que o Python recolheu
    return jsonify(dados_mqtt_socket)


@app.route('/')
def getRoot():
    return render_template('index.html')


@app.route('/favicon.ico')
def getFavicon():
    return send_file("./static/favicon.ico", as_attachment=True, max_age=1)


@app.route('/Registo')
def Registo():
    return render_template('Registo.html')


@app.route('/doRegisto', methods=['POST'])
def doRegisto():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('passwordName')
    confirm_password = request.form.get('confirmPassword')

    usernameCheck = re.search(vatRegEx, username or '')
    passwordCheck = re.search(passwordRegEx, password or '')

    if not username or not email or not password or not confirm_password:
        return render_template('dadosInvalidos.html', errorMessage="Todos os dados são obrigatórios", redirectURL="/Registo")
    if not usernameCheck or not passwordCheck:
        return render_template('dadosInvalidos.html', errorMessage="Password inválida", redirectURL="/Registo")
    if confirm_password != password:
        return render_template('dadosInvalidos.html', errorMessage="A confirmação tem de ser igual à password", redirectURL="/Registo")

    users = api_get('/users') or []
    for u in users:
        if u['user'] == username:
            return render_template('dadosInvalidos.html', errorMessage="Username já utilizado", redirectURL="/Registo")
        if u['email'] == email:
            return render_template('dadosInvalidos.html', errorMessage="Email já utilizado", redirectURL="/Registo")

    novo_user = {"user": username, "password": password, "email": email, "estado": "inativo"}
    api_post('/users', novo_user)

    return render_template('index.html')


@app.route('/Login')
def Login():
    return render_template('Login.html')


@app.route('/doLogin', methods=['POST'])
def doLogin():
    username = request.form.get('vatName')
    password = request.form.get('passwordName')

    user_data = api_get(f'/users/{username}')
    if user_data and user_data.get('password') == password:
        if user_data.get('estado') != 'ativo':
            user_data['estado'] = 'ativo'
            api_put(f'/users/{username}', user_data)
        session['username'] = username
        return redirect('/showLojas', code=302)

    return render_template('dadosInvalidos.html', errorMessage="Dados inválidos ou incorretos", redirectURL="/Login")

@app.route('/Logout')
def Logout():
    username = request.args.get('username', '')
    if username:
        user_data = api_get(f'/users/{username}')
        if user_data:
            user_data['estado'] = 'inativo'
            api_put(f'/users/{username}', user_data)
        session.pop('username', None)
    return redirect('/', code=302)


@app.route('/showLojas')
def showLojas():
    if 'username' not in session:
        return redirect('/Login')
    username = session['username']
    categoria_selecionada = request.args.get('categoria', '').strip()
    nome_procurado = request.args.get('nome', '').strip()

    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    lojas_por_pagina = 5

    db = api_get('/lojas') or {}
    lojas = db.get('lojas', []) if isinstance(db, dict) else db

    if categoria_selecionada:
        lojas = [l for l in lojas if l.get('categoria', '') == categoria_selecionada]
    if nome_procurado:
        lojas = [l for l in lojas if nome_procurado.lower() in l.get('nome', '').lower()]

    total_lojas = len(lojas)
    start = (page - 1) * lojas_por_pagina
    lojas_pagina = lojas[start:start + lojas_por_pagina]
    total_paginas = (total_lojas + lojas_por_pagina - 1) // lojas_por_pagina

    all_db = api_get('/lojas') or {}
    all_lojas = all_db.get('lojas', []) if isinstance(all_db, dict) else all_db
    categorias = sorted({l.get('categoria', '') for l in all_lojas if l.get('categoria')})

    lojas_json = json.dumps(lojas_pagina)

    return render_template('Lojas.html', lojas=lojas_pagina, lojas_json=lojas_json,
                           categorias=categorias, categoria_selecionada=categoria_selecionada,
                           nome_procurado=nome_procurado, username=username,
                           page=page, total_paginas=total_paginas)


@app.route('/manageLojas')
def manageLojas():
    if 'username' not in session:
        return redirect('/Login')
    username = session['username']
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    lojas_por_pagina = 5

    db = api_get('/lojas') or {}
    lojas = db.get('lojas', []) if isinstance(db, dict) else db

    total_lojas = len(lojas)
    start = (page - 1) * lojas_por_pagina
    end = start + lojas_por_pagina
    lojas_pagina = lojas[start:end]
    
    total_paginas = (total_lojas + lojas_por_pagina - 1) // lojas_por_pagina

    loja_id_edicao = request.args.get('edit_id')
    loja_data = None
    if loja_id_edicao:
        loja_data = api_get(f'/lojas/{loja_id_edicao}')

    return render_template('manageLojas.html', lojas=lojas_pagina, loja_data=loja_data,username=username, page=page, total_paginas=total_paginas)

@app.route('/saveLoja', methods=['POST'])
def saveLoja():
    if 'username' not in session:
        return redirect('/Login')    
    loja_id = request.form.get('loja_id')
    current_foto = request.form.get('current_foto', '')
    
    page = request.form.get('page', '1')

    foto_file = current_foto
    file = request.files.get('foto')
    if file and file.filename != '' and allowed_file(file.filename):
        foto_file = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_file))

    loja_data = {
        'nome': request.form.get('nome'),
        'categoria': request.form.get('categoria'),
        'link': request.form.get('link'),
        'foto': foto_file,
        'latitude': float(request.form.get('latitude') or 0),
        'longitude': float(request.form.get('longitude') or 0),
        'imagens': [],
        'video': ''
    }

    if loja_id and loja_id != '':
        loja_id = int(loja_id)
        loja_atual = api_get(f'/lojas/{loja_id}')
        if loja_atual:
            loja_data['id'] = loja_id
            loja_data['imagens'] = loja_atual.get('imagens', [])
            loja_data['video'] = loja_atual.get('video', '')
            api_put(f'/lojas/{loja_id}', loja_data)
    else:
        api_post('/lojas', loja_data)

    return redirect(f'/manageLojas?page={page}')


@app.route('/editLoja/<int:loja_id>', methods=['GET'])
def editLoja(loja_id):
    if 'username' not in session:
        return redirect('/Login')
    username = session['username']
    
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    lojas_por_pagina = 5

    db = api_get('/lojas') or {}
    lojas_todas = db.get('lojas', []) if isinstance(db, dict) else db
    
    loja_data = next((l for l in lojas_todas if l.get('id') == loja_id), None)
    
    total_lojas = len(lojas_todas)
    start = (page - 1) * lojas_por_pagina
    lojas_pagina = lojas_todas[start:start + lojas_por_pagina]
    total_paginas = (total_lojas + lojas_por_pagina - 1) // lojas_por_pagina

    return render_template('manageLojas.html', lojas=lojas_pagina, loja_data=loja_data, username=username, page=page, total_paginas=total_paginas)


@app.route('/deleteLoja/<int:loja_id>', methods=['GET'])
def deleteLoja(loja_id):
    if 'username' not in session:
        return redirect('/Login')
     
    page = request.args.get('page', '1')
    api_delete(f'/lojas/{loja_id}')

    return redirect(f'/manageLojas?page={page}')


@app.route('/imagensLoja/<int:loja_id>')
def imagensLoja(loja_id):
    if 'username' not in session:
        return redirect('/Login')
    username = session['username']
    loja_data = api_get(f'/lojas/{loja_id}')
    if not loja_data:
        return render_template('dadosInvalidos.html',
                               errorMessage=f"Loja com ID {loja_id} não encontrada.",
                               redirectURL=f"/showLojas?username={username}")
    return render_template('imagensLoja.html', username=username, loja=loja_data)


@app.route('/uploadImagens/<int:loja_id>', methods=['POST'])
def uploadImagens(loja_id):
    if 'username' not in session:
        return redirect('/Login')
    username = session['username']
    loja_data = api_get(f'/lojas/{loja_id}')
    if not loja_data:
        return render_template('dadosInvalidos.html',
                               errorMessage=f"Loja com ID {loja_id} não encontrada.",
                               redirectURL=f"/showLojas?username={username}")

    loja_data.setdefault('imagens', [])
    for file in request.files.getlist('imagens'):
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if filename not in loja_data['imagens']:
                loja_data['imagens'].append(filename)

    api_put(f'/lojas/{loja_id}', loja_data)
    return redirect(f'/imagensLoja/{loja_id}?username={username}')


@app.route('/uploadVideo/<int:loja_id>', methods=['POST'])
def uploadVideo(loja_id):
    username = request.args.get('username', '')
    loja_data = api_get(f'/lojas/{loja_id}')
    if not loja_data:
        return render_template('dadosInvalidos.html',
                               errorMessage=f"Loja com ID {loja_id} não encontrada.",
                               redirectURL=f"/showLojas?username={username}")

    file = request.files.get('video')
    if file and file.filename != '' and file.filename.lower().endswith('.mp4'):
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        loja_data['video'] = filename

    api_put(f'/lojas/{loja_id}', loja_data)
    return redirect(f'/imagensLoja/{loja_id}?username={username}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

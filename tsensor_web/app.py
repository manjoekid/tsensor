from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from shared_memory_dict import SharedMemoryDict
import os

#import test_serial

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Mock user data (replace with a database in a real application)
users = {
    'admin@admin.com': generate_password_hash('password123'),
    'tsensor@admin.com': generate_password_hash('1234'),
}

tsensor_pipe = SharedMemoryDict(name='temperatures', size=4096)
tsensor_pipe["estado"] = True

# Routes
@app.route('/')
def home():
    if 'user' in session:
        return render_template('temperatura.html')
    else:
        return 'Welcome to the home page. <a href="/login">Login</a>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in users and check_password_hash(users[email], password):
            session['user'] = email
            return redirect(url_for('home'))

        return 'Invalid email or password. <a href="/login">Try again</a>'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# Rota para fornecer os dados de temperatura via AJAX
@app.route('/dados_temperatura', methods=['GET'])
def dados_temperatura():
    # Dados de exemplo - 32 temperaturas
    #temperatures = test_serial.read_real_time_temperature()
    temperature = tsensor_pipe["temperature"]
    temperature_max = tsensor_pipe["temperature_max"]
    temperature_min = tsensor_pipe["temperature_min"]
    modo_atual = tsensor_pipe["modo"]
    estado_atual = tsensor_pipe["estado"]
    temperature_media = tsensor_pipe["media"]

    intermed = jsonify({'temperaturas':{'max': temperature_max,
                                        'real': temperature,
                                        'min': temperature_min},
                        'modo': modo_atual,
                        'estado':estado_atual,
                        'media':temperature_media})

    return intermed

@app.route('/alterar_modo', methods=['POST'])
def alterar_modo():
    novo_modo = request.json.get('modo')
    if novo_modo in ['ligado', 'desligado', 'auto']:
        tsensor_pipe["modo"] = novo_modo
        return jsonify({'message': f'Modo alterado para {novo_modo}'})
    else:
        return jsonify({'error': 'Modo inválido'}), 400

@app.route('/searchFiles')
def search_files():
    directory_path = '../tsensor_py/output/'  # Update with the path to your directory
    files = os.listdir(directory_path)
    
    # Filter files based on criteria (e.g., creation time)
    filtered_files = [file for file in files if meets_criteria(os.path.join(directory_path, file))]
    
    return jsonify(filtered_files)

def meets_criteria(file_path):
    # Implement your filtering criteria here (e.g., creation time)
    # For example, you can compare the creation time of the file with your start and stop times
    # Here's a placeholder example that always returns True
    return True

@app.route('/downloadFile/<filename>')
def download_file(filename):
    directory_path = '../tsensor_py/output/'  # Update with the path to your directory
    file_path = os.path.join(directory_path, filename)
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)



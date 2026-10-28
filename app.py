from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_flash_messages'

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='', # Insira sua senha do MySQL Workbench se houver
        database='clinica_veterinaria'
    )

# --- LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if usuario:
            return redirect(url_for('index'))
        else:
            flash('E-mail ou senha incorretos.', 'error')
            
    return render_template('login.html')

# --- DASHBOARD / AGENDAMENTOS ---
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id, a.data_hora, a.motivo, t.nome AS nome_tutor, t.telefone, p.nome_pet 
        FROM agendamentos a
        INNER JOIN tutores t ON a.id_tutor = t.id
        INNER JOIN pets p ON a.id_pet = p.id
        ORDER BY a.data_hora ASC;
    """)
    agendamentos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html', agendamentos=agendamentos, usuario="Matheus Bonenti")

@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome FROM tutores")
    tutores = cursor.fetchall()
    cursor.execute("SELECT id, nome_pet, id_tutor FROM pets")
    pets = cursor.fetchall()
    
    if request.method == 'POST':
        data_hora = request.form['data_hora']
        motivo = request.form['motivo']
        id_tutor = request.form['id_tutor']
        id_pet = request.form['id_pet']
        
        cursor.execute("SELECT * FROM agendamentos WHERE data_hora = %s", (data_hora,))
        conflito = cursor.fetchone()
        
        if conflito:
            cursor.close()
            conn.close()
            return render_template('agendar.html', tutores=tutores, pets=pets, erro_horario=True)
        
        cursor.execute("INSERT INTO agendamentos (data_hora, motivo, id_tutor, id_pet) VALUES (%s, %s, %s, %s)", 
                       (data_hora, motivo, id_tutor, id_pet))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
        
    cursor.close()
    conn.close()
    return render_template('agendar.html', tutores=tutores, pets=pets, erro_horario=False)

@app.route('/editar-agendamento/<int:id>', methods=['GET', 'POST'])
def editar_agendamento(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        data_hora = request.form['data_hora']
        motivo = request.form['motivo']
        
        cursor.execute("SELECT * FROM agendamentos WHERE data_hora = %s AND id != %s", (data_hora, id))
        conflito = cursor.fetchone()
        
        if conflito:
            cursor.close()
            conn.close()
            return render_template('editar_agendamento.html', erro_horario=True)
            
        cursor.execute("UPDATE agendamentos SET data_hora = %s, motivo = %s WHERE id = %s", (data_hora, motivo, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
        
    cursor.execute("SELECT * FROM agendamentos WHERE id = %s", (id,))
    agendamento = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('editar_agendamento.html', agendamento=agendamento, erro_horario=False)

@app.route('/deletar-agendamento/<int:id>')
def deletar_agendamento(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agendamentos WHERE id = %s", (id,))
    conn.commit()  # Garante que salva no banco
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

# --- USUÁRIOS (CRUD) ---
@app.route('/usuarios')
def listar_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, email FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/cadastrar-usuario', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('listar_usuarios'))
    return render_template('cadastrar_usuario.html')

@app.route('/editar-usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        cursor.execute("UPDATE usuarios SET nome = %s, email = %s, senha = %s WHERE id = %s", (nome, email, senha, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('listar_usuarios'))
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/deletar-usuario/<int:id>')
def deletar_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit()  # Garante que salva no banco
    cursor.close()
    conn.close()
    return redirect(url_for('listar_usuarios'))

# --- TUTORES (CRUD) ---
@app.route('/tutores')
def listar_tutores():
    busca = request.args.get('busca', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if busca:
        cursor.execute("SELECT * FROM tutores WHERE nome LIKE %s OR telefone LIKE %s", (f"%{busca}%", f"%{busca}%"))
    else:
        cursor.execute("SELECT * FROM tutores")
    tutores = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('tutor_info.html', tutores=tutores, busca=busca)

@app.route('/cadastrar-tutor', methods=['GET', 'POST'])
def cadastrar_tutor():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf'] 
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tutores (nome, cpf_criptografado, telefone, endereco) VALUES (%s, %s, %s, %s)", 
                       (nome, f"enc_{cpf}", telefone, endereco))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('listar_tutores'))
    return render_template('cadastrar_tutor.html')

@app.route('/editar-tutor/<int:id>', methods=['GET', 'POST'])
def editar_tutor(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        cursor.execute("UPDATE tutores SET nome = %s, telefone = %s, endereco = %s WHERE id = %s", (nome, telefone, endereco, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('listar_tutores'))
    cursor.execute("SELECT * FROM tutores WHERE id = %s", (id,))
    tutor = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('editar_tutor.html', tutor=tutor)

@app.route('/deletar-tutor/<int:id>')
def deletar_tutor(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Nota: Como o banco tem ON DELETE CASCADE, ao apagar o tutor, os pets e agendamentos dele somem automaticamente
    cursor.execute("DELETE FROM tutores WHERE id = %s", (id,))
    conn.commit()  # Garante que salva no banco
    cursor.close()
    conn.close()
    return redirect(url_for('listar_tutores'))

# --- ANIMAIS / PETS (CRUD com Categorias) ---
@app.route('/animais')
def listar_animais():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.nome_pet, p.especie, p.raca, p.categoria, t.nome AS nome_tutor 
        FROM pets p
        INNER JOIN tutores t ON p.id_tutor = t.id
    """)
    animais = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('animais.html', animais=animais)

@app.route('/cadastrar-animal', methods=['GET', 'POST'])
def cadastrar_animal():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome FROM tutores")
    tutores = cursor.fetchall()
    
    if request.method == 'POST':
        nome_pet = request.form['nome_pet']
        especie = request.form['especie']
        raca = request.form['raca']
        categoria = request.form['categoria']
        id_tutor = request.form['id_tutor']
        
        cursor.execute("INSERT INTO pets (nome_pet, especie, raca, categoria, id_tutor) VALUES (%s, %s, %s, %s, %s)", 
                       (nome_pet, especie, raca, categoria, id_tutor))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('listar_animais'))
        
    cursor.close()
    conn.close()
    return render_template('cadastrar_animal.html', tutores=tutores)

@app.route('/editar-animal/<int:id>', methods=['GET', 'POST'])
def editar_animal(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome FROM tutores")
    tutores = cursor.fetchall()
    
    if request.method == 'POST':
        nome_pet = request.form['nome_pet']
        especie = request.form['especie']
        raca = request.form['raca']
        categoria = request.form['categoria']
        id_tutor = request.form['id_tutor']
        
        cursor.execute("UPDATE pets SET nome_pet = %s, especie = %s, raca = %s, categoria = %s, id_tutor = %s WHERE id = %s", 
                       (nome_pet, especie, raca, categoria, id_tutor, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('listar_animais'))
        
    cursor.execute("SELECT * FROM pets WHERE id = %s", (id,))
    animal = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('editar_animal.html', animal=animal, tutores=tutores)

@app.route('/deletar-animal/<int:id>')
def deletar_animal(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pets WHERE id = %s", (id,))
    conn.commit()  # Garante que salva no banco
    cursor.close()
    conn.close()
    return redirect(url_for('listar_animais'))

if __name__ == '__main__':
    app.run(debug=True)
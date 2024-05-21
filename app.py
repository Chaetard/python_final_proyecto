from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db
from utils import get_items_avail, get_sum_items
import numpy as np
import datetime

app = Flask(__name__)
app.secret_key = "tu_clave_secreta"

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE user=%s', (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['user_id'] = user['id_user']
            session['username'] = user['user']
            session['type'] = user['type']
            return redirect('/')
        else:
            error = True
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        if session['type'] == 1:
            return render_template('admin.html')
        else:
            name = session['username']
            return render_template('index.html', name=name, sumAvailableRooms = get_items_avail("rooms"), sumRooms = get_sum_items("rooms"),sumAvailableComputer = get_items_avail("computer_equipment"), sumComputer = get_sum_items("computer_equipment") )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  
        hashed_password = generate_password_hash(password)

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute('INSERT INTO users (user, password) VALUES (%s, %s)', (username, hashed_password))
        db.commit()
        
        return redirect('/login')
    return render_template('register.html')

@app.route('/salas', methods=['GET', 'POST'])
def listarSalas():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        return render_template('salas.html')
@app.route('/buscar_salas', methods=['POST'])
def buscarSala():
    consulta = request.form['consulta']
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT name_room, available FROM rooms WHERE name_room LIKE %s', (f'%{consulta}%',))
    datos = cursor.fetchall()
    
    resultados = [{'name_room': sala['name_room'], 'available': sala['available']} for sala in datos]
    
    return jsonify(resultados)


@app.route('/buscar_equipos', methods=['POST'])
def buscarEquipo():
    consulta = request.form['consulta']   
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT model FROM computer_equipment')
    datos = cursor.fetchall()
    
    resultados = sorted([model['model'] for model in datos if consulta.lower() in model['model'].lower()])
    
    return jsonify(resultados)

@app.route('/equipos', methods=['GET', 'POST'])
def listarEquipos():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        return render_template('equipos.html')

@app.route('/salir')
def cerrar_sesion():
    session.clear()
    return redirect('/')

@app.route('/alta-equipo' , methods=['GET', 'POST'])
def alta_equipo():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        if session['type'] == 1:
            if request.method == 'POST': 
                model = request.form['model']
                serial = request.form['serial']  

                db = get_db()
                cursor = db.cursor(dictionary=True)

                cursor.execute('INSERT INTO computer_equipment (model, serial) VALUES (%s, %s)', (model, serial))
                db.commit()
                return redirect('/')
            else:
                return render_template('/alta-equipos.html')
        else:
            return redirect('/')

@app.route('/alta-sala' , methods=['GET', 'POST'])
def alta_sala():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        if session['type'] == 1:
            if request.method == 'POST': 
                name = request.form['name']
                capacity = request.form['capacity']  

                db = get_db()
                cursor = db.cursor(dictionary=True)

                cursor.execute('INSERT INTO rooms (name_room, capacity) VALUES (%s, %s)', (name, capacity))
                db.commit()
                return redirect('/')
            else:
                return render_template('/alta-sala.html')
        else:
            return redirect('/')

@app.route('/lista-reservaciones')
def lista_reservaciones():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        if session['type'] == 1:
            if request.method == 'POST': 
                return redirect('/')
            else:
                db = get_db()
                cursor = db.cursor(dictionary=True)
                query = "SELECT r.* , u.user FROM reservations r INNER JOIN users u where r.id_user = u.id_user" 
                cursor.execute(query)
                reservations = cursor.fetchall()
                return render_template('/reservaciones.html', reservations = reservations )
        else:
            return redirect('/')
    
@app.route('/mi-perfil')
def mi_perfil():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        query = "SELECT r.*, u.user FROM reservations r INNER JOIN users u ON r.id_user = u.id_user WHERE r.id_user = %s"
        cursor.execute(query, (session['user_id'],))  
        reservations = cursor.fetchall()
        reservationsOrdenado = np.roll(reservations, 2)
        current_time = datetime.datetime.now()
        return render_template('perfil.html', reservations=reservationsOrdenado, current_time=current_time)  
    
@app.route('/reservar-sala', methods=['GET', 'POST'])
def reservar_sala():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        if request.method == 'POST': 
                id_type = request.form['id_type']
                day = request.form['day']
                time_start = request.form['time_start']
                time_end = request.form['time_end']
                db = get_db()
                cursor = db.cursor(dictionary=True)
                #CALL insert_reservation(1, 'room', 101, NOW(), '09:00:00', '10:00:00');
                cursor.execute("CALL insert_reservation(%s, %s, %s,%s,%s,%s)", (session['user_id'], 'room', id_type, day, time_start, time_end ))
                db.commit()
                return redirect('/')
        else:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            query = "SELECT name_room, id_room from rooms WHERE available = 1"
            cursor.execute(query)
            rooms = cursor.fetchall()
            return render_template('/salasRev.html', rooms = rooms)
       

@app.route('/cancelar-reserva/<int:reservation_id>', methods=['GET', 'POST'])
def cancelarReserva(reservation_id):
    if not session.get('logged_in'):
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("CALL cancelar_reservacion(%s)", (reservation_id,))
        db.commit()  
    except Exception as e:
        db.rollback()  
        print(f"Error: {e}")
        return "Algo Ocurrio..."
    finally:
       
        cursor.close()
        db.close()
        return redirect('/mi-perfil') 

    return redirect('/')

    

    



@app.route('/reservar-equipo', methods=['GET', 'POST'])
def reservar_equipo():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        if request.method == 'POST': 
            id_type = request.form['id_type']
            day = request.form['day']
            time_start = request.form['time_start']
            time_end = request.form['time_end']
        
            db = get_db()
            cursor = db.cursor(dictionary=True)
                #CALL insert_reservation(1, 'room', 101, NOW(), '09:00:00', '10:00:00');
            cursor.execute("CALL insert_reservation(%s, %s, %s,%s,%s,%s)", (session['user_id'], 'computer', id_type, day, time_start, time_end ))
            db.commit()
            return redirect('/')

                    
            
            
        else:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            query = "SELECT model, id_equipment from computer_equipment WHERE available = 1"
            cursor.execute(query)
            equip = cursor.fetchall()
            return render_template('/equipmentRev.html', equip = equip)
    
    
    
        

if __name__ == '__main__':
    app.run(debug=True)

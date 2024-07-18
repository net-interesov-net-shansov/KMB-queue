from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask import Flask, render_template, request,redirect,url_for
import mimetypes

# Создаем приложение Flask
app = Flask(__name__)

# Конфигурируем базу данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///queue.db'
app.config['SECRET_KEY'] = 'secret!'

# Создаем экземпляр SocketIO
socketio = SocketIO(app)

# Создаем экземпляр SQLAlchemy
db = SQLAlchemy(app)


# Определяем модели для базы данных
class QueueModel(db.Model):
    # Определяем столбцы для таблицы QueueModel
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    userLastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String, nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    operation = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False, default='waiting')
    current_date = db.Column(db.String(100), nullable=False)

    # Определяем строковое представление экземпляра QueueModel
    def __repr__(self):
        return f"Очередь(номер={self.number}, имя={self.username})"

class OperatorModel(db.Model):
    # Определяем столбцы для таблицы OperatorModel
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    operations = db.Column(db.String(100), nullable=False)

    # Определяем строковое представление экземпляра OperatorModel
    def __repr__(self):
        return f"Менеджер(имя={self.name}, кабинет={self.cabinet}, операции={self.operations})"

class OperationModel(db.Model):
    # Определяем столбцы для таблицы OperationModel
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    operation_name = db.Column(db.String(100), nullable=False)
    operation_code = db.Column(db.String(100), nullable=False)
    cabinet = db.Column(db.String(100), nullable=False)

    # Определяем строковое представление экземпляра OperationModel
    def __repr__(self):
        return f"Операция(название={self.operation}, код={self.operation_code}, кабинет={self.cabinet})"

# Функции для работы с очередью
def create_queue_item(number, username, come):
    # Создаем новый экземпляр QueueModel
    new_queue_item = QueueModel(number=number, username=username, come=come)
    # Добавляем новый экземпляр в сессию базы данных
    db.session.add(new_queue_item)
    # Фиксируем изменения в базе данных
    db.session.commit()
    # Возвращаем новый элемент очереди
    return new_queue_item

def delete_queue_item(number):
    # Получаем элемент очереди с указанным номером
    queue_item = QueueModel.query.get(number)
    if queue_item:
        # Удаляем элемент очереди из базы данных
        db.session.delete(queue_item)
        # Фиксируем изменения в базе данных
        db.session.commit()

# Функции для работы с операторами
def create_operator(name, cabinet, operations):
    # Создаем новый экземпляр OperatorModel
    new_operator = OperatorModel(name=name, cabinet=cabinet, operations=operations)
    # Добавляем новый экземпляр в сессию базы данных
    db.session.add(new_operator)
    # Фиксируем изменения в базе данных
    db.session.commit()
    # Возвращаем нового оператора
    return new_operator

def get_operator():
    # Возвращаем все экземпляры OperatorModel из базы данных
    return OperatorModel.query.all()

# Загрузить очередь из базы данных
def get_queue_items():
    return QueueModel.query.all()

# Сохраняем очередь в базу данных
def save_queue_item(number, username, birthdate_str, operation, phone, userLastname, current_date):
    birthdate_obj = datetime.strptime(birthdate_str, '%Y-%m-%d')
    new_item = QueueModel( number=number, username=username, operation=operation , birthdate=birthdate_obj, phone=phone, userLastname=userLastname, current_date=current_date)
    db.session.add(new_item)
    db.session.commit()


# Список операторов
operators = []
# очередь пользователей
queue = []


# Работаем с socket
# проверка подключения
@socketio.on('connect')
def connect(auth):
    global queue,operators
    with app.app_context():
        queue = get_queue_items()
        operators_data = get_operator()
    operators = [{'id': item.id, 'username': item.username, 'password': item.password, 'operations': item.operations} for item in operators_data]
    queue_data = [{'number': item.number, 'username': item.username, 'birthdate': item.birthdate.strftime('%Y-%m-%d'), 'operation': item.operation, 'status':item.status, 'phone':item.phone, 'userLastname': item.userLastname} for item in queue]
    emit('queue_update', {'queue': queue_data}, broadcast=True)
    print('Client connected')
    
# проверка отключение
@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

# Удаляем клиента из очереди
@socketio.on('leave_queue')
def leave_queue(data):
    queue.remove(data['number'])
    emit('queue_update', {'queue': queue}, broadcast=True)

def get_latest_number():
    with app.app_context():
        latest_item = db.session.query(QueueModel).order_by(QueueModel.id.desc()).first()
        if latest_item:
            return latest_item.number
        else:
            return None



client_number = get_latest_number()
if client_number == None: client_number = 1
else: client_number += 1
print(client_number)

mimetypes.add_type('audio/mpeg', '.mp3')

# Добавление клиента в очередь
@socketio.on('next_client')
def pers(json):
    global client_number
    print(json)
    username = json['username']
    birthdate = json['birthdate']
    operation = json['operation']
    phone = json['phone']
    userLastname = json['userLastname']
    
    current_date_unformed = date.today()
    current_date = current_date_unformed.strftime('%d.%m')


    # Сохраните нового клиента в базе данных.
    save_queue_item(client_number, username, birthdate, operation, phone, userLastname, current_date)
    with app.app_context():
        queue = get_queue_items()
    queue_data = [{'number': item.number, 'username': item.username, 'birthdate': item.birthdate.strftime('%Y-%m-%d'), 'operation': item.operation,'status': item.status, 'phone': item.phone, 'userLastname': item.userLastname} for item in queue]
    # Отправьте обновленную очередь всем клиентам
    emit('queue_update', {'queue': queue_data}, broadcast=True) 
    emit('person_respons', client_number, broadcast=True)

    while True:
        client_number += 1
        if client_number == 101:
            client_number = 1
        print(client_number)
        break

# обнавление очереди
@socketio.on('queue_update')
def queue_update():
    
    emit('queue_update', {'queue': queue})
    print (queue)

@socketio.on('task_assigned')
def task_assigned(task):
    queue.remove(task)
    emit('queue_update', {'queue': queue})

# прием данных об обновлении менеджера
@socketio.on('assign_cabinet')
def assign_cabinet(data):
    print(data)
    number = int(data['number'])
    cabinet_id = data['cabinetId']
    # Обновите поле операции до значения True для соответствующего элемента очереди.
    queue_item = QueueModel.query.get(number)
    if queue_item:
        queue_item.status = 'True'
        db.session.commit()
        queue = get_queue_items()
    queue_data = [{'number': item.number, 'username': item.username, 'birthdate': item.birthdate.strftime('%Y-%m-%d'), 'operation': item.operation,'status': item.status, 'phone': item.phone, 'userLastname': item.userLastname} for item in queue]
    
    emit('queue_update', {'queue': queue_data}, broadcast=True)# обновление списка очереди

# прием данных об завершении студента
@socketio.on('unassign_cabinet')
def assign_cabinet(data):
    print("Я удаляю")
    print(data)

    number = int(data['number'])
    cabinet_id = data['cabinetId']
    # Обновите поле операции до значения True для соответствующего элемента очереди.
    queue_item = QueueModel.query.get(number)
    if queue_item:
        queue_item.status = 'False'
        db.session.commit()
        queue = get_queue_items()
    queue_data = [{'number': item.number, 'username': item.username, 'birthdate': item.birthdate.strftime('%Y-%m-%d'), 'operation': item.operation,'status': item.status, 'phone': item.phone, 'userLastname': item.userLastname} for item in queue]
    emit('queue_update', {'queue': queue_data}, broadcast=True)# обновление списка очереди

    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Проверьте правильность имени пользователя и пароля
        for operator in operators:
            if operator['username'] == username and operator['password'] == password:
                if (operator['username'] == 'Manager1' and operator['password'] == password) or (operator['username'] == 'Manager2' and operator['password'] == password):
                    return redirect(url_for('manager_page', operator_id=operator['id']))
                else:
                    return redirect(url_for('operator_page', operator_id=operator['id']))
        # Если имя пользователя и пароль неверны, верните сообщение об ошибке.
        return render_template('login.html',error = 'Неверный пароль или логин')
    else:
        return render_template('login.html')

@app.route('/monitor', methods=['GET', 'POST'])
def monitor():
    with app.app_context():
        operators_data = OperationModel.query.all()
    operations = [{'id': item.id, 'operation_name': item.operation_name, 'operation_code': item.operation_code, 'cabinet': item.cabinet} for item in operators_data]
    return render_template('monitor.html',operations=operations)

@app.route('/operator/<int:operator_id>')
def operator_page(operator_id):
    with app.app_context():
        operators_data = OperationModel.query.all()
    operations = [{'id': item.id, 'operation_name': item.operation_name, 'operation_code': item.operation_code, 'cabinet': item.cabinet} for item in operators_data]
    operator = next((o for o in operators if o['id'] == operator_id), None)
    if operator:
        return render_template('operator.html', operator=operator, operations=operations)
    else:
        return 'Operator not found', 404
    
@app.route('/manager/<int:operator_id>', methods=['GET', 'POST'])
def manager_page(operator_id):
    with app.app_context():
        operators_data = OperationModel.query.all()
    operations = [{'id': item.id, 'operation_name': item.operation_name, 'operation_code': item.operation_code, 'cabinet': item.cabinet} for item in operators_data]
    operator = next((o for o in operators if o['id'] == operator_id), None)
    if operator:
        return render_template('manager.html', operator=operator, operations=operations)
    else:
        return 'Operator not found', 404


# @app.route('/maneger', methods=['GET', 'POST'])
# def maneger():
#     operations = OperationModel.query.all()
#     return render_template('maneger.html', operations=operations)

#админ панель
@app.route('/admin')
def admin_index():
    tables = db.metadata.tables.keys()
    return render_template("admin.html", tables=tables)

# вывод таблиц
@app.route("/table/<string:table_name>")
def show_table(table_name):
    table = db.metadata.tables[table_name]
    rows = db.session.execute(table.select()).fetchall()
    return render_template("table.html", table=table, rows=rows)

#добавление записи в таблицу
@app.route("/table/<string:table_name>/add", methods=["GET", "POST"])
def add_row(table_name):
    table = db.metadata.tables[table_name]
    if request.method == "POST":
        data = {}
        for column in table.columns:
            data[column.name] = request.form.get(column.name)
        db.session.execute(table.insert(), data)
        db.session.commit()
        return redirect(url_for("show_table", table_name=table_name))
    return render_template("add.html", table=table)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     socketio.run(app,'172.10.30.89', port=5000)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='172.10.31.83', port=8080)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     socketio.run(app)
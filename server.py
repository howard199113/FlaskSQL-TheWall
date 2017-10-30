from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
app = Flask(__name__)
mysql = MySQLConnector(app,'mydb')
app.secret_key = "ThisIsSecret!"

@app.route('/')
def index():
    
 return render_template('index.html')

@app.route('/register', methods=['POST']) 
def register():
    # print request.form['first_name']
    # print request.form['last_name']
    # print request.form['email']
    # print request.form['password']
    # print request.form['confirm_password']
    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at)VALUES(:first_name, :last_name, :email, :password, NOW(), NOW())"
    
    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': request.form['confirm_password']
    }
    obj_id = mysql.query_db(query,data)
    new_obj_data = {
        "id": obj_id
    }
    stored_user = mysql.query_db("SELECT * FROM users WHERE id=:id", new_obj_data)
    session['id'] = stored_user[0]['id']
    session['first_name'] = stored_user[0]['first_name']

    return redirect('/wall')


@app.route('/login',methods=['POST'])
def login():
    query = "SELECT * FROM users WHERE email=:email"
    data= {
        'email': request.form['email']
    }
    retrieve_record = mysql.query_db(query,data)
    if len(retrieve_record) > 0:
        if request.form['password'] == retrieve_record[0]['password']:
            session['id'] = retrieve_record[0]['id']
            session['first_name'] = retrieve_record[0]['first_name']
            return redirect('/wall')
    return redirect('/')

@app.route('/wall')
def wall():
    if 'id' not in session:
        return redirect('/')
    message = mysql.query_db("SELECT messages.id, message, messages.created_at, user_id, users.first_name, users.last_name FROM messages JOIN users ON users.id = messages.user_id")
    
    comment = mysql.query_db("SELECT comments.comment, comments.created_at, users.first_name, users.last_name, comments.message_id FROM comments JOIN users ON users.id = comments.user_id")
    return render_template('wall.html', all_messages = message, all_comments = comment)

@app.route('/message', methods=['POST'])
def message():
    query = "INSERT INTO messages(message, created_at, updated_at, user_id)VALUE(:message, NOW(), NOW(), :user_id)"
    data = {
        'message': request.form['message'],
        'user_id': session['id']
    }
    mysql.query_db(query,data)
    return redirect('/wall')

@app.route('/comment/<message_id>', methods=['POST'])
def comment(message_id):
    query = "INSERT INTO comments(comment, created_at, updated_at, user_id, message_id)VALUE(:comment, NOW(), NOW(), :user_id, :message_id)"
    data = {
        'comment': request.form['comment'],
        'message_id': message_id,
        'user_id': session['id']
    }
    mysql.query_db(query,data)
    return redirect('/wall')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

 
app.run(debug=True)
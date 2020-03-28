from flask import Flask, render_template, request, jsonify
from cassandra.cluster import Cluster
import json
import requests
import requests_cache
requests_cache.install_cache('gymprogress_app_cache', backend='sqlite', expire_after=36000)
cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session = cluster.connect()

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')
    # return('<h1>Welcome to Gerardo\'s Gym Progress App</h1>')

# Index page, welcome the user 
@app.route('/welcome')
def hello():
    return render_template('index.html')
    # return('<h1>Welcome to Gerardo\'s Gym Progress App</h1>')

# Create a new user for the app from the command line
@app.route('/new_user_cli', methods=['POST'])
def create_new_user():
      
    if not request.json or not "name" in request.json or not "surname" in request.json \
        or not "age" in request.json or not "sex" in request.json or not "weight" in request.json or not "height" in request.json:
        return jsonify({'error':'the new record needs to have name,surname,age,sex,weight,height'}), 400
        
    name =  request.json['name']
    surname = request.json['surname']
    age = int(request.json['age'])
    sex = request.json['sex']
    weight = float(request.json['weight'])
    height = float(request.json['height'])
    
    query = "INSERT INTO gym.users(name,surname,age,sex,weight,height) VALUES ( '{}','{}',{},'{}',{},{})"\
        .format(name,surname,age,sex,weight,height)
    session.execute(query)    
    return jsonify({'message': 'created: /new_user {},{}'.format(name,surname)}), 201

# Create a new user from the browser
@app.route('/new_user_browser', methods=['POST'])
def create_new_user_browser():
    
    name =  request.form['name']
    surname = request.form['surname']
    age = int(request.form['age'])
    sex = request.form['sex']
    weight = float(request.form['weight'])
    height = float(request.form['height'])
    password = request.form['password']

    result = session.execute("""select count(*) from gym.users where name='{}' AND surname='{}'""".format(name,surname))
    if (result.was_applied == 0):

        query = "INSERT INTO gym.users(name,surname,age,sex,weight,height) VALUES ( '{}','{}',{},'{}',{},{})"\
            .format(name,surname,age,sex,weight,height)
        session.execute(query)

        password_query = "INSERT INTO gym.accounts (name,surname,password) VALUES ('{}','{}','{}')".format(name,surname,password)
        session.execute(password_query)

        return "Success",201
    else:
        return jsonify({'error':'User already exists'}), 404
   
#Login from the browser
@app.route('/login_user_browser',methods=['POST'])
def login_browser():

    name =  request.form['name']
    surname = request.form['surname']
    password = request.form['password']

    result = session.execute("""select count(*) from gym.accounts where name='{}' AND surname='{}' AND password='{}' ALLOW FILTERING"""\
        .format(name,surname,password))
    if (result.was_applied != 0):
       return render_template('index.html')
    else:
        return jsonify({'error':'Incorrect username or password'}), 404

#Get all users in the database
@app.route('/all', methods=['GET'])
def get_everything():
    rows = session.execute( """ SELECT * FROM gym.users""")
    result=[]
    for r in rows:
        result.append(
            {
                'name': r.name,
                'surname': r.surname,
                'age': r.age,
                'sex': r.sex,
                'weight': r.weight,
                'height': r.height
            }
        )
    # return render_template("index.html",content=result)
    return jsonify(result)

#Make an call to an external API to get routines
@app.route('/external_routines/<category>', methods=['GET'])
def get_external_workout(category):
    categories_url  = 'https://wger.de/api/v2/exercisecategory/'
    first_resp = requests.get(categories_url)
    if first_resp.ok:
        categories = first_resp.json()
        for excercise in categories['results']:
            if excercise['name'] == category.capitalize():
                workouts_template = 'https://wger.de/api/v2/exercise/?language=2&category={}'.format(int(excercise['id']))
                resp = requests.get(workouts_template)
                if resp.ok:
                    workouts = resp.json()
                else:
                    print(resp.reason)
                return workouts
    else:
        print(resp.reason)

#Delete an user from the Database
@app.route('/delete_user',methods=['DELETE'])
def delete_user():
    if not request.json or not "name" in request.json or not "surname" in request.json:
        return jsonify({'error':'the new record needs to have name and surname'}), 400    
    
    name = request.json['name']
    surname = request.json['surname']
    query = "DELETE FROM gym.users WHERE name='{}' AND surname='{}'".format(name,surname)
    session.execute(query)
    return jsonify({'message': 'deleted: /user/{},{}'.format\
        (request.json['name'],request.json['surname'])}),200
    
#Update the weight of a user
@app.route('/update_user_weight',methods=['PUT'])
def update_user_weight():
    if not request.json or not "name" in request.json or not "surname" in request.json or not "weight":
        return jsonify({'error':'the new record needs to have name,surname and weight'}), 400

    name = request.json['name']
    surname = request.json['surname']
    weight = float(request.json['weight'])
    
    result = session.execute("""select count(*) from gym.users where name='{}' AND surname='{}'""".format(name,surname))
    if (result.was_applied != 0):
        query = "UPDATE gym.users SET weight={} WHERE name='{}' AND surname='{}'".format(weight,name,surname)
        session.execute(query)
        return jsonify({'message': 'updated: /user/{},{}'.format\
            (request.json['name'],request.json['surname'])}),200
    else:
        return jsonify({'error':'User does not exist'}), 404

#Update the height of a user
@app.route('/update_user_height',methods=['PUT'])
def update_user_height():
    if not request.json or not "name" in request.json or not "surname" in request.json or not "height" in request.json:
        return jsonify({'error':'the new record needs to have name,surname and height'}), 400
        
    name = request.json['name']
    surname = request.json['surname']
    height = float(request.json['height'])
    
    result = session.execute("""select count(*) from gym.users where name='{}' AND surname='{}'""".format(name,surname))
    if (result.was_applied != 0):
        query = "UPDATE gym.users SET height={} WHERE name='{}' AND surname='{}'".format(height,name,surname)
        session.execute(query)
        return jsonify({'message': 'updated: /user/{},{}'.format\
            (request.json['name'],request.json['surname'])}),200
    else:
        return jsonify({'error':'User does not exist'}), 404


#Update the age of a user
@app.route('/update_user_age',methods=['PUT'])
def update_user_age():
    if not request.json or not "name" in request.json or not "surname" in request.json or not "age" in request.json:
        return jsonify({'error':'the new record needs to have name,surname and age'}), 400
        
    name = request.json['name']
    surname = request.json['surname']
    age = int(request.json['age'])
    
    result = session.execute("""select count(*) from gym.users where name='{}' AND surname='{}'""".format(name,surname))
    if (result.was_applied != 0):
        query = "UPDATE gym.users SET age={} WHERE name='{}' AND surname='{}'".format(age,name,surname)
        session.execute(query)
        return jsonify({'message': 'updated: /user/{},{}'.format\
            (request.json['name'],request.json['surname'])}),200
    else:
        return jsonify({'error':'User does not exist'}), 404

if __name__=="__main__":
    app.run(host='0.0.0.0',port=5000)

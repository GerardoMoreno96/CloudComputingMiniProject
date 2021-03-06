from flask import Flask, render_template, request, jsonify,redirect
from cassandra.cluster import Cluster
from werkzeug.security import generate_password_hash,check_password_hash
import datetime
import json
import requests
import requests_cache
requests_cache.install_cache('gymprogress_app_cache', backend='sqlite', expire_after=36000)
cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session = cluster.connect()

app = Flask(__name__)

# Index page, welcome the user 
@app.route('/')
def login():
    return render_template('login.html')


#Make a call to an external API to get routines
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

###################     /   _\/ \   / \     ###################
###################     |  /  | |   | |     ###################
###################     |  \__| |_/\| |     ###################
###################     \____/\____/\_/     ###################


# Create a new user for the app from the command line
@app.route('/new_user_cli', methods=['POST'])
def create_new_user():
      
    if not request.json or not "name" in request.json or not "surname" in request.json \
        or not "age" in request.json or not "gender" in request.json or not "weight" in request.json or not "height" in request.json or not "password" in request.json:
        return jsonify({'error':'the new record needs to have name,surname,age,gender,weight,height and password'}), 400
        
    name =  request.json['name']
    surname = request.json['surname']
    age = int(request.json['age'])
    gender = request.json['gender']
    weight = float(request.json['weight'])
    height = float(request.json['height'])
    password = generate_password_hash(request.json['password'], method='sha256')

    #Check if that user does not exist already
    result = session.execute("""select count(*) from gym.users where name='{}' AND surname='{}'""".format(name,surname))
    if (result.was_applied == 0):

        query = "INSERT INTO gym.users(name,surname,age,gender,weight,height) VALUES ( '{}','{}',{},'{}',{},{})"\
            .format(name,surname,age,gender,weight,height)
        session.execute(query)

        password_query = "INSERT INTO gym.accounts (name,surname,password) VALUES ('{}','{}','{}')".format(name,surname,password)
        session.execute(password_query)

        current_date = str(datetime.datetime.now())[:10]
        update_weights_query ="INSERT INTO gym.weights (name,new_date,surname,weight) VALUES ('{}','{}','{}',{})".\
            format(name,current_date,surname,weight)
        session.execute(update_weights_query)

        return jsonify({'message': 'created: /new_user {},{}'.format(name,surname)}), 201
    else:
        return jsonify({'error':'User already exists'}), 409

#Get all users in the database
# @app.route('/all', methods=['GET'])
# def get_everything():
#     rows = session.execute( """ SELECT * FROM gym.users""")
#     result=[]
#     for r in rows:
#         result.append(
#             {
#                 'name': r.name,
#                 'surname': r.surname,
#                 'age': r.age,
#                 'gender': r.gender,
#                 'weight': r.weight,
#                 'height': r.height
#             }
#         )
#     # return render_template("index.html",content=result)
#     return jsonify(result)

#Delete an user from the Database
@app.route('/delete_user',methods=['DELETE'])
def delete_user():
    if not request.json or not "name" in request.json or not "surname" in request.json:
        return jsonify({'error':'the new record needs to have name and surname'}), 400    
    
    name = request.json['name']
    surname = request.json['surname']
    query = "DELETE FROM gym.users WHERE name='{}' AND surname='{}'".format(name,surname)
    session.execute(query)

    accounts_query = "DELETE FROM gym.accounts where name='{}' and surname='{}'".format(name,surname)
    session.execute(accounts_query)

    rows = get_weights_query = "SELECT new_date from gym.weights where name='{}' and surname='{}' ALLOW FILTERING".format(name,surname)
    rows = session.execute(get_weights_query)
    result = []
    for r in rows:
        result.append(
            {
                'date': str(datetime.datetime.fromtimestamp(r.new_date.seconds))[0:-9],
            }
        )
    for i in result:
        delete_weights_query = "DELETE FROM gym.weights WHERE name='{}' AND surname='{}' AND new_date='{}'".format(name,surname,i['date'])
        session.execute(delete_weights_query)
    
    
    delete_pr_query = "DELETE FROM gym.personal_records WHERE name='{}' and surname='{}'".format(name,surname)
    session.execute(delete_pr_query)

    return jsonify({'message': 'deleted: /user/{},{}'.format\
        (request.json['name'],request.json['surname'])}),200

#Update the weight of a user from the command line
@app.route('/update_user_weight_cli',methods=['PUT'])
def update_user_weight():
    if not request.json or not "name" in request.json or not "surname" in request.json or not "weight" or not "date" in request.json:
        return jsonify({'error':'the new record needs to have name,surname, weight and date'}), 400

    name = request.json['name']
    surname = request.json['surname']
    weight = float(request.json['weight'])
    current_date = request.json['date']
    
    #check if the user exists
    result = session.execute("""select count(*) from gym.users where name='{}' AND surname='{}'""".format(name,surname))
    if (result.was_applied != 0):
        query = "UPDATE gym.users SET weight={} WHERE name='{}' AND surname='{}'".format(weight,name,surname)
        session.execute(query)

        update_weights_query ="INSERT INTO gym.weights (name,new_date,surname,weight) VALUES ('{}','{}','{}',{})".\
            format(name,current_date,surname,weight)
        session.execute(update_weights_query)
        
        return jsonify({'message': 'updated: /user/{},{}'.format\
            (request.json['name'],request.json['surname'])}),200
    else:
        return jsonify({'error':'User does not exist'}), 404

#Update the height of a user from the command line
@app.route('/update_user_height',methods=['PUT'])
def update_user_height():
    if not request.json or not "name" in request.json or not "surname" in request.json or not "height" in request.json:
        return jsonify({'error':'the new record needs to have name,surname and height'}), 400
        
    name = request.json['name']
    surname = request.json['surname']
    height = float(request.json['height'])
    
    #check if the user exists    
    result = session.execute("""select count(*) from gym.users where name='{}' AND surname='{}'""".format(name,surname))
    if (result.was_applied != 0):
        query = "UPDATE gym.users SET height={} WHERE name='{}' AND surname='{}'".format(height,name,surname)
        session.execute(query)
        return jsonify({'message': 'updated height for : /user/{},{}'.format\
            (request.json['name'],request.json['surname'])}),200
    else:
        return jsonify({'error':'User does not exist'}), 404

#Update the age of a user from the command line
@app.route('/update_user_age',methods=['PUT'])
def update_user_age():
    if not request.json or not "name" in request.json or not "surname" in request.json or not "age" in request.json:
        return jsonify({'error':'the new record needs to have name,surname and age'}), 400
        
    name = request.json['name']
    surname = request.json['surname']
    age = int(request.json['age'])
    

    #check if the user exists
    result = session.execute("""select count(*) from gym.users where name='{}' AND surname='{}'""".format(name,surname))
    if (result.was_applied != 0):
        query = "UPDATE gym.users SET age={} WHERE name='{}' AND surname='{}'".format(age,name,surname)
        session.execute(query)
        return jsonify({'message': 'updated age for: /user/{},{}'.format\
            (request.json['name'],request.json['surname'])}),200
    else:
        return jsonify({'error':'User does not exist'}), 404


#set a new pr for an unregistered excercise
@app.route('/set_user_pr_cli',methods=['POST'])
def set_pr_cli():
    if not request.json or not "name" in request.json or not "surname" in request.json or not "excercise_name" in request.json \
        or not "new_record" in request.json:
        
        return jsonify({'error':'the new record needs to have name,surname,excercise name and new_record'}), 400
        
    name = request.json['name']
    surname = request.json['surname']
    excercise_name = request.json['excercise_name']
    new_record = request.json['new_record']

    #check if the user exists
    result = session.execute("""select count(*) from gym.users where name='{}' AND surname='{}'""".format(name,surname))
    if (result.was_applied != 0):
        query = "INSERT INTO gym.personal_records(name,surname,excercise_name,new_record) VALUES('{}','{}','{}','{}')".\
            format(name,surname,excercise_name,new_record)
        session.execute(query)
        return jsonify({'message': 'created pr for : /user/{},{}'.format\
            (request.json['name'],request.json['surname'])}),200
    else:
        return jsonify({'error':'User does not exist'}), 404
    
#set a record for a registered excercise    
@app.route('/update_user_pr_cli',methods=['PUT'])
def update_pr_cli():
    if not request.json or not "name" in request.json or not "surname" in request.json or not "excercise_name" in request.json \
        or not "new_record" in request.json:
        
        return jsonify({'error':'the new record needs to have name,surname,excercise name and new_record'}), 400
        
    name = request.json['name']
    surname = request.json['surname']
    excercise_name = request.json['excercise_name']
    new_record = request.json['new_record']

    #check if the user exists
    result = session.execute("""select count(*) from gym.users where name='{}' AND surname='{}'""".format(name,surname))
    if (result.was_applied != 0):
        query = "UPDATE gym.personal_records SET new_record='{}' WHERE name='{}' AND surname='{}' AND excercise_name='{}'".\
            format(new_record,name,surname,excercise_name)
        session.execute(query)
        return jsonify({'message': 'updated pr for : /user/{},{}'.format\
            (request.json['name'],request.json['surname'])}),200
    else:
        return jsonify({'error':'User does not exist'}), 404
        

################### /  _ \/  __\/  _ \/ \  /|/ ___\/  __//  __\ ###################
################### | | //|  \/|| / \|| |  |||    \|  \  |  \/| ###################
################### | |_\\|    /| \_/|| |/\||\___ ||  /_ |    / ###################
################### \____/\_/\_\\____/\_/  \|\____/\____\\_/\_\ ###################
                                           
## Note: You will see that all the methods in the browser are using the 'POST' method, this is because first I have
## get what is written in the HTML textbox. If I don't use POST there's no way to get the information from the textbox.
## Also, HTML doesn't allow the 'PUT' method, but don't worry, all the methods that you see in here can also be executed
## through the terminal with their appropiate REST method.

# Create a new user from the browser
@app.route('/new_user_browser', methods=['POST'])
def create_new_user_browser():
    
    name =  request.form['name']
    surname = request.form['surname']
    age = int(request.form['age'])
    gender = request.form['gender']
    weight = float(request.form['weight'])
    height = float(request.form['height'])
    password = generate_password_hash(request.form['password'], method='sha256')

    result = session.execute("""select count(*) from gym.users where name='{}' AND surname='{}'""".format(name,surname))
    if (result.was_applied == 0):

        query = "INSERT INTO gym.users(name,surname,age,gender,weight,height) VALUES ( '{}','{}',{},'{}',{},{})"\
            .format(name,surname,age,gender,weight,height)
        session.execute(query)

        password_query = "INSERT INTO gym.accounts (name,surname,password) VALUES ('{}','{}','{}')".format(name,surname,password)
        session.execute(password_query)

        current_date = str(datetime.datetime.now())[:10]
        update_weights_query ="INSERT INTO gym.weights (name,new_date,surname,weight) VALUES ('{}','{}','{}',{})".\
            format(name,current_date,surname,weight)
        session.execute(update_weights_query)

        return "Success",201
    else:
        return jsonify({'error':'User already exists'}), 409
   
#Login from the browser
@app.route('/login_user_browser',methods=['POST'])
def login_browser():

    name =  request.form['name']
    surname = request.form['surname']
    password = request.form['password']

    result = session.execute("""select password from gym.accounts where name='{}' AND surname='{}'"""\
        .format(name,surname))
    if (len(result.current_rows) !=0):
        if check_password_hash(result.current_rows[0].password,password):
            query = "SELECT * FROM gym.users WHERE name='{}' AND surname = '{}'".format(name,surname)
            user_info = session.execute(query)
            user_name = user_info.current_rows[0].name
            user_surname = user_info.current_rows[0].surname
            user_age = user_info.current_rows[0].age
            user_weight = user_info.current_rows[0].weight
            user_height = user_info.current_rows[0].height

            user_weights_query = "SELECT * FROM gym.weights where name='{}' and surname='{}' ALLOW FILTERING".format(user_name,user_surname)    
            rows = session.execute(user_weights_query)
            result=[]
            for r in rows:
                result.append(
                    {
                        'date': str(datetime.datetime.fromtimestamp(r.new_date.seconds))[0:-9],
                        'weight': r.weight,
                    }
                )

            user_pr_query = "SELECT excercise_name,new_record FROM gym.personal_records WHERE name='{}' and surname='{}'".format(name,surname)
            pr_rows = session.execute(user_pr_query)
            pr_result=[]
            for r in pr_rows:
                pr_result.append(
                    {
                        'excercise_name': r.excercise_name,
                        'record': r.new_record,
                    }
                )


            return render_template('index.html',name=user_name,surname=user_surname,\
                age=user_age,weight=user_weight,height=user_height,weight_progress=result,pr=pr_result)
        else:
            return jsonify({'error':'Incorrect username or password'}), 401

    else:
        return jsonify({'error':'User does not exist'}), 404

#Make an call to an external API to get routines from the browser
@app.route('/external_routines_browser/', methods=['POST'])
def get_external_workout_browser_pt1():
    category =  request.form['category']
    return redirect('/external_routines/{}'.format(category))

#Update the weight of a user from the browser
@app.route('/update_user_weight_browser',methods=['POST']) #HTML doesn't allow PUT request
def update_user_weight_browser():

    weight = float(request.form['new_weight'])    
    name = request.form['user_name']
    surname = request.form['user_surname']

    query = "UPDATE gym.users SET weight={} WHERE name='{}' AND surname='{}'".format(weight,name,surname)
    session.execute(query)

    current_date = str(datetime.datetime.now())[:10]
    update_weights_query ="INSERT INTO gym.weights (name,new_date,surname,weight) VALUES ('{}','{}','{}',{})".\
        format(name,current_date,surname,weight)
    session.execute(update_weights_query)

    return jsonify({'message': 'updated: /user/{},{}'.format(name,surname)}),200


#Update the height of a user from the browser
@app.route('/update_user_height_browser',methods=['POST']) #HTML doesn't allow PUT request
def update_user_height_browser():

    height = float(request.form['new_height'])    
    name = request.form['user_name']
    surname = request.form['user_surname']

    query = "UPDATE gym.users SET height={} WHERE name='{}' AND surname='{}'".format(height,name,surname)
    session.execute(query)
    return jsonify({'message': 'updated: /user/{},{}'.format(name,surname)}),200

#Update the age of a user from the browser
@app.route('/update_user_age_browser',methods=['POST']) #HTML doesn't allow PUT request
def update_user_age_browser():

    age = int(request.form['new_age'])    
    name = request.form['user_name']
    surname = request.form['user_surname']

    query = "UPDATE gym.users SET age={} WHERE name='{}' AND surname='{}'".format(age,name,surname)
    session.execute(query)
    return jsonify({'message': 'updated: /user/{},{}'.format(name,surname)}),200


#set a new pr for an  excercise from the browser
@app.route('/set_pr_browser', methods=['POST'])
def set_pr_browser():
    
    name = request.form['user_name']
    surname = request.form['user_surname']
    excercise_name = request.form['pr_name']
    new_record = request.form['pr_record']
    #Get all prs with that name
    count_pr_query = "SELECT COUNT(*) from gym.personal_records WHERE name='{}' and surname='{}' and excercise_name='{}'".\
        format(name,surname,excercise_name)
    pr_rows = session.execute(count_pr_query)
    if pr_rows.was_applied == 0:
        #If the excercise is NOT registered in the database
        query = "INSERT INTO gym.personal_records(name,surname,excercise_name,new_record) VALUES('{}','{}','{}','{}')".\
            format(name,surname,excercise_name,new_record)
        session.execute(query)
        return jsonify({'message': 'created pr for : /user/{},{}'.format\
            (name,surname)}),200
    else:
        #If the excercise is already registered in the database
        query = "UPDATE gym.personal_records SET new_record='{}' WHERE name='{}' AND surname='{}' AND excercise_name='{}'".\
            format(new_record,name,surname,excercise_name)
        session.execute(query)
        return jsonify({'message': 'updated pr for : /user/{},{}'.format\
            (name,surname)}),200


if __name__=="__main__":
    app.run(host='0.0.0.0',port=5000)

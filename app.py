from flask import Flask, render_template, request, jsonify
from cassandra.cluster import Cluster
import json
import requests
import requests_cache
requests_cache.install_cache('gymprogress_app_cache', backend='sqlite', expire_after=36000)
cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session = cluster.connect()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return('<h1>Welcome to Gerardo\'s Gym Progress App</h1>')

@app.route('/new_client', methods=['POST'])
def create_new_client():
    if not request.json or not "name" in request.json or not "surname" in request.json \
        or not "age" in request.json or not "sex" in request.json or not "weight" in request.json or not "height" in request.json:
        return jsonify({'error':'the new record needs to have name,surname,age,sex,weight,height'}), 400
    new_record = {
        'name': request.json['name'],
        'surname': request.json['surname'],
        'age': int(request.json['age']),
        'sex': request.json['sex'],
        'weight': float(request.json['weight']),
        'height': float(request.json['height'])
    }
    session.execute( """INSERT INTO gym.users(name,surname,age,sex,weight,height) VALUES ( '{}','{}',{},'{}',{},{})""".format\
        (new_record['name'],new_record['surname'],new_record['age'],new_record['sex'],new_record['weight'],new_record['height'] ))
    
    return jsonify({'message': 'created: /new_client {}'.format(new_record['name'])}), 201

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
    return jsonify(result)

@app.route('/external_routines', methods=['GET'])
def get_external_workout():
    workouts_template = 'https://wger.de/api/v2/exercise/?language=2'
    resp = requests.get(workouts_template)
    if resp.ok:
        workouts = resp.json()
    else:
        print(resp.reason)
    return workouts

@app.route('/delete_user',methods=['DELETE'])
def delete_user():
    name = request.json['name']
    surname = request.json['surname']
    query = "DELETE FROM gym.users WHERE name='{}' AND surname='{}'".format(name,surname)
    session.execute(query)
    return jsonify({'message': 'deleted: /user/{},{}'.format\
        (request.json['name'],request.json['surname'])}),200
    

if __name__=="__main__":
    app.run(host='0.0.0.0',port=5000)
from flask import Flask, render_template, request, jsonify
import json
import requests
import requests_cache
import pprint

requests_cache.install_cache('nutrition_app_cache', backend='sqlite', expire_after=36000)

all_records = [{"age":"23","height":"1.70","name":"Name","sex":"male","surname":"Lastname","weight":"58"}]

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return('<h1>Welcome to Gerardo\'s Nutritional App</h1>')

@app.route('/new_client', methods=['POST'])
def create_new_client():
    if not request.json or not "name" in request.json or not "surname" in request.json or not "age" in request.json or not "sex" in request.json or not "weight" in request.json or not "height" in request.json:
        return jsonify({'error':'the new record needs to have name,surname,age,sex,weight,height'}), 400
    new_record = {
        'name': request.json['name'],
        'surname': request.json['surname'],
        'age': request.json['age'],
        'sex': request.json['sex'],
        'weight':request.json['weight'],
        'height': request.json['height']
    }
    all_records.append(new_record)
    return jsonify({'message': 'created: /new_client'.format(new_record['name'])}), 201

@app.route('/all', methods=['GET'])
def get_everything():
    return jsonify(all_records)

@app.route('/external_routines', methods=['GET'])
def get_external_workout():
    workouts_template = 'https://wger.de/api/v2/exercise/?language=2'
    resp = requests.get(workouts_template)
    if resp.ok:
        workouts = resp.json()
    else:
        print(resp.reason)
    return workouts

@app.route('/delete_user/<client_name>/<client_surname>',methods=['DELETE'])
def delete_user(client_name,client_surname):
    matching_user = [user for user in all_records if user["name"] == client_name and user["surname"] == client_surname]
    if len(matching_user)==0:
        return jsonify({ ' error ' : 'user not found! ' }), 404
    all_records.remove(matching_user[0])
    return jsonify({ ' success ' : True})

if __name__=="__main__":
    app.run(host='127.0.0.1')
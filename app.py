from flask import Flask, request, json, render_template
from pymongo import MongoClient
from decouple import config
from bson import json_util

app = Flask(__name__)

# Read the mongo_uri from the .env file
mongo_uri = config('MONGODB_URI')
db_name = config('DBNAME')

def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/api/get-doctors', methods=['GET'])
def get_doctors():
    client = MongoClient(mongo_uri)
    try:
        client.server_info()  # Check if connected to MongoDB
        db = client.get_database(db_name)
        doctors_collection = db.get_collection('doctors_collection')

        doctors = list(doctors_collection.find({}))
        return parse_json(doctors)
    except Exception as e:
        print(f'Error getting doctor data: {e}')
        return json.dumps({'message': 'An error occurred'}), 500
    finally:
        client.close()

@app.route('/api/get-patients', methods=['GET'])
def get_patients():
    client = MongoClient(mongo_uri)
    try:
        client.server_info()  # Check if connected to MongoDB
        db = client.get_database(db_name)
        patient_collection = db.get_collection('patient_collection')

        patients = list(patient_collection.find({}))
        return parse_json(patients)
    except Exception as e:
        print(f'Error getting patient data: {e}')
        return json.dumps({'message': 'An error occurred'}), 500
    finally:
        client.close()

@app.route('/api/insert-doctor', methods=['POST'])
def insert_doctor():
    data = request.get_json()
    client = MongoClient(mongo_uri)
    try:
        client.server_info()  # Check if connected to MongoDB
        db = client.your_database_name
        doctors_collection = db.doctors

        insert_result = doctors_collection.insert_one(data)
        return json.dumps({'message': 'Doctor data inserted successfully', 'inserted_id': str(insert_result.inserted_id)})
    except Exception as e:
        print(f'Error inserting doctor data: {e}')
        return json.dumps({'message': 'An error occurred'}), 500
    finally:
        client.close()

@app.route('/api/insert-patient', methods=['POST'])
def insert_patient():
    data = request.get_json()
    client = MongoClient(mongo_uri)
    try:
        client.server_info()  # Check if connected to MongoDB
        db = client.your_database_name
        patients_collection = db.patients

        insert_result = patients_collection.insert_one(data)
        return json.dumps({'message': 'Patient data inserted successfully', 'inserted_id': str(insert_result.inserted_id)})
    except Exception as e:
        print(f'Error inserting patient data: {e}')
        return json.dumps({'message': 'An error occurred'}), 500
    finally:
        client.close()


if __name__ == '__main__':
    app.run(debug=True)

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

@app.route('/enter_doctors', methods=['GET'])
def enter_doctors():
    return render_template('enter-doctor.html')

@app.route('/enter_patients', methods=['GET'])
def enter_patients():
    return render_template('enter-patient.html')

@app.route('/get_doctors', methods=['GET'])
def get_doctors():
    client = MongoClient(mongo_uri)
    try:
        client.server_info()  # Check if connected to MongoDB
        db = client.get_database(db_name)
        doctors_collection = db.get_collection('doctors_collection')

        doctors_list = list(doctors_collection.find({}))
        return render_template("get-doctor.html", doctors_list = doctors_list)
    except Exception as e:
        print(f'Error getting doctors data: {e}')
        return parse_json({'message': 'An error occurred'}), 500
    finally:
        client.close()

@app.route('/enter_prescription', methods=['GET'])
def enter_prescription():
    client = MongoClient(mongo_uri)
    try:
        client.server_info()  # Check if connected to MongoDB
        db = client.get_database(db_name)
        medications_collection = db.get_collection('medications_collection')
        patient_collection = db.get_collection('patient_collection')
        doctors_collection = db.get_collection('doctors_collection')

        doctors_list = list(doctors_collection.find({}))
        patients_list = list(patient_collection.find({}))
        medications_list = list(medications_collection.find({}))
        return render_template('enter-prescription.html', medications_list = medications_list, doctors_list=doctors_list, patients_list=patients_list)
    except Exception as e:
        print(f'Error getting prescription data: {e}')
        return parse_json({'message': 'An error occurred'}), 500
    finally:
        client.close()

@app.route('/get_patients', methods=['GET'])
def get_patients():
    client = MongoClient(mongo_uri)
    try:
        client.server_info()  # Check if connected to MongoDB
        db = client.get_database(db_name)
        patient_collection = db.get_collection('patient_collection')

        patients_list = list(patient_collection.find({}))
        return render_template("get-patient.html", patients_list = patients_list)
    except Exception as e:
        print(f'Error getting patient data: {e}')
        return parse_json({'message': 'An error occurred'}), 500
    finally:
        client.close()

@app.route('/insert_doctor', methods=['POST'])
def insert_doctor():
    data = json.loads(request.get_data())
    client = MongoClient(mongo_uri)
    try:
        client.server_info()  # Check if connected to MongoDB
        db = client.get_database(db_name)
        doctors_collection = db.get_collection('doctors_collection')

        insert_result = doctors_collection.insert_one(data)
        return parse_json({'message': 'Doctor data inserted successfully', 'inserted_id': str(insert_result.inserted_id)})
    except Exception as e:
        print(f'Error inserting doctor data: {e}')
        return parse_json({'message': 'An error occurred'}), 500
    finally:
        client.close()

@app.route('/insert_patient', methods=['POST'])
def insert_patient():
    data = json.loads(request.get_data())
    client = MongoClient(mongo_uri)
    try:
        client.server_info()  # Check if connected to MongoDB
        db = client.get_database(db_name)
        patient_collection = db.get_collection('patient_collection')

        insert_result = patient_collection.insert_one(data)
        return parse_json({'message': 'Patient data inserted successfully', 'inserted_id': str(insert_result.inserted_id)})
    except Exception as e:
        print(f'Error inserting patient data: {e}')
        return parse_json({'message': 'An error occurred'}), 500
    finally:
        client.close()


@app.route('/insert_prescription', methods=['POST'])
def insert_prescription():
    data = json.loads(request.get_data())
    client = MongoClient(mongo_uri)
    try:
        client.server_info()  # Check if connected to MongoDB
        db = client.get_database(db_name)
        prescription_collection = db.get_collection('prescription_collection')

        insert_result = prescription_collection.insert_one(data)
        return parse_json({'message': 'Prescription data inserted successfully', 'inserted_id': str(insert_result.inserted_id)})
    except Exception as e:
        print(f'Error inserting prescription data: {e}')
        return parse_json({'message': 'An error occurred'}), 500
    finally:
        client.close()


if __name__ == '__main__':
    app.run(debug=True)

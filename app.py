from flask import Flask, request, json, render_template, send_file
from pymongo import MongoClient
from decouple import config
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.barcode import code39, code128, code93
from reportlab.graphics.barcode import eanbc, qr, usps
from reportlab.graphics.shapes import Drawing 
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
import os

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
    print(data)
    try:
        client.server_info()  # Check if connected to MongoDB
        db = client.get_database(db_name)
        prescription_collection = db.get_collection('prescription_collection')
        medications_collection = db.get_collection('medications_collection')
        patient_collection = db.get_collection('patient_collection')
        doctors_collection = db.get_collection('doctors_collection')

        selected_doctor = list(doctors_collection.find({"_id":ObjectId(data['doctor_name'])}))[0]
        selected_patient = list(patient_collection.find({"_id":ObjectId(data['patient_name'])}))[0]
        selected_medication = list(medications_collection.find({"_id":ObjectId(data['prescription_name'])}))[0]

        print(selected_doctor)
        print(selected_patient)
        print(selected_medication)

        prescription_object = {
            "prescription_date": "{:%B %d, %Y}".format(datetime.now()),
            "patient_name" : "{} {}".format(selected_patient['firstName'], selected_patient['lastName']),
            "patient_age": selected_patient['age'],
            "patient_phone": selected_patient['phoneNumber'],
            "patient_dob": selected_patient['dob'],
            "patient_email": selected_patient.get('email'),
            "patient_gender": selected_patient.get('gender'),
            "patient_address": selected_patient.get('address'),
            "patient_allergies": selected_patient.get('allergies'),
            "patient_health_condition": selected_patient.get('healthCondition'),
            
            "selected_medication": selected_medication.get('name'),
            "purpose": data.get('purpose'),
            "dosage": data.get('dosage') ,
            "route": data.get('route'),
            "frequency": data.get('frequency'),

            "doctor_name": "{} {}".format(selected_doctor['firstName'], selected_doctor['lastName']),
            "doctor_phone": selected_doctor.get('phoneNumber'),
            "doctor_email": selected_doctor.get('email'),
        }

        insert_result = prescription_collection.insert_one(prescription_object).inserted_id
        inserted_prescription = list(prescription_collection.find({"_id":ObjectId(insert_result)}))[0]

        barcode_value = insert_result
        # barcode128 = code128.Code128(barcode_value)
        # x = 1 * mm
        # y = 285 * mm
        # x1 = 6.4 * mm

        # Load JSON data
        data = inserted_prescription

        # Create a PDF
        if not os.path.exists('cached'):
            os.makedirs('cached')
        prescription_pdf_path = "cached/prescription.pdf"
        doc = SimpleDocTemplate(prescription_pdf_path, pagesize=letter)

        elements = []

        # Styles
        styles = getSampleStyleSheet()
        style = styles["BodyText"]

        # Create a table to display the data
        data = [
            ["Prescription Date:", data["prescription_date"]],
            ["Patient Name:", data["patient_name"]],
            ["Patient Age:", data["patient_age"]],
            ["Patient Phone:", data["patient_phone"]],
            ["Patient Date of Birth:", data["patient_dob"]],
            ["Patient Email:", data["patient_email"]],
            ["Patient Gender:", data["patient_gender"]],
            ["Patient Address:", data["patient_address"]],
            ["Patient Allergies:", data["patient_allergies"]],
            ["Patient Health Condition:", data["patient_health_condition"]],
            ["Selected Medication:", data["selected_medication"]],
            ["Purpose:", data["purpose"]],
            ["Dosage:", data["dosage"]],
            ["Route:", data["route"]],
            ["Frequency:", data["frequency"]],
            ["Doctor Name:", data["doctor_name"]],
            ["Doctor Phone:", data["doctor_phone"]],
            ["Doctor Email:", data["doctor_email"]],
        ]

        table = Table(data, colWidths=120, rowHeights=20)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(Paragraph("Prescription Details", style))
        elements.append(table)

        # Generate a Code128 barcode
        # barcode = code128.Code128("123456789", writer=renderPDF)
        # barcode.drawOn(doc, 50, 50)  # Adjust the coordinates as needed

        # Build the PDF
        doc.build(elements)

        print("Prescription PDF created: prescription.pdf")
        return send_file(os.getcwd() + "/" + prescription_pdf_path, as_attachment=True)

        # return parse_json({'message': 'Prescription data inserted successfully', 'inserted_id': str(insert_result.inserted_id)})
    except Exception as e:
        print(f'Error inserting prescription data: {e}')
        return parse_json({'message': 'An error occurred'}), 500
    finally:
        client.close()


if __name__ == '__main__':
    app.run(debug=True)

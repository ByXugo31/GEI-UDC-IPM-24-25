from .database import engine
from .models import Patient, Medication, Posology
from sqlmodel import SQLModel, text, Session
from faker import Faker
from .crud import *
import random
import json
import datetime


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # Foreign keys are disabled in sqlite3 by default
    with Session(engine) as session:
        session.exec(text("PRAGMA foreign_keys = ON"))


def init_db():
    fake = Faker()
    f = open('medications.json', 'r', encoding='utf8')
    medications = json.load(f)
    f.close()
    dosages = [0.25, 0.5, 0.75, 1, 1.5, 2]
    posology_delta = [6, 8, 12, 24]

    base_intake_date = datetime.datetime(2024, 10, 1)
    day_delta = datetime.timedelta(days=1)
    
    with Session(engine) as session:

        for i in range(100):
            profile = fake.simple_profile()
            name = profile['name'].split()
        
            patient = Patient(
                code=fake.ssn(),
                name=name[0],
                surname=name[1],
            )
            patient = insert_patient(session, patient)
    
            for j in range(random.randint(1,5)):
                name = medications[random.randint(0, len(medications))]['nombre']
                idx = random.randint(0,len(dosages)-1)
                start_date = fake.date_between(datetime.datetime(2024,10,1), datetime.datetime.now())
                medication = Medication(
                    name=name, 
                    dosage=dosages[idx],
                    treatment_duration=random.randint(5, 100), 
                    start_date=start_date,
                    patient_id = patient.id,
                    )
                medication = insert_medication(session, medication)
                time_str = fake.time()
                time = datetime.datetime.strptime(time_str, "%H:%M:%S")
                idx = random.randint(0, len(posology_delta)-1)
                rep = int(24/posology_delta[idx])
                time_delta = datetime.timedelta(hours=posology_delta[idx])
                for k in range(rep):
                    posology = Posology(
                        medication_id = medication.id,
                        hour=int(time.hour),
                        minute=0)
                    insert_posology(session, posology)

                    
                    intake_date = datetime.datetime(
                        year=start_date.year,
                        month= start_date.month,
                        day=start_date.day,   
                        hour = int(time.hour),
                        minute = 0 
                    )
                    for l in range(14):
                        r = random.uniform(0,1)
                        if r < 0.2: # Skip some intakes
                            print("Skipped intake!")
                            continue
                        actual_intake_date = intake_date + datetime.timedelta(minutes=random.randint(-60, 60))
                        intake = Intake(
                            medication_id = medication.id,
                            date=actual_intake_date.strftime("%Y-%m-%dT%H:%M")
                        )
                        insert_intake(session, intake)
                        intake_date += day_delta
                    time += time_delta

def init_db_if_empty():
    with Session(engine) as session:
        patients = find_patient(session)
        if len(patients) == 0:
            init_db()
        else:
            print("DB not empty")
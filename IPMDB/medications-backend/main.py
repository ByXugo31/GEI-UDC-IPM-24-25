from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import datetime

from sql_app.database import get_session
from sql_app.models import Patient, Medication, Posology, Message, Intake
from sql_app.utils import create_db_and_tables, init_db_if_empty
from sql_app.crud import *
from sqlmodel import Session

import time

tags_metadata = [
    {
        "name": "patients",
        "description": "CRUD operations with patients.",
    },
    {
        "name": "medications",
        "description": "CRUD operations with medications.",
    },
    {
        "name": "posologies",
        "description": "Operations with posologies.",
    }, {
        "name": "intakes",
        "description": "Operations with intakes.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    init_db_if_empty()
    yield


app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)

# Enable CORS
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Patients

@app.post("/patients", tags=["patients"],
          status_code=201,
          responses={201: {"model": Patient}, 409: {"model": Message}})
def add_patient(patient: Patient, session: Session = Depends(get_session)):
    registered_patient = insert_patient(session, patient)
    if registered_patient is not None:
        return registered_patient
    else:
        raise HTTPException(status_code=409, detail="Patient already exists")


@app.get("/patients/{patient_id}", tags=["patients"],
         responses={200: {"model": Patient}, 404: {"model": Message}})
def get_patient(patient_id: int, session: Session = Depends(get_session)):
    patient = find_patient(session, patient_id=patient_id)
    if patient is not None:
        return patient
    else:
        raise HTTPException(status_code=404, detail="Patient not found")


@app.get("/patients", tags=["patients"],
         responses={200: {"model": Patient | list[Patient]}, 404: {"model": Message}})
def get_patient_by_code(code: str = None, start_index: int = None, count: int = None, session: Session = Depends(get_session)):
    patient = find_patient(
        session, code=code, start_index=start_index, count=count)
    if patient is not None:
        return patient
    else:
        raise HTTPException(status_code=404, detail="Patient not found")


@app.patch("/patients/{patient_id}", tags=["patients"],
           status_code=204,
           responses={404: {"model": Message}})
def update_patient(patient_id: int, patient: Patient, session: Session = Depends(get_session)):
    patient.id = patient_id
    if not update_patient_data(session, patient):
        raise HTTPException(
            status_code=404, detail=f"Patient {patient_id} could not be updated")


@app.delete("/patients/{patient_id}", tags=["patients"],
            status_code=204,
            responses={404: {"model": Message}})
def delete_patients(patient_id: int, session: Session = Depends(get_session)):
    patient = find_patient(session, patient_id=patient_id)
    if patient is not None:
        remove_patient(session, patient)
    else:
        raise HTTPException(
            status_code=404, detail=f"Patient {patient_id} not found")


# Medications

@app.post("/patients/{patient_id}/medications", tags=["medications"],
          status_code=201,
          responses={201: {"model": Medication}, 422: {"model": Message}})
def add_medication(patient_id: int, medication: Medication, session: Session = Depends(get_session)):
    try:
        date = datetime.datetime.strptime(medication.start_date, "%Y-%m-%d")
        medication.patient_id = patient_id
        new_medication = insert_medication(session, medication)
        if new_medication is not None:
            return new_medication
    except ValueError:
        pass
    raise HTTPException(
        status_code=422, detail=f"Medication {medication} could not be inserted: invalid data")


@app.get("/patients/{patient_id}/medications/{medication_id}", tags=["medications"],
         responses={200: {"model": Medication}, 404: {"model": Message}})
def get_medication(patient_id: int, medication_id: int, session: Session = Depends(get_session)):
    medication = find_medication(session, patient_id, medication_id)
    if medication is not None:
        return medication
    else:
        raise HTTPException(status_code=404, detail="Medication not found")


@app.get("/patients/{patient_id}/medications", tags=["medications"],
         responses={200: {"model": list[Medication]}, 404: {"model": Message}})
def get_all_medications(patient_id: int, session: Session = Depends(get_session)):
    if find_patient(session, patient_id=patient_id) is None:
        raise HTTPException(
            status_code=404, detail=f"Patient {patient_id} not found")
    medications = find_medications(session, patient_id)
    return medications


@app.patch(("/patients/{patient_id}/medications/{medication_id}"), tags=["medications"],
           status_code=204,
           responses={404: {"model": Message}})
def update_medication(patient_id: int, medication_id: int, medication: Medication, session: Session = Depends(get_session)):
    medication.id = medication_id
    medication.patient_id = patient_id
    if not update_medication_data(session, medication):
        raise HTTPException(
            status_code=404, detail=f"Medication {medication_id} for patient {patient_id} could not be updated")


@app.delete(("/patients/{patient_id}/medications/{medication_id}"), tags=["medications"],
            status_code=204,
            responses={404: {"model": Message}})
def delete_medications(patient_id: int, medication_id: int, session: Session = Depends(get_session)):
    medication = find_medication(session, patient_id, medication_id)
    if medication is not None:
        remove_medication(session, medication)
    else:
        raise HTTPException(
            status_code=404, detail=f"Medication {medication_id} not found for patient {patient_id}")


# Posologies

@app.post("/patients/{patient_id}/medications/{medication_id}/posologies", tags=["posologies"],
          status_code=201,
          responses={201: {"model": Posology}, 422: {"model": Message}})
def add_posology(patient_id: int, medication_id: int, posology: Posology, session: Session = Depends(get_session)):
    if posology.hour >= 0 and posology.hour < 24 and posology.minute >= 0 and posology.minute < 60:
        posology.medication_id = medication_id
        medication = find_medication(session, patient_id, medication_id)
        if medication is not None:
            new_posology = insert_posology(session, posology)
            if new_posology is not None:
                return new_posology
    raise HTTPException(
        status_code=422, detail=f"Posology {posology} could not be inserted into medication {medication_id} and patient {patient_id}: invalid data")


@app.get("/patients/{patient_id}/medications/{medication_id}/posologies", tags=["posologies"],
         responses={200: {"model": list[Posology]}, 404: {"model": Message}})
def get_posologies(patient_id: int, medication_id: int, session: Session = Depends(get_session)):
    if find_medication(session, patient_id, medication_id) is None:
        raise HTTPException(
            status_code=404, detail=f"Patient {patient_id} and medication {medication_id} not found")
    posologies = find_posologies(session, patient_id, medication_id)
    return posologies


@app.patch(("/patients/{patient_id}/medications/{medication_id}/posologies/{posology_id}"),  tags=["posologies"],
            status_code=204,
            responses={404: {"model": Message}, 422: {"model": Message}})
def update_posology(patient_id: int, medication_id: int, posology_id: int, posology: Posology, session: Session = Depends(get_session)):
    if posology.hour >= 0 and posology.hour < 24 and posology.minute >= 0 and posology.minute < 60:
        old_posology = find_posology(session, patient_id, medication_id, posology_id)
        if old_posology is not None:
            old_posology.hour = posology.hour
            old_posology.minute = posology.minute
            update_posology_data(session, old_posology)
        else:
            raise HTTPException(
                status_code=404, detail=f"Posology {posology_id} not found for patient {patient_id} and medication {medication_id}")
    else:
        raise HTTPException(
            status_code=424, detail=f"Posology {posology} could not be updated for medication {medication_id} and patient {patient_id}: invalid data")


@app.delete(("/patients/{patient_id}/medications/{medication_id}/posologies/{posology_id}"),  tags=["posologies"],
            status_code=204,
            responses={404: {"model": Message}})
def delete_posologies(patient_id: int, medication_id: int, posology_id: int, session: Session = Depends(get_session)):
    posology = find_posology(session, patient_id, medication_id, posology_id)
    if posology is not None:
        remove_posology(session, posology)
    else:
        raise HTTPException(
            status_code=404, detail=f"Posology {posology_id} not found for patient {patient_id} and medication {medication_id}")


@app.post("/patients/{patient_id}/medications/{medication_id}/intakes", tags=["intakes"],
          status_code=201,
          responses={201: {"model": Intake}, 404: {"model": Message}, 422: {"model": Message}})
def add_intake(patient_id: int, medication_id: int, intake: Intake, session: Session = Depends(get_session)):
    intake.medication_id = medication_id
    try:
        date = datetime.datetime.strptime(intake.date, "%Y-%m-%dT%H:%M")
        medication = find_medication(session, patient_id, medication_id)
        if medication is not None:
            intake = insert_intake(session, intake)
            return intake
        else:
            raise HTTPException(
                status_code=404, detail=f"Medication {medication_id} not found for patient {patient_id}")
    except ValueError:
        raise HTTPException(
            status_code=422, detail=f"Invalid date format {intake.date}. Required format: %Y-%m-%dT%H:%M")


@app.get("/patients/{patient_id}/medications/{medication_id}/intakes",  tags=["intakes"],
         responses={200: {"model": list[Intake]}, 404: {"model": Message}, 422: {"model": Message}})
def get_intakes_by_patient_and_medication(patient_id: int, medication_id: int, start_date: str = None, end_date: str = None, session: Session = Depends(get_session)):
    try:
        if start_date is not None:
            date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
        if end_date is not None:
            date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise HTTPException(
            status_code=422, detail=f"Invalid date format for start_date {start_date}  or end_date {end_date}. Required format: %Y-%m-%dT%H:%M")
    if find_medication(session, patient_id, medication_id) is None:
        raise HTTPException(
            status_code=404, detail=f"Medication {medication_id} for patient {patient_id} not found")

    intakes = find_intakes(session, medication_id,
                           start_date=start_date, end_date=end_date)
    return intakes


@app.get("/patients/{patient_id}/intakes",  tags=["intakes"],
         responses={200: {"model": list[MedicationIntake]}, 404: {"model": Message}, 422: {"model": Message}})
def get_intakes_by_patient(patient_id: int,  start_date: str = None, end_date: str = None, session: Session = Depends(get_session)):
    try:
        if start_date is not None:
            date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
        if end_date is not None:
            date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise HTTPException(
            status_code=422, detail=f"Invalid date format for start_date {start_date}  or end_date {end_date}. Required format: %Y-%m-%dT%H:%M")

    if find_patient(session, patient_id=patient_id) is None:
        raise HTTPException(
            status_code=404, detail=f"Patient {patient_id} not found")

    intakes = find_intakes_by_patient(
        session, patient_id, start_date=start_date, end_date=end_date)
    return intakes


@app.delete("/patients/{patient_id}/medications/{medication_id}/intakes/{intake_id}",  tags=["intakes"],
            status_code=204,
            responses={404: {"model": Message}})
def delete_intake(patient_id: int, medication_id: int, intake_id: int, session: Session = Depends(get_session)):
    intake = find_intake(session, patient_id, medication_id, intake_id)
    if intake is not None:
        remove_intake(session, intake)
    else:
        raise HTTPException(
            status_code=404, detail=f"Medication {medication_id} not found for patient {patient_id}")

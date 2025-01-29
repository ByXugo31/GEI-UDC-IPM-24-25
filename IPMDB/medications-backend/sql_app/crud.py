from __future__ import annotations

from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from .models import Patient, Medication, Posology, Intake, MedicationIntake


def insert_patient(session: Session, patient: Patient) -> Patient | None:
    statement = select(Patient).where(Patient.code == patient.code)
    results = session.exec(statement)
    registered_patient = results.first()
    if registered_patient is None:
        session.add(patient)
        session.commit()
        session.refresh(patient)
        return patient
    else:
        return None


def find_patient(session: Session, **kwargs) -> Patient | None | list["Patient"]:
    patient_id = kwargs.get('patient_id', None)
    code = kwargs.get('code', None)
    start_index = kwargs.get('start_index', None)
    count = kwargs.get('count', None)
    if patient_id:
        statement = select(Patient).where(Patient.id == patient_id)
        results = session.exec(statement)
        patient = results.first()
        return patient
    if code:
        statement = select(Patient).where(Patient.code == code)
        results = session.exec(statement)
        patient = results.first()
        return patient
        
    statement = select(Patient)
    if start_index is not None:
        statement = statement.offset(start_index)
    if count is not None:
        statement = statement.limit(count)
    results = session.exec(statement)
    patients = results.all()
    return patients


def find_medication(session: Session, patient_id: int, medication_id: int) -> Medication | None:
    statement = select(Medication).where(
        Medication.patient_id == patient_id,
        Medication.id == medication_id)
    results = session.exec(statement)
    medication = results.first()
    return medication


def find_medications(session: Session, patient_id: int) -> list["Medication"]:
    statement = select(Medication).where(
        (Medication.patient_id == patient_id))
    results = session.exec(statement)
    medications = results.all()
    return medications


def find_posology(session: Session, patient_id: int, medication_id: int, posology_id: int) -> Posology | None:
    statement = select(Medication, Posology).where(
        Medication.patient_id == patient_id,
        Medication.id == medication_id,
        Posology.medication_id == medication_id,
        Posology.id == posology_id)
    results = session.exec(statement)
    data = results.first()
    if data is not None:
        _, posology = data
        return posology
    return None


def find_posologies(session: Session, patient_id: int, medication_id: int) -> list["Posology"]:
    statement = select(Medication, Posology).where(
        Medication.patient_id == patient_id,
        Medication.id == medication_id,
        Posology.medication_id == medication_id)
    results = session.exec(statement)
    posologies = []
    for _, posology in results.all():
        posologies.append(posology)
    return posologies


def insert_medication(session: Session, medication: Medication) -> Medication | None:
    try:
        session.add(medication)
        session.commit()
        session.refresh(medication)
        return medication
    except IntegrityError:
        return None


def insert_posology(session: Session, posology: Posology) -> Posology | None:
    try:
        session.add(posology)
        session.commit()
        session.refresh(posology)
        return posology
    except IntegrityError:
        return None

def update_posology_data(session: Session, posology: Posology) -> bool:
    try:
        session.add(posology)
        session.commit()
        session.refresh(posology)
        return True
    except IntegrityError:
        return False

def remove_patient(session: Session, patient: Patient):
    session.delete(patient)
    session.commit()


def remove_medication(session: Session, medication: Medication):
    session.delete(medication)
    session.commit()


def remove_posology(session: Session, posology: Posology):
    session.delete(posology)
    session.commit()


def update_patient_data(session: Session, new_patient: Patient) -> bool:
    patient = find_patient(session, patient_id=new_patient.id)
    if patient is not None:
        patient.name = new_patient.name
        patient.surname = new_patient.surname
        patient.code = new_patient.code
        session.add(patient)
        session.commit()
        session.refresh(patient)
        return True
    return False


def update_medication_data(session: Session, new_medication: Medication) -> bool:
    medication = find_medication(
        session, new_medication.patient_id, new_medication.id)
    if medication is not None:
        medication.name = new_medication.name
        medication.dosage = new_medication.dosage
        medication.start_date = new_medication.start_date
        medication.treatment_duration = new_medication.treatment_duration
        session.add(medication)
        session.commit()
        session.refresh(medication)
        return True
    return False


def insert_intake(session: Session, intake: Intake) -> Intake:
    session.add(intake)
    session.commit()
    session.refresh(intake)
    return intake


def find_intake(session: Session, patient_id: int, medication_id: int, intake_id: int) -> Intake | None:

    statement = select(Medication, Intake).where(
        Medication.id == medication_id,
        Medication.patient_id == patient_id,
        Intake.id == intake_id,
        Intake.medication_id == medication_id)
    result = session.exec(statement)
    data = result.first()
    if data is not None:
        _, intake = data
        return intake
    return None


def find_intakes(session: Session, medication_id: int, **kwargs) -> list["Intake"]:
    start_date = kwargs.get('start_date', None)
    end_date = kwargs.get('end_date', None)
    if start_date is not None and end_date is not None:
        statement = select(Intake).where(
            Intake.medication_id == medication_id,
            Intake.date >= start_date,
            Intake.date <= end_date)
    elif start_date is not None:
        statement = select(Intake).where(
            Intake.medication_id == medication_id,
            Intake.date >= start_date)
    elif end_date is not None:
        statement = select(Intake).where(
            Intake.medication_id == medication_id,
            Intake.date <= end_date)
    else:
        statement = select(Intake).where(
            Intake.medication_id == medication_id)
    results = session.exec(statement)
    intakes = results.all()
    return intakes


def find_intakes_by_patient(session: Session, patient_id: int, **kwargs) -> list["MedicationIntake"]:
    start_date = kwargs.get('start_date', None)
    end_date = kwargs.get('end_date', None)

    if start_date is not None and end_date is not None:
        statement = select(Medication, Intake).where(
            Medication.patient_id == patient_id,
            Medication.id == Intake.medication_id,
            Intake.date >= start_date,
            Intake.date <= end_date)
    elif start_date is not None:
        statement = select(Medication, Intake).where(
            Medication.patient_id == patient_id,
            Medication.id == Intake.medication_id,
            Intake.date >= start_date)
    elif end_date is not None:
        statement = select(Medication, Intake).where(
            Medication.patient_id == patient_id,
            Medication.id == Intake.medication_id,
            Intake.date <= end_date)
    else:
        statement = select(Medication, Intake).where(
            Medication.patient_id == patient_id,
            Medication.id == Intake.medication_id,
        )
    results = session.exec(statement)
    medication_and_intakes = results.all()
    intakes_by_medication = dict()
    for medication, intake in medication_and_intakes:
        if medication.id not in intakes_by_medication:
            intakes_by_medication[medication.id] = MedicationIntake(
                id=medication.id,
                name=medication.name,
                dosage=medication.dosage,
                start_date=medication.start_date,
                treatment_duration=medication.treatment_duration,
                posologies_by_medication=find_posologies(session, patient_id, medication.id),
                patient_id=medication.patient_id)
            
        intakes_by_medication[medication.id].intakes_by_medication.append(
            intake)

    return list(intakes_by_medication.values())


def remove_intake(session: Session, intake: Intake):
    session.delete(intake)
    session.commit()


from typing import Optional
from sqlmodel import Field, Relationship, SQLModel
from pydantic import BaseModel

class Message(BaseModel):
    detail: str

class Patient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    name: Optional[str]  = None
    surname: Optional[str] = None
    medications: list["Medication"] = Relationship(back_populates="patient", sa_relationship_kwargs={"cascade": "delete"})

class Medication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    dosage: float = Field(default=1.0)
    start_date: str
    treatment_duration: int = Field(default=1)
    patient_id: int = Field(foreign_key="patient.id")
    patient: Patient = Relationship(back_populates="medications")
    posology: list["Posology"] = Relationship(back_populates="medication_posology", sa_relationship_kwargs={"cascade": "delete"})
    intakes: list["Intake"] = Relationship(back_populates="medication_intake", sa_relationship_kwargs={"cascade": "delete"})

 
class Posology(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hour: int
    minute: int
    medication_id: int = Field(foreign_key="medication.id")
    medication_posology: Medication = Relationship(back_populates="posology")


class Intake(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: str
    medication_id: int = Field(foreign_key="medication.id")
    medication_intake: Medication = Relationship(back_populates="intakes")

class MedicationIntake(BaseModel):
    id: int
    name: str
    dosage: float
    start_date: str
    treatment_duration: int
    patient_id: int
    posologies_by_medication: Optional[list["Posology"]] = []
    intakes_by_medication: Optional[list["Intake"]] = []
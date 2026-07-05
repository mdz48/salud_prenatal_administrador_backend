from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    patient = "paciente"
    doctor = "doctor"
    recepcionist = "recepcionista"

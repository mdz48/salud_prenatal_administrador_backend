from dataclasses import dataclass


@dataclass
class LoginDTO:
    email: str
    password: str


@dataclass
class CreateAdminDTO:
    name: str
    last_name: str
    email: str
    phone: str | None
    password: str
    role: str

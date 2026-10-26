"""Seed sellers. Listings reference a seller by the index in `USERS`.

The WhatsApp number identifies a seed user on repeated runs: docs/backend/STRUCTURE.md#seed.
"""

from modules.users.schemas import UserCreate

USERS: list[UserCreate] = [
    UserCreate(whatsapp="+12125550147", first_name="Michael", last_name="Turner"),
    UserCreate(whatsapp="+13105550182", first_name="Jessica", last_name="Ramirez"),
    UserCreate(whatsapp="+17735550126", first_name="David", last_name="Kim"),
    UserCreate(whatsapp="+14155550193", first_name="Emily", last_name="Carter"),
    UserCreate(whatsapp="+13055550164", first_name="Carlos", last_name="Mendoza"),
    UserCreate(whatsapp="+12065550171", first_name="Sarah", last_name="Thompson"),
    UserCreate(whatsapp="+15125550138", first_name="Daniel", last_name="Brooks"),
]

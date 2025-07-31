from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from database import Base
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


def load_public_key():
    with open("db/keys/public_key.pem", "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())


def load_private_key():
    with open("db/keys/private_key.pem", "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )


public_key = load_public_key()
private_key = load_private_key()


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    students = relationship("Student", back_populates="subject")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    encrypted_name = Column(LargeBinary, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)

    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    subject = relationship("Subject", back_populates="students")

    def set_name(self, name: str):
        self.encrypted_name = public_key.encrypt(
            name.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def get_name(self) -> str:
        return private_key.decrypt(
            self.encrypted_name,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode()
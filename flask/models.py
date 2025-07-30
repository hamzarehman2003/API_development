from config import db
from sqlalchemy.orm import relationship
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def load_public_key():
    with open("db/keys/public_key.pem", "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())


def load_private_key():
    with open("db/keys/private_key.pem", "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=None)


public_key = load_public_key()
private_key = load_private_key()


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),  nullable=False)
    students = relationship(
        'Student', backref='subject', lazy=True
    )


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    encrypted_name = db.Column(db.LargeBinary, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    def set_name(self, plain_name):
        self.encrypted_name = public_key.encrypt(
            plain_name.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def get_name(self):
        private_key = load_private_key()
        return private_key.decrypt(
            self.encrypted_name,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode()

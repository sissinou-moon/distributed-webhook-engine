from argon2 import PasswordHasher

hash = PasswordHasher()

def hashPassword(password: str):
    return hash.hash(password)

def verifyHasedPassword(hashed: str, password: str):
    return hash.verify(hashed, password)
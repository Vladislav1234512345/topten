from random import choice
from string import digits, ascii_letters
from typing import LiteralString


def generate_password(
    population: str = digits + ascii_letters, length: int = 100
) -> str:
    password = ""
    for _ in range(length):
        password += choice(population)

    return password


def generate_verification_code(symbols: LiteralString = digits, length: int = 6) -> str:
    return generate_password(population=symbols, length=length)

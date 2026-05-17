from random import randint
from os import mkdir, listdir
PATH = 'meanings'
if PATH not in listdir(): mkdir(PATH)

with open(f'{PATH}.txt', 'w') as file:
    for i in range(10_000):
        file.write(f"{randint(-10_000, 10_000)}\n")
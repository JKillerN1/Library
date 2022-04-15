import requests
from pathlib import Path

folder = Path('books').mkdir(parents=True, exist_ok=True)



for i in range(1,11):
    url = f"https://tululu.org/txt.php?id={i}"
    filename = f'books/{i}.txt'

    response = requests.get(url)
    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)

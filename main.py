import requests
from bs4 import BeautifulSoup
from pathlib import Path
import os
import lxml
from urllib.error import HTTPError


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(response, filename, folder='books/'):
    file_name, avtor_name = filename
    filename_book = os.path.join(folder, f'{file_name}.txt')

    with open(filename_book, 'wb') as file:
        file.write(response.content)


def filename_f(book_url):
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1').text
    # print(title_tag)
    title_book, title_avtor = title_tag.split(' :: ')
    title_book = title_book.split()
    title_book = ' '.join(title_book)
    return title_book, title_avtor


if __name__ == "__main__":
    os.makedirs("books", exist_ok=True)
    url = "https://tululu.org/txt.php"
    # download = 'https://tululu.org'
    for book_num in range(1, 11):
        params = {"id": book_num}
        try:
            book_url = f'https://tululu.org/b{book_num}/'
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)
            # response.raise_for_status()
            # book_url = book_url.format(book_num)
            book_page = filename_f(response)
            # print(book_page)
            response2 = requests.get(url, params=params)
            check_for_redirect(response2)
            download_txt(response2, book_page)
        except requests.HTTPError:
            print("такой книги не существует")
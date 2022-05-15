import requests
from bs4 import BeautifulSoup
from pathlib import Path
import os
import lxml
from urllib.error import HTTPError
from urllib.parse import urljoin


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_book(response, filename, folder='books/'):
    file_name = filename
    filename_book = os.path.join(folder, f'{file_name}.txt')
    with open(filename_book, 'w', encoding="utf-8") as file:
        file.write(response.text)


def download_picture(response, filename, folder='images/'):
    download_url = 'https://tululu.org'
    response = requests.get(urljoin(download_url, filename))
    picture_name=filename.split('/')[2]
    path = os.path.join(folder, picture_name)
    with open(path, 'wb') as file:
        file.write(response.content)


def parse_book_page(id, book_url):
    response = requests.get(book_url.format(id=id))
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')

    title_tag = soup.find('h1').text
    title_book, title_avtor = title_tag.split(' :: ')
    title_book = title_book.split()
    title_book = ' '.join(title_book)

    title_tag = soup.find('div', class_='bookimage').find('img')['src']

    download_book(response, title_book, folder='books/')
    download_picture(response, title_tag, folder='images/')
    return title_book, title_avtor


if __name__ == "__main__":
    os.makedirs("books", exist_ok = True)
    os.makedirs("images", exist_ok = True)
    url_book = "https://tululu.org/txt.php"
    download_url = 'https://tululu.org'
    book_url = 'https://tululu.org/b{id}/'

    for book_num in range(1, 11):
        params = {"id": book_num}
        response = requests.get(url_book, params)
        response_p=requests.get(book_url)

        try:
            response.raise_for_status()
            #response_p.raise_for_status()
            check_for_redirect(response)
            parse_book_page(book_num, book_url)

            #download_picture(book_num, book_url)
            #check_for_redirect(response2)

            #print(urljoin(download, picture(response)))
        except requests.exceptions.HTTPError:
            print("такой книги не существует")
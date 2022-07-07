import requests
import argparse
from bs4 import BeautifulSoup
import os
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
    picture_name = filename.split('/')[2]
    path = os.path.join(folder, picture_name)
    with open(path, 'wb') as file:
        file.write(response.content)


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')

    title_tag = soup.find('h1').text
    title_book, title_author = title_tag.split(' :: ')
    title_book = title_book.split()
    title_book = ' '.join(title_book)
    title_author = title_author.split()
    title_author = ' '.join(title_author)

    print('Заголовок:', title_book)
    print('Автор:', title_author)

    genres = soup.find_all('span', class_='d_book')
    for genre in genres:
        genre_book = genre.find('a').text
        print('Жанр:', genre_book)

    title_tag = soup.find('div', class_='bookimage').find('img')['src']

    download_book(response, title_book, folder='books/')
    download_picture(response, title_tag, folder='images/')
    return title_book, title_author


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('id', type=int)
    parser.add_argument('id2', type=int)
    args = parser.parse_args()

    start_id = args.id
    end_id = args.id2

    os.makedirs("books", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    main_page_url = "https://tululu.org/txt.php"
    download_url = 'https://tululu.org'
    book_page_url = 'https://tululu.org/b{id}/'

    for book_num in range(start_id, end_id):
        params = {"id": book_num}
        response = requests.get(main_page_url, params)
        response_page = requests.get(book_page_url.format(id=params['id']))

        try:

            response.raise_for_status()
            response_page.raise_for_status()
            check_for_redirect(response)
            parse_book_page(response_page)

        except requests.exceptions.HTTPError:
            print('такой книги не существует')
            print()

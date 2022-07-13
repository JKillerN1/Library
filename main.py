import requests
import argparse
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def dowloand_comments(response):
    soup = BeautifulSoup(response.text, 'lxml')
    #print(response.text)
    comments = soup.find_all('div', class_='texts')
    #print(comments)
    for comment in comments:
        com = comment.find('span', class_='black').text
        print(com)


def download_book(response, id, filename, folder='books/'):
    file_name = filename
    #filename_book = os.path.join(folder, f'{id}.{file_name}.txt')
    with open(filename_book, 'w', encoding="utf-8") as file:
        file.write(response.text)


def download_picture(response, filename, folder='images/'):
    download_url = 'https://tululu.org'
    response = requests.get(urljoin(download_url, filename))
    picture_name = filename  # .split('/')[2]
    path = os.path.join(folder, picture_name)
    with open(path, 'wb') as file:
        file.write(response.content)


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')

    title_tag = soup.find('h1').text
    title_book, title_avtor = title_tag.split(' :: ')
    title_book = title_book.split()
    title_book = ' '.join(title_book)
    title_avtor = title_avtor.split()
    title_avtor = ' '.join(title_avtor)

    #  print('Заголовок:', title_book)
    #  print('Автор:', title_avtor)

    genres = soup.find_all('span', class_='d_book')
    genre_book = [genre.find('a').text for genre in genres]
    # for genre in genres:
    #   genre_book = genre.find('a').text
    # print('Жанр:', " ".join(genre_book))

    title_tag = soup.find('div', class_='bookimage').find('img')['src']

    # download_book(response, title_book, folder='books/')
    # download_picture(response, title_tag, folder='images/')
    return title_book, title_avtor, " ".join(genre_book)


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
        # print(book_page_url.format(id=params['id']))

        try:
            # response2 = requests.get(book_page_url.format(id=id))
            # response2.raise_for_status()
            response.raise_for_status()
            response_page.raise_for_status()
            check_for_redirect(response)
            print(parse_book_page(response_page))
            print(dowloand_comments(response_page))

            if parse_book_page(response_page):
                download_book(response, book_num, parse_book_page(response_page)[0], folder='books/')
                download_picture(response, parse_book_page(response_page)[0], folder='images/')



        except requests.exceptions.HTTPError:
            print('такой книги не существует')


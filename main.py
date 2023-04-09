import pathlib
import requests
import argparse
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import json
import logging
import time
from collections import OrderedDict


class FormatError(TypeError):
    pass


def find_book_numbers(soup):
    book_numbers = [number.get('href') for number in soup.select('a')
                    if '/b' in number.get('href')]

    del book_numbers[0:6]
    nonrepeating_book_numbers = list(OrderedDict.fromkeys(book_numbers))

    return nonrepeating_book_numbers


def check_for_redirect(response):
    if response.history:
        raise FormatError


def find_comments(soup):
    comments = soup.select("div.texts")
    all_comments = [comment.select_one('span.black').text
                    for comment in comments]
    return all_comments


def download_book(response, id, filename, folder='books/'):
    file_name = filename
    book_file_path = os.path.join(folder, f'{id} {file_name}.txt')

    with open(book_file_path, 'w+', encoding="utf-8") as file:
        file.write(response.text)


def download_picture(title_tag, book_url, folder='images/'):
    response = requests.get(urljoin(book_url, title_tag))
    response.raise_for_status()
    picture_name = title_tag.split('/')[2]
    path = os.path.join(folder, picture_name)
    with open(path, 'wb') as file:
        file.write(response.content)


def parse_book_page(soup):
    title_tag = soup.select_one('h1').text
    title_book, title_author = title_tag.split(' :: ')
    title_book = title_book.strip()
    title_author = title_author.strip()

    genres = soup.select('span.d_book')
    books_genres = [genre.select_one('a').text for genre in genres]

    picture_url = soup.select_one("div.bookimage img")['src']

    book_params = {
        "title": title_book,
        "author": title_author,
        "pic_url": picture_url,
        "comments": find_comments(soup),
        "genres": " ".join(books_genres),
    }

    return book_params


logger = logging.getLogger(__file__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Напишите id книг, с какой по какую надо скачать')
    parser.add_argument('start_page', type=int, help='странциа с которой нужно начинать скачивать книги')
    parser.add_argument('end_page', type=int, help='странциа по которую нужно скачивать книги')
    parser.add_argument("--dest_folder", action='store_const', const=pathlib.Path().resolve(), help='путь к каталогу с результатами парсинга: картинкам, книгам, JSON')
    parser.add_argument("--skip_imgs", action="store_true", help='не скачивать картинки')
    parser.add_argument("--skip_txt", action="store_true", help='не скачивать книги')
    parser.add_argument("--json_path", default=pathlib.Path().resolve(), help='указать свой путь к *.json файлу с результатами')

    args = parser.parse_args()

    start_page = args.start_page
    end_page = args.end_page

    os.makedirs("books", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    connection_count = 0
    book_page_url = 'https://tululu.org/b{id}/'

    '''if (args.dest_folder):
        logging.basicConfig(level=logging.INFO)
        logger.info(pathlib.Path().resolve())'''

    books_params=[]
    for page in range(start_page, end_page):
        try:
            url = f'https://tululu.org/l55/{page}/'
            response = requests.get(url)
            check_for_redirect(response)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')
            book_numbers = find_book_numbers(soup)

            for number, book_number in enumerate(book_numbers):
                try:
                    book_id = book_number.strip('/').lstrip("b")
                    param = {'id': book_id}

                    book_url_page = f'https://tululu.org/{book_number}'
                    book_url = f'https://tululu.org/txt.php'

                    page_response = requests.get(book_url_page)
                    page_response.raise_for_status()
                    check_for_redirect(page_response)

                    book_response = requests.get(book_url, params=param)
                    book_response.raise_for_status()
                    check_for_redirect(book_response)

                    soup_book = BeautifulSoup(page_response.text, 'lxml')

                    disassembled_book = parse_book_page(soup_book)

                    books_params.append(disassembled_book)

                    if not args.skip_txt:
                        download_book(book_response,
                                      book_id,
                                      disassembled_book["title"],
                                      folder='books/')

                    if not args.skip_imgs:
                        download_picture(disassembled_book["pic_url"],
                                         book_page_url, folder='images/')

                except FileNotFoundError:
                    logging.basicConfig(level=logging.INFO)
                    logger.info("такой книги не существует")

                except FormatError:
                    logging.basicConfig(level=logging.INFO)
                    logger.info("такой книги не существует!")

                except requests.exceptions.ConnectionError:
                    time.sleep(5)
                    connection_count += 1
                    logging.basicConfig(level=logging.INFO)
                    logger.info("Прервано соединение при скачивании книги")
                    if connection_count == 10:
                        time.sleep(3600)


        except requests.exceptions.HTTPError:
            logging.basicConfig(level=logging.INFO)
            logger.info("такой ссылки не существует")

        except FormatError:
            logging.basicConfig(level=logging.INFO)
            logger.info("такой страницы не существует!")

        except requests.exceptions.ConnectionError:
            time.sleep(5)
            connection_count += 1
            logging.basicConfig(level=logging.INFO)
            logger.info("Прервано соединение")
            if connection_count == 10:
                time.sleep(3600)

    with open(os.path.join(args.json_path, "books_params.json"), "a",
              encoding="utf-8") as file:
        json.dump(books_params, file, ensure_ascii=False)


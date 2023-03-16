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


def find_book_numbers(soup):
    book_numbers = []
    
    for number in soup.select('a'):
        if '/b' in number.get('href'):
            book_numbers.append(number.get('href'))
    del book_numbers[0:6]
    nonrepeating_book_numbers = list(OrderedDict.fromkeys(book_numbers))

    return nonrepeating_book_numbers


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def find_comments(soup):
    comments = soup.select("div.texts")
    all_comments = []
    for comment in comments:
        comment = comment.select_one('span.black').text
        all_comments.append(comment)
    return all_comments


def download_book(response, id, filename, folder='books/'):
    file_name = filename
    book_file_path = os.path.join(folder, f'{id} {file_name}.txt')

    with open(book_file_path, 'w+', encoding="utf-8") as file:
        file.write(response.text)


def download_picture(title_tag, filename, book_url, folder='images/'):
    response = requests.get(urljoin(book_url, filename))
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
    genres_books = [genre.select_one('a').text for genre in genres]

    picture_url = soup.select_one("div.bookimage img")['src']

    book_params = {
        "title": title_book,
        "author": title_author,
        "pic_url": picture_url,
        "comments": find_comments(soup),
        "genres": " ".join(genres_books),
    }

    return book_params


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Напишите id книг, с какой по какую надо скачать')
    parser.add_argument('start_page', type=int, help='странциа с которой нужно начинать скачивать книги')
    parser.add_argument('end_page', type=int, help='странциа по которую нужно скачивать книги')
    parser.add_argument("--dest_folder", action="store_true", help='путь к каталогу с результатами парсинга: картинкам, книгам, JSON')
    parser.add_argument("--skip_imgs", action="store_true", help='не скачивать картинки')
    parser.add_argument("--skip_txt", action="store_true", help='не скачивать книги')
    parser.add_argument("--json_path", default=pathlib.Path().resolve(), help='указать свой путь к *.json файлу с результатами')

    args = parser.parse_args()

    start_page = args.start_page
    end_page = args.end_page

    os.makedirs("books", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    text_book_page_url = "https://tululu.org/txt.php"
    book_page_url = 'https://tululu.org/b{id}/'
    book_url = 'http://tululu.org'

    if (args.dest_folder):
        logging.basicConfig(level=logging.INFO)
        logging.info(pathlib.Path().resolve())

    for page in range(start_page, end_page):
        try:
            url = f'https://tululu.org/l55/{page}/'
            response = requests.get(url)
            response.raise_for_status()
            #print(response.is_redirect)
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            list_book_numbers=find_book_numbers(soup)
            try:
                for number in range(25):
                    book_number = list_book_numbers[number]
                    param = {'id': book_number.split("/")[1].lstrip("b")}
                    bookUrl_page = f'https://tululu.org{book_number}'
                    bookurl = f'https://tululu.org/txt.php'
                    
                    response_page = requests.get(bookUrl_page)
                    response_page.raise_for_status()
                    response_book = requests.get(bookurl, params=param)
                    response_book.raise_for_status()

                    soup_book = BeautifulSoup(response_page.text, 'lxml')
    
                    disassembled_book = parse_book_page(soup_book)
    
                    with open(f"{args.json_path}\\books_params.json", "a",
                              encoding="utf-8") as file:
                        json.dump(disassembled_book, file, ensure_ascii=False)
                        file.write("\n")

                    if not args.skip_txt:
                        download_book(response_book, find_book_numbers(soup)[number].split("/")[1].lstrip("b"),
                                      disassembled_book["title"], folder='books/')

                    if not args.skip_imgs:
                        tag = soup_book.select_one('div.bookimage img')['src']
                        download_picture(tag, disassembled_book["pic_url"], book_url, folder='images/')
    
            except FileNotFoundError:
                print('такой книги не существует)')
    
        except requests.exceptions.HTTPError:
            print('такой книги не существует')

        except requests.exceptions.ConnectionError:
            time.sleep(1)
            print("Прервано соединение")

     

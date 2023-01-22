import pathlib
import requests
import argparse
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import json
import logging


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def find_comments(soup):
    comments = soup.select("div.texts")
    all_comments = []
    for comment_people in comments:
        comment = comment_people.select_one('span.black').text
        all_comments.append(comment)
    return all_comments


def download_book(response, id, filename, folder='books/'):
    file_name = filename
    book_file_path = os.path.join(folder, f'{id} {file_name}.txt')

    with open(book_file_path, 'w+', encoding="utf-8") as file:
        file.write(response.text.replace(" ", ""))


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

    return title_book, title_author, " ".join(genres_books),picture_url


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Напишите id книг, с какой по какую надо скачать')
    parser.add_argument('start_page', type=int)
    parser.add_argument('end_page', type=int)

    parser.add_argument("--dest_folder",action="store_true", help='путь к каталогу с результатами парсинга: картинкам, книгам, JSON')
    parser.add_argument("--skip_imgs",action="store_true", help='не скачивать картинки')
    parser.add_argument("--skip_txt",action="store_true", help='не скачивать книги')
    parser.add_argument("--json_path",action="store_true",default=pathlib.Path().resolve(), help='указать свой путь к *.json файлу с результатами')

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
        url = f'https://tululu.org/l55/{page}/'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        book_number = []
        for number in soup.select('a'):
            if '/b' in number.get('href'):
                book_number.append(number.get('href'))

        for number in book_number:
            if number != '/b239/':
                book_number.remove(number)
            else:
                break

        nonrepeating_book_number = []
        for number in book_number:
            if number not in nonrepeating_book_number:
                nonrepeating_book_number.append(number)

        for number in range(3, 7):

            bookUrl_page = f'https://tululu.org{nonrepeating_book_number[number]}'
            bookurl = f'https://tululu.org/txt.php?id={nonrepeating_book_number[number].split("/")[1].lstrip("b")}'
            text_book_page_url = f"https://tululu.org/txt.php/id={nonrepeating_book_number[number]}"

            try:
                response_page = requests.get(bookUrl_page)
                response_page.raise_for_status()
                soup_book = BeautifulSoup(response_page.text, 'lxml')

                disassembled_book = parse_book_page(soup_book)

                response_book = requests.get(bookurl)
                response_book.raise_for_status()

                if disassembled_book:

                    book_params = {
                        "title": disassembled_book[0],
                        "author": disassembled_book[1],
                        "pic_url": disassembled_book[3],
                        "comments": find_comments(soup_book),
                        "genres": disassembled_book[2],
                    }

                    if book_params:
                        json_object = json.dumps(book_params, ensure_ascii=False)
                        if not args.json_path:
                            with open(f"{pathlib.Path().resolve()}\\books_params.json", "a",
                                      encoding="utf-8") as file:
                                file.write(json_object+'\n')
                        else:
                            with open(f"{args.json_path}\\books_params.json", "a",
                                      encoding="utf-8") as file:
                                file.write(json_object+'\n')

                        if not args.skip_txt:
                            download_book(response_book, nonrepeating_book_number[i].split("/")[1].lstrip("b"), book_params["title"], folder='books/')

                        if not args.skip_imgs:
                            tag = soup_book.select_one('div.bookimage img')['src']
                            download_picture(tag, book_params["pic_url"], book_url, folder='images/')

            except FileNotFoundError:
                print('такой книги не существует')
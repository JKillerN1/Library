import requests
import argparse
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import json


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def find_comments(soup):
    comments = soup.find_all('div', class_='texts')
    all_comments=[]
    for comment_people in comments:
        comment = comment_people.find('span', class_='black').text
        all_comments.append(comment)
    return all_comments


def download_book(response, id, filename, folder='books/'):
    file_name = filename
    book_file_path = os.path.join(folder, f'{id} {file_name}.txt')
    with open(book_file_path, 'w', encoding="utf-8") as file:
        file.write(response.text)


def download_picture(title_tag, filename, folder='images/'):

    response = requests.get(urljoin('http://tululu.org', filename))
    response.raise_for_status()
    picture_name = title_tag.split('/')[2]
    path = os.path.join(folder, picture_name)
    with open(path, 'wb') as file:
        file.write(response.content)


def parse_book_page(soup):

    title_tag = soup.find('h1').text
    title_book, title_author = title_tag.split(' :: ')
    title_book = title_book.strip()
    title_author = title_author.strip()
    
    genres = soup.find_all('span', class_='d_book')
    genres_books = [genre.find('a').text for genre in genres]

    picture_url = soup.find('div', class_='bookimage').find('img')['src']

    book_params = {
        "title": title_book,
        "author": title_author,
        "genres": " ".join(genres_books),
        "pic_url": picture_url,
        "comments": find_comments(soup),
    }

    return book_params


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Напишите id книг, с какой по какую надо скачать')
    parser.add_argument('start_id', type=int)
    parser.add_argument('end_id', type=int)
    args = parser.parse_args()

    start_id = args.start_id
    end_id = args.end_id

    os.makedirs("books", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    text_book_page_url = "https://tululu.org/txt.php"
    book_page_url = 'https://tululu.org/b{id}/'

    for book_num in range(start_id, end_id):
        params = {"id": book_num}
        response = requests.get(text_book_page_url, params)
        response_page = requests.get(book_page_url.format(id=params['id']))
        try:
            soup = BeautifulSoup(response_page.text, 'lxml')
            response.raise_for_status()
            response_page.raise_for_status()
            check_for_redirect(response)
            disassembled_book = parse_book_page(soup)
            
            books_name = disassembled_book["title"]
            picture_books_url = disassembled_book["pic_url"]
            if disassembled_book:
                download_book(response, book_num, books_name, folder='books/')
                tag = soup.find('div', class_='bookimage').find('img')['src']
                download_picture(tag, picture_books_url, folder='images/')
            
        except requests.exceptions.HTTPError:
            print('такой книги не существует')

        except requests.exceptions.ConnectionError:
            print('прервано соединение')
            time.sleep(10)

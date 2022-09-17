import requests
import argparse
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def find_comments(soup):
    comments = soup.find_all('div', class_='texts')
    for comment_people in comments:
        comment = comment_people.find('span', class_='black').text
        return comment


def download_book(response, id, filename, folder='books/'):
    file_name = filename
    filename_book = os.path.join(folder, f'{id} {file_name}.txt')
    with open(filename_book, 'w', encoding="utf-8") as file:
        file.write(response.text)


def download_picture(title_tag, filename, folder='images/'):
    
    download_url = 'https://tululu.org'
    response = requests.get(urljoin(download_url, filename))
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

    return title_book, title_author, " ".join(genres_books)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Напишите id книг, с какой по какую надо скачать')
    parser.add_argument('id_first_book', type=int)
    parser.add_argument('id_second_book', type=int)
    args = parser.parse_args()

    start_id = args.id_first_book
    end_id = args.id_second_book

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
            parse_book = parse_book_page(soup)
            find_comments(soup)

            if parse_book:
                tag = soup.find('div', class_='bookimage').find('img')['src']
                download_book(response, book_num, parse_book[0], folder='books/')
                download_picture(tag, parse_book[0], folder='images/')

        except requests.exceptions.HTTPError:
            print('такой книги не существует')

        except requests.exceptions.ConnectionError:
            print('прервано соединение')
            time.sleep(10)

'''k=0
for i in range(100,1000):
    if i%7==0 and i%5!=0 and i%9!=0:
        k+=1
print(k)
print(len(list(filter(lambda x: x % 7 == 0 and x % 5 != 0 and x % 9 != 0,range(100,1000)))))'''

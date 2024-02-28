import sqlite3
import sys

import requests
from bs4 import BeautifulSoup




def setupTableInDB():
    connection = sqlite3.connect("cached.db")
    #print(connection.total_changes)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE books (fetched_term TEXT, author TEXT, title TEXT, publisher TEXT, "
                   "year INTEGER, pages_count INTEGER, language TEXT, size TEXT, "
                   "extension TEXT, link1 TEXT, link2 TEXT)")
    connection.close()


def fetchColumnOfDB(column):
    connection = sqlite3.connect("cached.db")
    cursor = connection.cursor()
    resp = cursor.execute(f"SELECT {column} FROM books").fetchall()
    connection.close()
    return resp

def cleanDBTable(table_name):
    connection = sqlite3.connect("cached.db")
    with connection:
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM {table_name};')
        connection.commit()

def insertRecordListToDB(records):
    connection = sqlite3.connect("cached.db")
    with connection:
        cursor = connection.cursor()
        for record in records:
            cursor.execute(f"INSERT INTO books (fetched_term, author, title, publisher, year, pages_count, language, size, extension, link1, link2) VALUES (\"{record['fetched_term']}\", \"{record['author']}\", \"{record['title']}\", \"{record['publisher']}\", \"{record['year']}\", \"{record['pages_count']}\", \"{record['language']}\", \"{record['size']}\", \"{record['extension']}\", \"{record['link1']}\", \"{record['link2']}\");")
        connection.commit()


def fetchTermInLibGenSearchEngine(term):  # Will return all extracted book information from response table as a list of bs4 objects
    base_url = "https://www.libgen.is/search.php?&res=25&req={term}&phrase=1&view=simple&column=def&sort=def&sortmode=ASC&page={page_number}"
    page_counter = 1
    books = []
    while True:
        resp = requests.get(base_url.format(term=term, page_number=page_counter))
        bs_obj = BeautifulSoup(resp.text, "html.parser")
        if bs_obj.title.string == '504 Gateway Time-out':
            sys.exit('504 Gateway Time :(')
        with open('typically-fetched.html', 'w', encoding="utf-8") as file:
            file.write(resp.text)
        with open('typically-fetched.html', 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, "html.parser")
        if len(soup.select('body > table.c')) <= 0:  # Last table page
            break
        books_table = soup.select('body > table.c')[0]  # A tag object
        # First book is in the 1st index and all even indexes are empty
        # So you should just crawl on even indexes that starts from 1 and smaller than length
        if len(books_table) <= 1: # Last table page
            break
        for counter in range(1, len(books_table), 2):
            next_book_index = list(books_table.contents[counter].children)  # A record of books table in html response page
            # for catching exceptions due to " and ' chars while inserting to sql (sql query interference)
            # .replace('\"','\'')
            # print(next_book_index)
            books.append({'fetched_term': term, 'author': next_book_index[2].get_text().replace('\"','\''), 'title': next_book_index[4].get_text().replace('\"','\''),
                          'publisher': next_book_index[6].get_text().replace('\"','\''), 'year': next_book_index[8].get_text(),
                          'pages_count': next_book_index[10].get_text(), 'language': next_book_index[12].get_text(),
                          'size': next_book_index[14].get_text(), 'extension': next_book_index[16].get_text(),
                          'link1': next_book_index[18].contents[0]['href'], 'link2': next_book_index[19].contents[0]['href']})
        #print(books)
        print(f'page number {page_counter} of this term fetched successfully ...')
        page_counter += 1
    return books









if __name__ == "__main__":
    entry_term = input('Hi, Please give me your intended term to search in lib.gen -> : ')
    insertRecordListToDB(fetchTermInLibGenSearchEngine(term=entry_term))
    #fetchTermInLibGenSearchEngine('combine')
    #setupTableInDB()
    #fetchColumnOfDB('fetched_term')
    #insertRecordListToDB([{'fetched_term': 'combine', 'author': 'testt', 'title': 'Combine or Combust Co-operating on Chemicals and Hazardous Substances Management 978-981-05-9468-8', 'publisher': 'test', 'year': '1423', 'pages_count': '151', 'language': 'English', 'size': '9 Mb', 'extension': 'pdf', 'link1': 'http://library.lol/main/C6E5F4C8E901702283EDC8D4EFE23657', 'link2': 'http://libgen.li/ads.php?md5=C6E5F4C8E901702283EDC8D4EFE23657'}])
    #cleanDBTable('books')
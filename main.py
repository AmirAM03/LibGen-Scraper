import sqlite3
import sys

import requests
from bs4 import BeautifulSoup
import texttable


def setup_table_in_db():
    connection = sqlite3.connect("cached.db")
    #  print(connection.total_changes)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE books (fetched_term TEXT, author TEXT, title TEXT, publisher TEXT, "
                   "year INTEGER, pages_count INTEGER, language TEXT, size TEXT, "
                   "extension TEXT, link1 TEXT, link2 TEXT)")
    connection.close()


def fetch_db_column(column):
    connection = sqlite3.connect("cached.db")
    cursor = connection.cursor()
    resp = cursor.execute(f"SELECT {column} FROM books").fetchall()
    connection.close()
    return resp


def clean_db_table(table_name):
    connection = sqlite3.connect("cached.db")
    with connection:
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM {table_name};')
        connection.commit()


def insert_record_list_to_db(records):
    connection = sqlite3.connect("cached.db")
    with connection:
        cursor = connection.cursor()
        for record in records:
            cursor.execute(f"INSERT INTO books (fetched_term, author, title, publisher, year, pages_count, language, size, extension, link1, link2) VALUES (\"{record['fetched_term']}\", \"{record['author']}\", \"{record['title']}\", \"{record['publisher']}\", \"{record['year']}\", \"{record['pages_count']}\", \"{record['language']}\", \"{record['size']}\", \"{record['extension']}\", \"{record['link1']}\", \"{record['link2']}\");")
        connection.commit()


def fetch_db_record_using_certain_fetched_term(term):
    connection = sqlite3.connect("cached.db")
    with connection:
        cursor = connection.cursor()
        resp = cursor.execute(f"SELECT * FROM books WHERE fetched_term = \"{term}\";").fetchall()
        return resp


def delete_relevant_term_records_from_db(term):
    connection = sqlite3.connect("cached.db")
    with connection:
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM books WHERE fetched_term = \"{term}\";')
        connection.commit()


def fetch_term_in_lib_gen_search_engine(term):
    # Will return all extracted book information from response table as a list of bs4 objects
    base_url = ("https://www.libgen.is/search.php?&res=100&req={term}"
                "&phrase=1&view=simple&column=def&sort=def&sortmode=ASC&page={page_number}")
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
        if len(books_table) <= 1:
            #  Last table page
            break
        for counter in range(1, len(books_table), 2):
            next_book_index = list(books_table.contents[counter].children)
            # A record of books table in html response page
            # for catching exceptions due to " and ' chars while inserting to sql (sql query interference)
            # .replace('\"','\'')
            # print(next_book_index)
            books.append({'fetched_term': term, 'author': next_book_index[2].get_text().replace('\"', '\''),
                          'title': next_book_index[4].get_text().replace('\"', '\''),
                          'publisher': next_book_index[6].get_text().replace('\"', '\''),
                          'year': next_book_index[8].get_text(),
                          'pages_count': next_book_index[10].get_text(), 'language': next_book_index[12].get_text(),
                          'size': next_book_index[14].get_text(), 'extension': next_book_index[16].get_text(),
                          'link1': next_book_index[18].contents[0]['href'],
                          'link2': next_book_index[19].contents[0]['href']})
        #  print(books)
        print(f'page number {page_counter} of this term fetched successfully ...')
        page_counter += 1
    return books


def print_results_table(books_list):
    table = texttable.Texttable(120)
    table.set_cols_align(["c", "c", "c", "c", "c", "c", "c", "c", "c", "c", "c"])
    table.set_cols_dtype(["t", "t", "t", "t", "i", "i", "t", "t", "t", "t", "t"])
    table.set_cols_valign(["m", "m", "m", "m", "m", "m", "m", "m", "m", "m", "m"])
    table.add_row(
        ["Relevant Fetched Term", "Author", "Title", "Publisher", "Publication Year", "Pages Count", "Language",
         "File Size", "Extension", "1st Path", "2nd Path"])
    for record in books_list:
        table.add_row(record)
    print(table.draw())


def print_already_fetched_terms():
    connection = sqlite3.connect("cached.db")
    with connection:
        cursor = connection.cursor()
        resp = cursor.execute(f"SELECT (fetched_term) FROM books;").fetchall()
        print('\n<======= List Of All Fetched Terms =======>')
        for i in set(resp):
            print(f' - {i[0]}')
        print('<========================================>')


if __name__ == "__main__":
    #  insertRecordListToDB(fetchTermInLibGenSearchEngine(term=entry_term))
    #  fetchTermInLibGenSearchEngine('combine')
    #  setup_table_in_db()
    #  fetch_db_column()
    #  insertRecordListToDB([{'fetched_term': 'combine', 'author': 'testt',
    #  'title': 'Combine or Combust Co-operating on Chemicals and Hazardous Substances Management 978-981-05-9468-8',
    #  'publisher': 'test', 'year': '1423',
    #  'pages_count': '151', 'language': 'English', 'size': '9 Mb', 'extension': 'pdf',
    #  'link1': 'http://library.lol/main/C6E5F4C8E901702283EDC8D4EFE23657',
    #  'link2': 'http://libgen.li/ads.php?md5=C6E5F4C8E901702283EDC8D4EFE23657'}])
    #  cleanDBTable('books')
    print('Hi, Welcome to the feature selection section. '
          'Please select your intended option based on following guid table')

    tableObj = texttable.Texttable(120)
    tableObj.set_cols_align(["l", "c", "c", "r"])
    tableObj.set_cols_dtype(["i", "t", "t", "t"])
    tableObj.set_cols_valign(["t", "t", "m", "b"])
    tableObj.add_rows([
        ["Activation Key", "Option Name", "Need Connection", "Option Description"],
        [1, 'Fetch A Term', '✅', 'Give a term to program then get all existed relevant books in LibGen'],
        [2, 'Get Cached Terms', '❌', 'Get the list of already fetched terms and cached in program data base'],
        [3, 'Check Fetch Status', '❌', 'Give a term to program to check fetch status of it'],
        [4, 'Re-Fetch an existing term', '✅',
         'Fetch an already fetched term again and replace new results instead of previous records into data base'],
        [5, 'Clean DB', '❌', 'Clear all Data Base records (Reset DB)']
    ])
    print(tableObj.draw())

    entry_term = input('Now, Input your intended option -> : ')

    if entry_term == '1':
        entry_term = input('Now, Input your intended term to fetch -> : ')
        db_result = fetch_db_record_using_certain_fetched_term(entry_term)
        if len(db_result):
            print_results_table(db_result)
        else:
            #  print('There is nothing to show in cached database')
            insert_record_list_to_db(fetch_term_in_lib_gen_search_engine(entry_term))
            print(fetch_db_record_using_certain_fetched_term(entry_term))
            print_results_table(fetch_db_record_using_certain_fetched_term(entry_term))
    elif entry_term == '2':
        print_already_fetched_terms()
    elif entry_term == '3':
        entry_term = input('Now, Input your intended term to check status -> : ')
        db_result = fetch_db_record_using_certain_fetched_term(entry_term)
        print('\n<!!!!!!!!!!!!!!!>')
        if len(db_result):
            print('There is some relevant records in our database so this term was already fetched !')
        else:
            print('Not Found any related records, you should fetch this term for first time using option number 1')
        print('<!!!!!!!!!!!!!!!>\n')
    elif entry_term == '4':
        entry_term = input('Now, Input your intended term to re-fetch -> : ')
        delete_relevant_term_records_from_db(entry_term)
        insert_record_list_to_db(fetch_term_in_lib_gen_search_engine(entry_term))
        print(fetch_db_record_using_certain_fetched_term(entry_term))
        print_results_table(fetch_db_record_using_certain_fetched_term(entry_term))
    elif entry_term == '5':
        clean_db_table('books')
        print('Data Base Cleared Successfully!')

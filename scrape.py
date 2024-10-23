from bs4 import BeautifulSoup as bs
from ebooklib import epub
import ebooklib
import os

authors = ['colossus']


def scrape(author):

    chapters = []

    filename = f"{os.getcwd()}/books/epub/{author}.epub"

    book = epub.read_epub(filename)
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

    for i, ch in enumerate(items[1:]):
        chapter = chapter_to_str(ch)
        chapters.append(chapter)
        with open(f"test/{author}_{i}.txt", 'w') as file:
            file.write(chapter)
    
    with open(f"books/txt/{author}.txt", "w") as file:
        file.write(' '.join(chapters))


def chapter_to_str(chapter):
    soup = bs(chapter.get_body_content(), 'html.parser')
    text = [p.get_text() for p in soup.find_all('p')]
    return ' '.join(text)

if __name__ == "__main__":
    for author in authors:
        scrape(author)
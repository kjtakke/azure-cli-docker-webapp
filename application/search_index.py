from bs4 import BeautifulSoup
import os
import json

search_html = '''
<div style="position: absolute; top: 22px; right: 60px; margin-top:2px;">
<a href="/search" style="color: white; text-decoration: none; background-color: #303033; padding: 5px 10px; border-radius: 5px;">Search</a>
</div>
'''

docs_dir = 'static/docs'
index_file = 'templates/search/search_index.json'


def add_search_link(file_path):
    """
    Adds a search link HTML snippet to the beginning of an HTML file. The method searches 
    for the `<body>` tag to insert the content. If `<body>` is not found, it attempts to 
    insert the content into the `<head>` or `<html>` tags as a fallback.

    :param file_path: Path to the HTML file where the search link HTML will be inserted
    :type file_path: str
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

        # Try to find the body tag first
        body_tag = soup.body
        if body_tag:
            # Insert the search link HTML at the beginning of the body
            body_tag.insert(0, BeautifulSoup(search_html, 'html.parser'))
        else:
            # Fallback: try to insert into the head or html tag if body is not found
            head_tag = soup.head
            if head_tag:
                head_tag.insert_before(BeautifulSoup(search_html, 'html.parser'))
            else:
                html_tag = soup.html
                if html_tag:
                    html_tag.insert(0, BeautifulSoup(search_html, 'html.parser'))
                else:
                    print(f"No body, head, or html tag found in {file_path}")

        # Write changes back to the file
        with open(file_path, 'w', encoding='utf-8') as outfile:
            outfile.write(str(soup))

def search_link():
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                add_search_link(file_path)


def generate_search_index():
    index_data = []
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file).replace('\\', '/')  # Replace backslashes with forward slashes
                with open(file_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    title = soup.title.string if soup.title else ''
                    body = soup.get_text()
                    body = body.replace("\n", "<br>")
                    index_data.append({
                        'file_path': file_path.replace(docs_dir + '/', ''),
                        'title': title,
                        'body': body
                    })
    with open(index_file, 'w', encoding='utf-8') as json_file:
        json.dump(index_data, json_file, ensure_ascii=False, indent=2)
    print(f"Index created: {index_file}")


if __name__ == "__main__":
    generate_search_index()
    search_link()
    pass

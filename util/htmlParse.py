from bs4 import Comment, BeautifulSoup
import re
import time




def retry(func):
    def wrap(*args, **kwargs):
        delays = [1, 5, 10]
        for i, delay in enumerate(delays):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f'Error: {e} | Function: {func.__name__} | Args: {args} | Kwargs: {kwargs}')
                if i < len(delays) - 1:
                    time.sleep(delay)
        return ''
    return wrap


def simplify_html(html, keep_attr=False):
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    #  remove all attributes
    if not keep_attr:
        for tag in soup.find_all(True):
            tag.attrs = {}
    #  remove empty tags recursively
    while True:
        removed = False
        for tag in soup.find_all():
            if not tag.text.strip():
                tag.decompose()
                removed = True
        if not removed:
            break
    #  remove href attributes
    for tag in soup.find_all("a"):
        del tag["href"]
    #  remove comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    def concat_text(text):
        text = "".join(text.split("\n"))
        text = "".join(text.split("\t"))
        text = "".join(text.split(" "))
        return text

    # remove all tags with no text
    for tag in soup.find_all():
        children = [child for child in tag.contents if not isinstance(child, str)]
        if len(children) == 1:
            tag_text = tag.get_text()
            child_text = "".join([child.get_text() for child in tag.contents if not isinstance(child, str)])
            if concat_text(child_text) == concat_text(tag_text):
                tag.replace_with_children()
    #  if html is not wrapped in a html tag, wrap it

    # remove empty lines
    res = str(soup)
    lines = [line for line in res.split("\n") if line.strip()]
    res = "\n".join(lines)
    return res


def clean_xml(html):
    # remove tags starts with <?xml
    html = re.sub(r"<\?xml.*?>", "", html)
    # remove tags starts with <!DOCTYPE
    html = re.sub(r"<!DOCTYPE.*?>", "", html)
    # remove tags starts with <!DOCTYPE
    html = re.sub(r"<!doctype.*?>", "", html)
    return html


def clean_html(html: str) -> str:
    html=simplify_html(html)
    html=clean_xml(html)
    return html
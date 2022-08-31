from bs4 import BeautifulSoup

def get_tags(text):
    soup = BeautifulSoup(text)
    m = {}
    for i in soup.find_all("input", type="hidden"):
        m[i.attrs["name"]] = i.attrs["value"]
    return m

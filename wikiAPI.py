import requests
import os
import numpy as np

languages = ['en', 'sk', 'de', 'fr', 'it', 'cz', 'pl', 'hr', 'nl']
n_articles = 50

class attributes(object):
    def __init__(self):
        self.atts = {}
        self.atts['action'] = 'query'  # action=query
        self.atts['prop'] = 'extracts|links'  # prop=info
        self.atts['format'] = 'json'  # format=json
        # my_atts['titles'] = 'Freddie Mercury' # titles=Stanford%20University
        self.atts['explaintext'] = True
        self.atts['pllimit'] = 'max'
        self.atts['plnamespace'] = 0

    def set_title(self, title):
        self.atts['titles'] = title

    def reset(self):
        self.atts['prop'] = 'extracts|links'
        try:
            del self.atts['plcontinue']
        except KeyError:
            pass

    def set_links_only(self, pl):
        self.atts['prop'] = 'extracts|links'
        self.atts['plcontinue'] = pl

def send_request(title):
    my_atts.set_title(title)
    resp = requests.get(baseurl, params=my_atts.atts).json()
    return resp

def get_article_data(title):
    my_atts.reset()
    resp = send_request(title)
    try:
        text = [r['extract'] for r in resp['query']['pages'].values()][0]
        links = [link['title'] for link in [r['links'] for r in resp['query']['pages'].values()][0]]
    except KeyError:
        return None, None

    while True:
        try:
            pl = resp['continue']['plcontinue']
        except KeyError:
            break
        my_atts.set_links_only(pl)
        resp = send_request(title)
        links += [link['title'] for link in [r['links'] for r in resp['query']['pages'].values()][0]]

    return text, links

def save_text(title, text, lang):
    with open('wiki_texts/' + lang + '/' + title.replace('/', '') + '.txt', 'w') as file:
        file.write(text)

def check_continue(title, n):
    global done, broken
    return title not in done and len(done) < n and title not in broken

def read_all_links(title, n, lang):
    if not check_continue(title, n):
        return
    text, links = get_article_data(title)
    if text == '' or text == None:
        broken.append(title)
        return
    save_text(title, text, lang)

    global done
    print(title)
    done.append(title)

    np.random.shuffle(links)

    for l in links:
        read_all_links(l, n, lang)

def get_done_from_folder():
    return [file[:-4] for file in os.listdir('wiki_texts')]

if __name__ == '__main__':


    for lang in languages:
        baseurl = 'http://' + lang + '.wikipedia.org/w/api.php'
        my_atts = attributes()
        if not os.path.exists('wiki_texts/'+lang):
            os.makedirs('wiki_texts/'+lang)

        done = []
        broken = []

        read_all_links('Albert Einstein', n_articles, lang) #Stack Overflow


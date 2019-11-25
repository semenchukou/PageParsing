import urllib.request
from bs4 import BeautifulSoup
import bs4
import requests
import os, sys
import urllib.request
import re
import json

url = 'https://it.wikipedia.org/wiki/Categoria:Automobili_per_marca'
second_url = 'https://it.wikipedia.org/'
file_name = "characteristics.json"
characteristics = {}

def download_picture(url, file_path, file_name):
    full_path = file_path + file_name + '.jpg'
    urllib.request.urlretrieve(url, full_path)

def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()

def clean_word(word):
    return word.replace(':', ' ').replace('/', ' ').replace('"', ' ').replace('"', '').replace('*', '')

def get_and_add_characteristic(tr, characteristic, car_name, is_dimension_mm):
    if is_dimension_mm == True:
        mm = True
        millimm = 'mm'
        found_str = tr.find("td").getText().replace('\xa0', " ").strip()
        if millimm not in found_str:
            mm = False
        values = found_str.split(' ')
        for value in values:
            value = re.sub(r" ?\[[^)]+\]", "", value).replace(',' , '.')
            if value.replace('.' , '').isdigit():
                if mm is False:
                    characteristics[car_name].append({characteristic : float(value) * 1000})
                else:
                    characteristics[car_name].append({characteristic : value})
                mm = True
                break           
    else:
        found_str = tr.find("td").getText().replace('\xa0', " ").strip()
        values = found_str.split(' ')
        for value in values:
            value = re.sub(r" ?\[[^)]+\]", "", value).replace(',' , '.')
            if value.replace('.' , '').isdigit():
                characteristics[car_name].append({characteristic : value})
                break

def get_characteristics_from_table(table, car_name):
    characteristics[car_name] = []
    trs = table.findAll("tr")
    for tr in trs:
        ths = tr.findAll("th")
        for th in ths:
            if th.text.strip() == "Lunghezza":
                get_and_add_characteristic(tr, "Lunghezza", car_name, True)
            elif th.text.strip() == "Larghezza":
                get_and_add_characteristic(tr, "Larghezza", car_name, True)
            elif th.text.strip() == "Altezza":
                get_and_add_characteristic(tr, "Altezza", car_name, True)
            elif th.text.strip() == "Passo":
                get_and_add_characteristic(tr, "Passo", car_name, True)
            elif th.text.strip() == "Massa" or th.text.strip() == "Peso":
                get_and_add_characteristic(tr, "Massa", car_name, False)
    print(characteristics)


def parse(html):
    soup = BeautifulSoup(html)
    groups = soup.findAll("div", {"class": "mw-category-group"})
    for group in groups:
        first_group_name = group.find("h3").getText()
        ul = group.find("ul")
        for li in ul.findAll("li"):
            first_name = li.find("a").getText()
            ref = li.find(href = True)
            second_soup = BeautifulSoup(get_html(second_url + ref['href']))
            second_groups = second_soup.findAll("div", {"class": "mw-category-group"})
            for sec_group in second_groups:
                second_group_name = sec_group.find("h3").getText()
                sec_ul = sec_group.find("ul")
                for sec_li in sec_ul.findAll("li"):
                    second_name = sec_li.find("a").getText()
                    sec_ref = sec_li.find(href = True)
                    third_soup = BeautifulSoup(get_html(second_url + sec_ref['href']))
                    table = third_soup.find("table", {"class" : "sinottico"})
                    if(table != None):
                        '''img = table.find("a", {"class" : "image"}, href = True)
                        pic_ref = img.find('img')'''
                        path = "C:/Users/Alex/Desktop/iba/pics/" + clean_word(first_group_name) + '/' + clean_word(first_name) + '/' + clean_word(second_group_name) + '/' + clean_word(second_name) + '/'
                        print(path.encode('utf-8'))
                        '''if not os.path.exists(path.replace('//' , '/')):
                            os.makedirs(path)
                        download_picture('https:' + pic_ref['src'], path, clean_word(second_name))'''
                        get_characteristics_from_table(table, clean_word(second_name))
                        


def main():
    parse(get_html(url))
    with open(file_name, 'w') as outfile:
        json.dump(characteristics, outfile)
    
if __name__ == "__main__":
    main()

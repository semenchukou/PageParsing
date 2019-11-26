import urllib.request
from bs4 import BeautifulSoup
import bs4
import requests
import os, sys
import urllib.request
import re
import json
import pandas as pd

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

def get_characteristic(tr, characteristic, car_name, is_dimension_mm, destination):
    if is_dimension_mm == True:
        mm = True
        millimm = 'mm'
        found_str = tr.find("td").getText().replace('\xa0', " ").strip()
        if millimm not in found_str:
            mm = False
        values = found_str.split(' ')
        for i in range(len(values)):
            value = re.sub(r" ?\[[^)]+\]", "", values[i]).replace(',' , '.')
            if value.replace('.' , '').isdigit():
                if mm is False:
                    destination[characteristic] = float(value) * 1000
                else:
                    if(len(value) == 1):
                        next_val = re.sub(r" ?\[[^)]+\]", "", values[i + 1])
                        if next_val.isdigit():
                            value += next_val
                        else:
                            continue
                    else:
                        destination[characteristic] = float(value.replace('.', ''))
                mm = True
                break    
    else:
        kg = True
        kilogramm = 'kg'
        found_str = tr.find("td").getText().replace('\xa0', " ").strip()
        if kilogramm not in found_str:
            kg = False
        values = found_str.split(' ')
        for i in range(len(values)):
            value = re.sub(r" ?\[[^)]+\]", "", values[i]).replace(',' , '.')
            if value.replace('.' , '').isdigit():
                if kg is False:
                    destination[characteristic] = float(value) * 1000
                else:
                    if(len(value) == 1):
                        next_val = re.sub(r" ?\[[^)]+\]", "", values[i + 1])
                        if next_val.isdigit():
                            value += next_val
                        else:
                            continue
                    else:
                        destination[characteristic] = float(value.replace('.', ''))
                kg = True
                break

def get_characteristics_from_table(table, car_name, model):
    lung_added = False
    larg_added = False
    alt_added = False
    passo_added = False
    massa_added = False
    chars = {}
    trs = table.findAll("tr")
    for tr in trs:
        ths = tr.findAll("th")
        for th in ths:
            if th.text.strip() == "Lunghezza":
                get_characteristic(tr, "Length", car_name, True, chars)
                lung_added = True
            elif th.text.strip() == "Larghezza":
                get_characteristic(tr, "Width", car_name, True, chars)
                larg_added = True
            elif th.text.strip() == "Altezza":
                get_characteristic(tr, "Height", car_name, True, chars)
                alt_added = True
            elif th.text.strip() == "Passo":
                get_characteristic(tr, "Pace", car_name, True, chars)
                passo_added = True
            elif th.text.strip() == "Massa" or th.text.strip() == "Peso":
                get_characteristic(tr, "Weight", car_name, False, chars)
                massa_added = True
    chars['Model'] = model
    chars_amount = len(chars)
    if chars_amount == 6:
        characteristics[car_name] = chars
    else:
        if lung_added == False:
            chars['Length'] = 0
        if larg_added == False:
            chars['Width'] = 0
        if alt_added == False:
            chars['Height'] = 0
        if passo_added == False:
            chars['Pace'] = 0
        if massa_added == False:
            chars['Weight'] = 0
        characteristics[car_name] = chars


def parse(html):
    soup = BeautifulSoup(html)
    models_groups = soup.findAll("div", {"class": "mw-category-group"})
    for model in models_groups:
        model_group_name = model.find("h3").getText()
        ul = model.find("ul")
        for li in ul.findAll("li"):
            model_name = li.find("a").getText()
            ref = li.find(href = True)
            second_soup = BeautifulSoup(get_html(second_url + ref['href']))
            types_groups = second_soup.findAll("div", {"class": "mw-category-group"})
            for type_ in types_groups:
                type_group_name = type_.find("h3").getText()
                type_ul = type_.find("ul")
                for sec_li in type_ul.findAll("li"):
                    type_name = sec_li.find("a").getText()
                    sec_ref = sec_li.find(href = True)
                    third_soup = BeautifulSoup(get_html(second_url + sec_ref['href']))
                    table = third_soup.find("table", {"class" : "sinottico"})
                    if(table != None):
                        path = "C:/Users/Alex/Desktop/iba/pics/" + clean_word(model_group_name) + '/' + clean_word(model_name) + '/' + clean_word(type_group_name) + '/' + clean_word(type_name) + '/'
                        print(path.encode('utf-8'))
                        '''img = table.find("a", {"class" : "image"}, href = True)
                        pic_ref = img.find('img')
                        if not os.path.exists(path.replace('//' , '/')):
                            os.makedirs(path)
                        download_picture('https:' + pic_ref['src'], path, clean_word(type_name))'''
                        get_characteristics_from_table(table, clean_word(type_name), model_name)
                        


def main():
    '''parse(get_html(url))
    with open(file_name, 'w') as outfile:
        json.dump(characteristics, outfile)'''
    df = pd.read_json (r'characteristics.json')
    df = df.transpose()
    #print(df[((df.Length < 30) & (df.Length >0)) | ((df.Width < 30) & (df.Width >0)) | ((df.Height < 30) & (df.Height >0)) | ((df.Pace < 30) & (df.Pace  >0)) | ((df.Weight < 30) & (df.Weight >0))])
    
if __name__ == "__main__":
    main()
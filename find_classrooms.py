import requests
from bs4 import BeautifulSoup
import json
import re

URL = "https://www7.ceda.polimi.it/spazi/spazi/controller/OccupazioniGiornoEsatto.do"
BUILDING = 'innerEdificio'
ROOM = 'dove'
LECTURE = 'slot'


# Return a dict with all the info about the classrooms for the chosen day
def find_classrooms(location , day , month , year):
    info = {} 
    buildingName = '-' #defaul value for building
    info[buildingName] = {}

    params = {'csic': location , 'categoria' : 'tutte', 'tipologia' : 'tutte', 'giorno_day' : day , 'giorno_month' : month, 'giorno_year' : year , 'jaf_giorno_date_format' : 'dd%2FMM%2Fyyyy'  , 'evn_visualizza' : ''}
    r = requests.get(URL , params= params)
    
    soup = BeautifulSoup(r.text, 'html.parser')
    tableContainer = soup.find("div", {"id": "tableContainer"})
    tableRows = tableContainer.find_all('tr')[3:] #remove first three headers
    
    for row in tableRows:
        tds = row.find_all('td')
        if 'class' not in row.attrs:
            if BUILDING in tds[0].attrs['class']:
                buildingName = tds[0].string
                buildingName = re.search('(Edificio.*)' , buildingName).group(1) #take only the building name
                info[buildingName] = {}
        else:
            room = ''
            time = 7.75
            for td in tds:
                if ROOM in td.attrs['class']:
                    room = td.find('a').string
                    info[buildingName][room] = {}
                    info[buildingName][room]['lessons'] = []
                elif LECTURE in td.attrs['class'] and room != '':
                    duration = int(td.attrs['colspan'])
                    lesson_name = td.find('a').string
                    slot = {}
                    slot['from'] = time
                    time += duration/4
                    slot['to'] = time
                    lesson = {}
                    lesson[lesson_name] = slot                    
                    info[buildingName][room]['lessons'].append(lesson)
                else:
                    time += 0.25
    return info




if __name__ == "__main__":
    infos =  find_classrooms('MIA' , 1 , 6 , 2021)
    with open('infos_a.json' , 'w') as outfile:
        json.dump(infos , outfile)
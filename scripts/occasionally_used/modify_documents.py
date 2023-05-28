''' Modify documents in the database'''
import os
import sys
import logging
from logging import config
import re
from datetime import datetime

# Change the current working directory to 'scripts'
os.chdir('../')
# Add 'scripts' directory to the sys.path
sys.path.append('.')

# Import custom modules
import logging_functions as l
import mongodb_functions as mongodb

#Performs basic logging set up
#Get this script name
log_file_name = __file__.split('\\')
log_file_name = f'{log_file_name[-1][:-3]}_log.log'

l.get_log_file_name(log_file_name)

#Configure logging file
l.configure_logging()
logger = logging.getLogger('main')

# Connect to DB
client = mongodb.return_db_client()

# Check connection to DB
try:
    mongodb.command_ping(client)
except:
    l.log_exception('main', 'Unable to connect with database')

db = client['Web_Scraping_Job_Site']
collection_job_listings = db['Job_Listings']

def removing_jest(collection):
    ''' Remove Jest from the database'''


    result = collection.update_many({'$or': [
        {'technologies.expected': 'Jest'},
        {'technologies.optional': 'Jest'},
        {'technologies.found': 'Jest'}]},
        {'$pull': {'technologies.expected': 'Jest',
                'technologies.optional': 'Jest',
                'technologies.found': 'Jest'}})
    result = collection.update_many({'technologies.found': 'Jest'},{'$pull': {'technologies.found': 'Jest'}})

    print(result.modified_count, "documents updated.")

def removing_nas(collection):
    ''' Remove NAS from the database'''
    result = collection.update_many({'technologies.found': 'NAS'},{'$pull': {'technologies.found': 'NAS'}})
    print(result.modified_count, "documents updated.")

def get_all_regions(collection):
    ''' Returns all regions in the database'''
    regions = collection.distinct('region')
    print(regions)

def get_all_locations(collection):
    ''' Returns all locations in the database'''
    locations = collection.distinct('location')
    print(locations)

def modify_locations_test():
    ''' Modify locations in the database'''
    pattern = r'^(.*?)\s+\('
    city_names = []

    locations = ['Aleksandrów Łódzki', 'Andrychów', 'Balice (pow. krakowski)', 'Bażanowice (pow. cieszyński)', 'Bełchatów', 'Biała Podlaska', 'Białystok', 
            'Bielany Wrocławskie (pow. wrocławski)', 'Bielawa', 'Bielsko-Biała', 'Biskupice Podgórne (pow. wrocławski)', 'Biłgoraj', 'Bochnia', 'Bolesławiec', 
            'Bolszewo (pow. wejherowski)', 'Bożejowice (pow. bolesławiecki)', 'Brzeg Dolny', 'Buk', 'Bydgoszcz', 'Bytom', 'Bytów', 'Błonie', 'Chełm', 
            'Cholerzyn (pow. krakowski)', 'Chorkówka (pow. krośnieński)', 'Chorula (pow. krapkowicki)', 'Chorzów', 'Chrzanów', 'Ciechanów', 'Cieszyn', 
            'Czaple (pow. kartuski)', 'Czechowice-Dziedzice', 'Czeladź', 'Czernin (pow. sztumski)', 'Czerwieńsk', 'Częstochowa', 'Dobczyce', 
            'Domasław (pow. wrocławski)', 'Duchnice (pow. warszawski zachodni)', 'Dzierżoniów', 'Dąbrowa (pow. poznański)', 'Dąbrowa Górnicza', 
            'Dębica', 'Dęblin', 'Dębowica (pow. łukowski)', 'Elbląg', 'Ełk', 'Frydrychowo (pow. golubsko-dobrzyński)', 'Galew (pow. turecki)', 
            'Gdańsk', 'Gdynia', 'Gliwice', 'Gniezno', 'Godzikowice (pow. oławski)', 'Gorzów Wielkopolski', 'Grabki Duże (pow. staszowski)', 
            'Grodzisk Mazowiecki', 'Grudziądz', 'Grójec', 'Głogów', 'Głogów Małopolski', 'Głuchowo (pow. poznański)', 'Głuchołazy', 'Hrubieszów', 
            'Inowrocław', 'Jankowice (pow. poznański)', 'Jankowo Gdańskie (pow. gdański)', 'Jarocin (pow. jarociński)', 'Jarosław', 'Jasionka (pow. rzeszowski)', 
            'Jastrzębie-Zdrój', 'Jasło', 'Jaworzno', 'Jelcz-Laskowice', 'Jelenia Góra', 'Jędrzejów', 'Kalisz', 'Kanie (pow. pruszkowski)', 
            'Karpicko (pow. wolsztyński)', 'Katowice', 'Kielce', 'Kobierzyce (pow. wrocławski)', 'Kobylarnia (pow. bydgoski)', 'Kolbuszowa', 
            'Komorniki (gm. Komorniki)', 'Komorów (pow. pruszkowski)', 'Koniecpol', 'Konin', 'Kornice (pow. raciborski)', 'Koszalin', 
            'Kowale (pow. gdański)', 'Kozienice', 'Kraków', 'Krasnystaw', 'Kraśnik', 'Krosno', 'Krotoszyn', 'Krzeszowice', 'Krępice (pow. średzki)', 
            'Ksawerów (pow. pabianicki)', 'Kuranów (pow. żyrardowski)', 'Kwidzyn', 'Kędzierzyn-Koźle', 'Kęty', 'Legionowo', 'Legnica', 'Leszno', 
            'Leżajsk', 'Lubartów', 'Lublin', 'Luboń', 'Magnice (pow. wrocławski)', 'Malbork', 'Marki', 'Małkowo (pow. kartuski)', 'Mielec', 
            'Mieścisko (pow. wągrowiecki)', 'Mirków (pow. wrocławski)', 'Międzyrzecz', 'Mińsk Mazowiecki', 'Morawica (pow. krakowski)', 'Morąg', 
            'Mszczonów', 'Musuły (pow. grodziski)', 'Mysłowice', 'Myślenice', 'Niepołomice', 'Niepruszewo (pow. poznański)', 'Nowa Ruda', 
            'Nowy Dwór Mazowiecki', 'Nowy Sącz', 'Nowy Tomyśl', 'Nysa', 'Olewin (pow. olkuski)', 'Olkusz', 'Olsztyn', 'Opoczno', 'Opole', 
            'Ostaszewo (pow. toruński)', 'Ostrołęka', 'Ostrów Wielkopolski', 'Osła (pow. bolesławiecki)', 'Otwock', 'Oława', 'Ołtarzew (pow. warszawski zachodni)', 
            'Oświęcim', 'Ożarów Mazowiecki', 'Pabianice', 'Paczkowo (pow. poznański)', 'Pass (pow. warszawski zachodni gm. Błonie)', 'Paterek (pow. nakielski)', 
            'Piaseczno', 'Piekary Śląskie', 'Piekoszów (pow. kielecki)', 'Pieńków (pow. nowodworski)', 'Piotrków Trybunalski', 'Piła', 'Pleszew', 'Plewiska (pow. poznański)',
            'Podgrodzie (pow. dębicki)', 'Pogórska Wola (pow. tarnowski)', 'Polanka (pow. myślenicki)', 'Police', 'Polkowice', 'Porosły-Kolonia (pow. białostocki)',
            'Poznań', 'Połaniec', 'Prandocin-Iły (pow. krakowski)', 'Pruszcz Gdański', 'Pruszków', 'Przemyśl', 'Przęsocin (pow. policki)', 'Pszczyna', 'Puławy', 
            'Pęcice (pow. pruszkowski)', 'Płock', 'Płońsk', 'Racibórz', 'Radom', 'Radomsko', 'Radonice (pow. warszawski zachodni)', 'Radzionków', 'Rawa Mazowiecka', 
            'Rawicz', 'Robakowo (pow. poznański)', 'Rojów (pow. ostrzeszowski)', 'Ropczyce', 'Ruda Śląska', 'Rybie (pow. pruszkowski)', 'Rybnik', 'Rzeszów', 'Rzgów', 
            'Sanok', 'Siedlce', 'Sieradz', 'Skawina', 'Skierniewice', 'Sochaczew', 'Sokołów (pow. pruszkowski)', 'Solec Kujawski', 'Sopot', 'Sosnowiec', 'Stalowa Wola', 
            'Stara Iwiczna (pow. piaseczyński)', 'Starachowice', 'Stargard', 'Starogard Gdański', 'Stryków', 'Strzelce Opolskie', 'Suchy Las (pow. poznański)', 'Sulechów', 
            'Sulejówek', 'Suwałki', 'Swadzim (pow. poznański)', 'Swarzędz', 'Szczecin', 'Szczekociny', 'Szprotawa', 'Sępólno Krajeńskie', 'Słubice', 'Słupsk', 
            'Tajęcina (pow. rzeszowski)', 'Tarnobrzeg', 'Tarnowo Podgórne (pow. poznański)', 'Tarnowskie Góry', 'Tarnów', 'Tczew', 'Teolin (pow. łódzki wschodni)', 
            'Tomaszów Mazowiecki', 'Toruń', 'Trzebnica', 'Tuchów', 'Tychy', 'Warszawa', 'Wałbrzych', 'Wejherowo', 'Wieliczka', 'Wielogłowy (pow. nowosądecki)', 
            'Wiskitki (pow. żyrardowski)', 'Wiązowna (pow. otwocki)', 'Wolbórz', 'Wolsztyn', 'Wołomin', 'Wrocław', 'Wronki', 'Września', 'Wsola (pow. radomski)', 'Wyszków', 
            'Włocławek', 'Włoszczowa', 'Zabierzów (pow. krakowski)', 'Zabrze', 'Zabłudów', 'Zaczernie (pow. rzeszowski)', 'Zakroczym', 'Zakrzewo (pow. poznański)', 'Zambrów', 
            'Zamienie (pow. piaseczyński gm. Lesznowola)', 'Zamość', 'Zawiercie', 'Zbąszynek', 'Zduńska Wola', 'Zgierz', 'Zielona Góra', 'Zielonka', 'Zimna Wódka (pow. strzelecki)', 
            'Ząbki', 'Złotniki (pow. poznański)', 'Złotów', 'Łagiewniki (pow. dzierżoniowski)', 'Łaziska Górne', 'Łańcut', 'Łomna-Las (pow. nowodworski)', 'Łomża', 
            'Łozienica (pow. goleniowski)', 'Łyski (pow. białostocki)', 'Łódź', 'Łódź (pow. poznański)', 'Łęczna', 'Środa Śląska', 'Świebodzin', 
            'Świerklany (pow. rybnicki)', 'Świerże Górne (pow. kozienicki)', 'Świnoujście', 'Żołędowo (pow. bydgoski)', 'Żuławki (pow. nowodworski)', 'Żyrardów', 'Żywiec']

    for location in locations:
        match = re.search(pattern, location)
        if match:
            city_name = match.group(1)
            city_names.append(city_name)
        else:
            city_names.append(location)

    for old, new in zip(city_names, locations):
        print("{:20} {}".format(old, new))
        print()

def modify_location(collection):
    '''Modify the location field by removing the county or shire name inside the parentheses'''
    # Define the regular expression pattern
    pattern = r'^(.*?)\s+\('

    # Update the documents in the collection
    result = collection.update_many({'location': {'$regex': pattern}},
                            {'$set': {'location': {'$regexReplace': {'input': '$location',
                                                                    'find': pattern,
                                                                    'replacement': '$1'}}}})
    print(result.modified_count, 'documents updated')

def remove_invalid_locations(collection):
    '''Remove the documents that have invalid location'''
    # During querries, some variables were replaced with querry itself. Change them to None
    result = collection.update_many({'location': {'$type': 'object'}},
                          {'$unset': {'location': ''}})

    query = {"location": {"$type": "object"}}
    result = collection.find(query)
    print('objects removed')
    # Print the documents
    for document in result:
        print(document['location'])

def clean_region(region_name):
    ''' Keap only proper voivodeships names'''
    voivodeships_pl = ['dolnośląskie', 'kujawsko-pomorskie', 'lubelskie', 'lubuskie', 
                    'łódzkie', 'małopolskie', 'mazowieckie', 'opolskie', 'podkarpackie', 
                    'podlaskie', 'pomorskie', 'śląskie', 'świętokrzyskie', 'warmińsko-mazurskie', 
                    'wielkopolskie', 'zachodniopomorskie']
    voivodeships_en_1 = ['lower silesia', 'kuyavian-pomerania', 'lublin', 'lubusz', 'łódź', 
                       'lesser poland', 'masovia', 'opole', 'subcarpathia', 
                       'podlaskie', 'pomerania', 'silesia', 'holy cross', 'warmian-masuria',
                       'greater poland', 'west pomerania']
    voivodeships_en_2 = ['lower silesian', 'kuyavian-pomeranian', 'lublin', 'lubusz', 'łódź', 
                       'lesser poland', 'masovian', 'opole', 'subcarpathian', 
                       'podlaskie', 'pomeranian', 'silesian', 'holy cross', 'warmian-masurian',
                       'greater poland', 'west pomeranian']
    if region_name is None or region_name == '' or region_name == ' ':
        return None
    
    temp_name = region_name.lower()
    # If name is in polish, return it in lower case
    if temp_name in voivodeships_pl:
        return temp_name
    # If name is in english, return polish name
    if temp_name in voivodeships_en_1:
        return voivodeships_pl[voivodeships_en_1.index(temp_name)]
    if temp_name in voivodeships_en_2:
        return voivodeships_pl[voivodeships_en_2.index(temp_name)]
    if temp_name in ['warmia-mazuria', 'warmia-mazurian']:
        return 'warmińsko-mazurskie'
    if temp_name in ['kuyavia-pomerania', 'kuyavia-pomeranian']:
        return 'kujawsko-pomorskie'
    # If abroad, return None
    if region_name in ['abroad', 'zagranica']:
        return None
    return region_name

def replace_regions(collection):
    '''Replace the region field with proper voivodeship name'''
    for doc in collection.find({'region': {'$ne': ''}}):
        # call the clean_region function
        new_region = clean_region(doc['region'])
        collection.update_one({'_id': doc['_id']}, {'$set': {'region': new_region}})
        print('regions replaced')

def correct_last_region(collection):
    '''Correct the last region name'''
    filter = {"region": "Kuyavia-Pomerania"}
    update = {"$set": {"region": "kujawsko-pomorskie"}}

    result = collection.update_many(filter, update)
    print(result.modified_count, "documents updated.")

def clean_contract_type(contract_type):
    '''Clean the contract_type field'''
    contract_pl = ['umowa o pracę', 'umowa zlecenie', 'umowa o dzieło', 
                   'umowa na zastępstwo', 'umowa o pracę tymczasową', 'kontrakt B2B', 
                   'umowa o staż praktyki', 'umowa agencyjna']
    contract_en = ['contract of employment', 'contract of mandate', 'contract for specific work', 
                   'replacement contract', 'temporary employment contract', 'B2B contract', 
                   'internship apprenticeship contract', 'agency agreement']
    if contract_type is None or contract_type == '' or contract_type == ' ':
        return None
    if contract_type in contract_pl:
        return contract_type
    if contract_type in contract_en:
        return contract_pl[contract_en.index(contract_type)]
    return contract_type

def replace_contract_type(collection):
    '''Replace the contract_type field with polish name'''
    for doc in collection.find({'contract_type': {'$ne': ''}}):
        # call the clean_region function
        new_contract_type = clean_contract_type(doc['contract_type'])
        collection.update_one({'_id': doc['_id']}, {'$set': {'contract_type': new_contract_type}})

def find_duplicates(collection):
    '''Get the duplicate documents'''
    pipeline = [{"$group": {"_id": "$url", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}},
                {"$project": {"_id": 0, "url": "$_id", "count": 1}}]

    # get the duplicates
    duplicates = list(collection.aggregate(pipeline))
    print(len(duplicates))
    # get the number of duplicates
    return duplicates

def add_pub_month_field(collection):
    '''Add publication month field'''

    # assuming your collection is named "my_collection"
    docs = collection.find({})

    for doc in docs:
        pub_str = str(doc["publication_date"])
        pub_dt = datetime.fromisoformat(pub_str)
        # Use 1 day of the month as default
        month_year = datetime(pub_dt.year, pub_dt.month, 1).isoformat()
        collection.update_one({'_id': doc['_id']}, {'$set': {'publication_month': month_year}})
    print('publication month added')

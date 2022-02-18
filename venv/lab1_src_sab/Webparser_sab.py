#coding:utf-8
"""
Information Extraction from Webpages as Semi-Structured Data or Unstructured Data
Method : Webpages as Unstructured Data with Parsing
Author: Sabareeswaran Shanmugam
•	Scripting language – python 3.7
•	Database – MySQL Workbench 8.0
•	IDE - PyCharm 2021.3.1 (Professional Edition)
    Runtime version: 11.0.13+7-b1751.21 x86_64
    VM: OpenJDK 64-Bit Server VM by JetBrains s.r.o.
    macOS 12.1
    GC: G1 Young Generation, G1 Old Generation
    Memory: 2048M
    Cores: 16
    Non-Bundled Plugins:
    DBN (3.3.1249.0)
"""

import requests
import csv
from bs4 import BeautifulSoup
import os
import mysql.connector
from pathlib import Path

#Create output files in Working Directory.
SAB_PROJECT_ROOT = Path(__file__).parents[1]
#declaring website url need to be parsed orscrap some data
URL = "https://www.infoplease.com/homework-help/history/collected-state-union-addresses-us-presidents"

# get content using beautifulsoup from url
req = requests.get(URL)
soup = BeautifulSoup(req.content, 'html5lib')
print("Web Scraping using Beautifulsoup - html parser")
# prettify will show the html tag with linewrap
print(soup.prettify())
table = soup.find('div', attrs = {'class':'toc'})
count = 1

# Scraping  all data from html span tag
for presidentDetails in table.findAll('span', attrs={'class': 'article'}):
    # define all variables and list
    President_List = []
    P_Name = " "
    P_Date = " "
    # fetch president Name, Date and URL to store in csv file
    President_Name = presidentDetails.a.text.split("(", 1)[0].replace('.', '').lower()
    P_Name = President_Name.replace('-', '')
    President_Date = presidentDetails.a.text.split("(", 1)[1][:-1].replace(',', '').lower()
    P_Date = President_Date.replace('-', '')
    s = "-"
    President_Linktoaddress = presidentDetails.a['href']


    # condition for special characters in president_address_url
    # Some of the site links are redirected to some Advertisement pages
    if President_Linktoaddress[:3] == '/t/' or President_Linktoaddress[:3] == '':
        President_Linktoaddress = "/primary-sources/government/presidential-speeches/state-union-address-" + s.join(P_Name) \
                                  + s.join(P_Date)
    else:
        President_Linktoaddress = presidentDetails.a['href']
    Base_URL = "https://www.infoplease.com"
    President_Linktoaddress = Base_URL + President_Linktoaddress

    # Append all data into President Array List
    President_List.append(P_Name)
    President_List.append(P_Date)
    President_List.append(President_Linktoaddress)

    # fetch all the content from paragraph tag to store in txt file in the local Path
    try:
        Pr = requests.get(President_Linktoaddress)
        P_Soup = BeautifulSoup(Pr.content, 'html.parser')
        Paragraph_Content = P_Soup.find('div', attrs={'class': 'article'}).findAll('p')
    except:
        pass
    individual_path = SAB_PROJECT_ROOT /'output'/'TextOfAddress_Individual_Sab'
    Filename_Address_Local = str(individual_path)+ "/" + str(count) + ".txt"
    AddressFile = open(Filename_Address_Local, "w")
    count = count + 1
    TextofAddress = ""

# combine all data in single txt file (Extra Credits)
    AllDatainFile = SAB_PROJECT_ROOT /'output'/ 'TextOfAddress_Entire_sab.txt'

    for context in Paragraph_Content:
        PresidentDetails = ''.join(context.findAll(text=True))
        # Write all content in each Address file
        AddressFile.write(PresidentDetails)
        # Write all content in single Address file
        DataFile = open(AllDatainFile, "a")
        # Append each paragraph content to textofaddress
        TextofAddress = TextofAddress +PresidentDetails
        DataFile.write(TextofAddress)

    President_List.append(Filename_Address_Local)
    President_List.append(TextofAddress)

   # Print entire President Array List
    print("Extracted Data")
    print(President_List)
    AddressFile.close()
    DataFile.close()

# Load all data into CSV file
    csv_path=SAB_PROJECT_ROOT /'output'/'President_CSV_Extracted.csv'
    txt_path=SAB_PROJECT_ROOT /'output'/'Extracredit.txt'
    with open(csv_path, 'a') as out_file:
        writer = csv.writer(out_file)
        writer.writerow((President_Name, President_Date, President_Linktoaddress, Filename_Address_Local,
                         TextofAddress))

# Load all data into text file for future processing ( Extra Credit)
    with open(txt_path, 'a') as f:
        f.write(str(President_Name)+str(President_Date)+str(TextofAddress))

#Database connection
    mydb = mysql.connector.connect(host='localhost',
                                   user='root',
                                   password='qwerty60',
                                   port='3306',
                                   database='infoplease_us_president',
                                   auth_plugin='mysql_native_password')
    print("Successfully connected to database: ")
    mycursor = mydb.cursor()
    try:
        table_create = 'CREATE TABLE `president` (`Name_of_presidents` varchar(60) DEFAULT NULL,' \
                       '`Date_of_union_address` longtext,' \
                       '`Link_to_address` longtext,`Filename_Address_Local` longtext,' \
                       '`Text_of_address` longtext)'
        mycursor.execute(table_create)
    except:
        pass
    finally:
        sql = 'INSERT INTO president (Name_of_presidents,Date_of_union_address,Link_to_address,Filename_Address_Local,Text_of_address) ' \
              'VALUES (%s,%s,%s,%s,%s)'
        mycursor.execute(sql, President_List)
    mydb.commit()
    print("Successfully Table Created and Data Inserted")



"""
Reference

1. https://www.geeksforgeeks.org/implementing-web-scraping-python-beautiful-soup/
2. https://realpython.com/beautiful-soup-web-scraper-python/

Database Connection
1. https://stackoverflow.com/questions/372885/how-do-i-connect-to-a-mysql-database-in-python
2.Downloaded software
	Mysql Community server 8.0.28  https://dev.mysql.com/downloads/mysql/
	Mysql workbench 8.0.28   https://dev.mysql.com/downloads/workbench/
3.Connect MySql server to IDE : Pycharm
https://developpaper.com/how-does-pycharm-connect-to-and-configure-the-mysql-database/

"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import mysql.connector
import os

connection = mysql.connector.connect(
    host="localhost",
    user="homecms",
    password="homecms",
    database="homecms"
)

def processWeblinks(cursor):

  print ("\n\nProcessing weblinks records : \n \n")

  query = "SELECT weblink FROM weblinks WHERE ((updated_on <= CURDATE() - INTERVAL 1 WEEK) or (updated_on is null))"
  cursor.execute(query)

  weblinks = cursor.fetchall()

  for weblink in weblinks:
    
    print("  > Processing web link : " + weblink[0])

    sql = "UPDATE weblinks SET updated_on = CURRENT_DATE() WHERE weblink = '" + weblink[0] + "'"
    cursor.execute(sql)
    connection.commit()

    parsed_url = urlparse(weblink[0])
    hostname = parsed_url.hostname
    response = requests.get(weblink[0])

    if response.status_code == 200:

        soup = BeautifulSoup(response.content, 'html.parser')
        sublinks = soup.find_all('a')

        for sublink in sublinks:

          subLinkUrl = sublink.get('href')

          if subLinkUrl is not None:

            cursor = connection.cursor()

            sql = "SELECT COUNT(*) FROM stage_weblinks WHERE weblink = '" + subLinkUrl + "'"
            cursor.execute(sql)
            row_count = cursor.fetchone()[0]

            if (row_count == 0):

              if subLinkUrl[0] == '/':
                  subLinkUrl = 'http://' + hostname + subLinkUrl
              print(subLinkUrl)
              print('  > New url : ' + subLinkUrl)
              cursor = connection.cursor()

              if subLinkUrl[0:4] == 'http':
              
                sql = "INSERT INTO stage_weblinks (weblink, source_type) VALUES ('" + subLinkUrl + "', 12)"
                cursor.execute(sql)

              connection.commit()

    else:
      print('  > Failed to fetch the webpage')

def processStageWeblinks(cursor):
  
  print ("\n\n  >Processing weblinks stage records : \n \n")

  query = "SELECT weblink FROM stage_weblinks LIMIT 0, 1"
  cursor.execute(query)

  weblinks = cursor.fetchall()

  for weblink in weblinks:
    
    print("Processing web link : " + weblink[0])
    choice = input("\n(a) Save current link: \n" +
                   "(b) Save current website: \n" +
                   "(c) Remove current weblink: \n" +
                   "(d) Remove all website links : \n \n"+
                   "Option >> ")
    
    print("\nYou entered: " + choice + "\n")

    if choice == "a":

      sql = "INSERT INTO weblinks (title, weblink, created_by) " + \
            " VALUES ('" + weblink[0] + "', '" + weblink[0] + "', 'batch')"
      
      print ("Inserted new weblink : " + weblink[0])

    elif choice == "b":

      parsed_url = urlparse(weblink[0])
      hostname = parsed_url.hostname

      print ("Inserting website http://" + hostname)

      sql = "INSERT INTO weblinks (title, weblink, created_by) " + \
            " VALUES ('http://" + hostname + "', 'http://" + hostname + "', 'batch')"
      print (sql)

    elif choice == "c":

      print ("Deleting weblink" + weblink[0])

      sql = "DELETE FROM stage_weblinks WHERE weblink = '" + weblink[0] + "'"
      print (sql)

    elif choice == "d":

      print ("Deleting all weblinks for " + hostname)

      sql = "DELETE FROM stage_weblinks WHERE weblink LIKE '%" + hostname + "%'"
      print (sql)

    cursor.execute(sql)
    connection.commit()

    if ((choice == "a") or 
        (choice == "c")):

      sql = "DELETE FROM stage_weblinks WHERE weblink = '" + weblink[0] + "'"

    cursor.execute(sql)
    connection.commit()

    sql = "SELECT COUNT(*) FROM stage_weblinks"
    cursor.execute(sql)
    row_count = cursor.fetchone()[0]

    print ("\n\nNumber of weblinks stage records before processing : " + str(f"{old_row_count:,}"))
    print ("\nNumber of weblinks stage records remaining : " + str(f"{row_count:,}\n"))

cursor = connection.cursor()

os.system('cls')

sql = "SELECT COUNT(*) FROM stage_weblinks"
cursor.execute(sql)
old_row_count = cursor.fetchone()[0]

processWeblinks(cursor)
processStageWeblinks(cursor)

cursor.close()
connection.close()
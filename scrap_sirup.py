import time
import pandas as pd
import requests
import re,json
import mysql.connector


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#------------------------------------------------------
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="app_lpse"
)

# Set up the web driver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
driver.get("https://sirup.inaproc.id/sirup/caripaketctr/index")
time.sleep(3)

#------------------------------------------------------
# Jika ada Pop Up -------------------------------------
#------------------------------------------------------
try:
    close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='fullImageModal']//*[@aria-label='Close']"))
    )
    close_button.click()
    print("Pop-up berhasil ditutup!")
    
except Exception as e:
    print("Gagal klik biasa, mencoba klik paksa via JavaScript...")
    # Solusi cadangan: Jika tombol terhalang backdrop modal, klik menggunakan JavaScript
    close_button = driver.find_element(By.XPATH, "//*[@id='fullImageModal']//*[@aria-label='Close']")
    driver.execute_script("arguments[0].click();", close_button)


#------------------------------------------------------
# Jika ada Pop Up -------------------------------------
#------------------------------------------------------


#------------------------------------------------------
all_rows = [] 
sch =  driver.find_element("xpath",'//*[@id="searchbox"]')
driver.implicitly_wait(3)
sch.send_keys("akuntan")
select_element =  driver.find_element("xpath",'//*[@id="searchResult_length"]/label/select/option[4]')
driver.implicitly_wait(3)
select_element.click()
time.sleep(5)

x=1
while x<24:
	html = driver.page_source
	soup = BeautifulSoup(html, 'html.parser')	
	tables = soup.find_all('table')
	table1 = tables[0]
	body = table1.find_all("tr")
	head = body[0] 
	body_rows = body[1:]

	for row_num in range(len(body_rows)):       
	    row = []                                
	    for row_item in body_rows[row_num].find_all("td"):       
	        aa = re.sub("(\xa0)|(\n)|,","",row_item.text)
	        row.append(aa)
	    all_rows.append(row)

	    #---------------------------------------
	    no 			= row[0]
	    paket		= row[1]
	    pagu 		= int(row[2])
	    jenis		= row[3]
	    produk		= row[4]
	    usaha		= row[5]
	    metode		= row[6]
	    pemilihan	= row[7]
	    klpd		= row[8]
	    satker		= row[9]
	    lokasi		= row[10]
	    id_sirup	= row[11]

	    if pagu > 10000000 and jenis!='Barang':
	    	mycursor = mydb.cursor()
	    	sql = "INSERT INTO data_sirup (id,no,paket,pagu,jenis,produk,usaha,metode,pemilihan,klpd,satker,lokasi,id_sirup) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s)"
	    	val = ("",no,paket,pagu,jenis,produk,usaha,metode,pemilihan,klpd,satker,lokasi,id_sirup)
	    	mycursor.execute(sql, val)
	    	mydb.commit()
	    #----------------------------------------


	    
	time.sleep(2)
	driver.execute_script("window.scrollTo(0, window.scrollY + 200)")
	tbl_next = driver.find_element("xpath",'//*[@id="searchResult_next"]/a')
	driver.implicitly_wait(5)
	tbl_next.click()
	time.sleep(2)

	print(x," : ",x*100)
	x+=1

#------------------------------------------------------
with open(f'data/data.json', 'w') as f:
   json.dump(all_rows, f, indent=4)

print("------------------------")
print("Save to File Json. ")

#print(df)
#------------------------------------------------------
driver.quit()

#//*[@id="searchbox"]




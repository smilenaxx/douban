import requests
from bs4 import BeautifulSoup as BS
import re
import pymysql

def get_htmlsoup(url):
	r_sess = requests.session()
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.1708.400 QQBrowser/9.5.9635.400'}
	r = r_sess.get(url,headers = headers,timeout = 60)
	soup = BS(r.text,"html.parser")
	
	return soup

def get_content(soup):
	#act_re = re.compile(r'导演[^主]+(?:主|\.)')
	each_item_list = soup.find_all('tr','item')
	each_content_list = []
	for each in each_item_list:
		each_soup = BS(str(each),'html.parser')
		
		each_title = BS(str(each_soup.find_all('div','pl2')),'html.parser').get_text().replace('\n','')[1:-1].strip()
		if each_title.find(' ') != -1:
			each_title = each_title[:each_title.find(' ')]
		each_author = BS(str(each_soup.find_all('p','pl')[0]),'html.parser').get_text().replace(' ','').split('/')[0]
		each_press = BS(str(each_soup.find_all('p','pl')[0]),'html.parser').get_text().replace(' ','').split('/')[-3]
		each_price = BS(str(each_soup.find_all('p','pl')[0]),'html.parser').get_text().replace(' ','').split('/')[-1]
		if each_price[-1] == '元':
			each_price = each_price[:-1]
		each_star = '豆瓣评分:' + BS(str(each_soup.find_all('span','rating_nums')[0]),'html.parser').get_text()
		each_people = '评级人数:' + str(each_soup.find_all('span','pl')[0])[39:-27]
		each_sentence = each_soup.find_all('span','inq')
		if each_sentence:
			each_sentence = str(each_sentence[0])[18:-7]
		else:
			each_sentence = '无'
		
		each_content_list.append([each_title,each_author,each_press,each_price,each_star,each_people,each_sentence])

	return each_content_list

def insert_mysql(book_list):
	book_content_list = book_list
	#连接数据库
	db = pymysql.connect("localhost","root","940530","book",charset='utf8')
	# 使用 cursor() 方法创建一个游标对象 cursor
	cursor = db.cursor()
	
	cursor.execute("DROP TABLE IF EXISTS douban_book250")
	#创建表
	sql = """CREATE TABLE douban_book250(
		 TOP_ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
         BOOK_NAME  CHAR(50),
         AUTHOR_NAME CHAR(50),
         PRESS_NAME CHAR(50),
         PRICE  CHAR(20),
         DOUBAN CHAR(20),  
         PEOPLE CHAR(20), 
         SENTENCE CHAR(200) )"""
	
	cursor.execute(sql)
	
	for each_book in book_content_list:

		sql = "INSERT INTO douban_book250(BOOK_NAME,AUTHOR_NAME,PRESS_NAME,PRICE,DOUBAN,PEOPLE,SENTENCE) VALUES (%s,%s,%s,%s,%s,%s,%s)"
		#try:
			# 执行sql语句
		cursor.execute(sql,(each_book[0],each_book[1],each_book[2],each_book[3],each_book[4],each_book[5],each_book[6]))
		# 提交到数据库执行
		db.commit()
		'''except:
			# 如果发生错误则回滚
			db.rollback()'''

	# 关闭数据库连接
	db.close()
	print('存入数据库成功')
	return 

def main():
	all_book_list = []
	for i in range(0,10):
		url = 'https://book.douban.com/top250?start=%s'%(i*25)
		each_soup = get_htmlsoup(url)
		each_25_list = get_content(each_soup)
		for each in each_25_list:
			all_book_list.append(each)

	insert_mysql(all_book_list)

if __name__ == '__main__':	  
	main()
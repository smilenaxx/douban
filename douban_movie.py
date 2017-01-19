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
	act_re = re.compile(r'导演[^主]+(?:主|\.)')
	each_item_list = soup.find_all('div','info')
	each_content_list = []
	for each in each_item_list:
		each_soup = BS(str(each),'html.parser')
		each_title = str(each_soup.find_all('span','title')[0])[20:-7]
		each_act = act_re.findall(BS(str(each_soup.find_all('p')[0]),'html.parser').get_text())[0]
		each_act = each_act[4:each_act.find('\xa0')]
		each_tip = BS(str(each_soup.find_all('p')[0]),'html.parser').br.get_text().strip().replace('\xa0','')
		each_star = '豆瓣评分:' + BS(str(each_soup.find_all('span','rating_num')[0]),'html.parser').get_text()
		each_people = '评价人数:' + str(BS(str(each_soup.find_all('div','star')[0]),'html.parser').find_all('span')[3])[6:-10]
		each_sentence = each_soup.find_all('span','inq')
		if each_sentence:
			each_sentence = str(each_sentence[0])[18:-7]
		else:
			each_sentence = '无'

		each_content_list.append([each_title,each_act,each_tip,each_star,each_people,each_sentence])

	return each_content_list

def insert_mysql(movie_list):
	movie_content_list = movie_list
	#连接数据库
	db = pymysql.connect("localhost","root","940530","movie250",charset='utf8')
	# 使用 cursor() 方法创建一个游标对象 cursor
	cursor = db.cursor()
	
	'''cursor.execute("DROP TABLE IF EXISTS movie_table")
	#创建表
	sql = """CREATE TABLE movie_table(
		 TOP_ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
         MOVIE_NAME  CHAR(20) NOT NULL,
         ACT_NAME CHAR(50),
         TIP  CHAR(200),
         DOUBAN CHAR(20),  
         PEOPLE CHAR(20), 
         SENTENCE CHAR(200) )"""
	
	cursor.execute(sql)'''
	
	for each_movie in movie_content_list:

		sql = "INSERT INTO movie_table(MOVIE_NAME,ACT_NAME,TIP,DOUBAN,PEOPLE,SENTENCE) VALUES (%s,%s,%s,%s,%s,%s)"
		#try:
			# 执行sql语句
		cursor.execute(sql,(each_movie[0],each_movie[1],each_movie[2],each_movie[3],each_movie[4],each_movie[5]))
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
	all_movie_list = []
	for i in range(0,10):
		url = 'https://movie.douban.com/top250?start=%s&filter='%(i*25)
		each_soup = get_htmlsoup(url)
		each_10_list = get_content(each_soup)
		for each in each_10_list:
			all_movie_list.append(each)

	insert_mysql(all_movie_list)

if __name__ == '__main__':	  
	main()
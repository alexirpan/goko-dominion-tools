import requests
from bs4 import BeautifulSoup

r = requests.get("http://gokosalvager.com/logsearch?p1name=Titandrake&p1score=any&p2name=&startdate=08%2F05%2F2012&enddate=01%2F06%2F2015&supply=&nonsupply=&rating=pro%2B&pcount=2&colony=any&bot=false&shelters=any&guest=false&minturns=&maxturns=&quit=false&resign=any&limit=1000&submitted=true&offset=0")

soup = BeautifulSoup(r.text)

i = 1
for link in soup.find_all('a'):
    href = link.get('href')
    if 'static' not in href and href[-3:] == 'txt':
        print href
        f = open("log%d.txt" % i, "w")
        f.write(requests.get(href).text)
        f.close()
        print 'Downloaded log %d' % i
        i += 1

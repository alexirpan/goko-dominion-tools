import requests
from bs4 import BeautifulSoup
import string
r = requests.get("http://gokosalvager.com/logsearch?p1name=Titandrake&p1score=any&p2name=&startdate=08%2F05%2F2012&enddate=01%2F21%2F2014&supply=&nonsupply=&rating=pro%2B&pcount=2&colony=any&bot=false&shelters=any&guest=false&minturns=&maxturns=&quit=false&resign=any&limit=1000&submitted=true&offset=0")

soup = BeautifulSoup(r.text)

i = 264
for link in soup.find_all('a'):
    href = link.get('href')
    if href[:4] == 'http' and 'static' not in href and href[-3:] == 'txt':
        print href
        f = open("log%d.txt" % i, "w")
        r = requests.get(href)
        # unicode too hard
        f.write(filter(lambda x : x in string.printable, r.text))
        f.close()
        print 'Downloaded log %d' % i
        i += 1

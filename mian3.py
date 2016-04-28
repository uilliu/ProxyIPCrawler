# -*- coding:utf8 -*-
import urllib2
from urllib2 import URLError
from BeautifulSoup import BeautifulSoup

import requests
from requests.packages.urllib3.util import timeout
from requests.exceptions import ConnectionError

import time
import threading
from threading import Thread
import re

def ProxyIPSpider(self):
    # get the proxy
    f = open('proxy.txt', 'w')
    for page in range(1,50):
        url = 'http://www.xicidaili.com/nn/%s' %page
        user_agent = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
        request = urllib2.Request(url)
        request.add_header("User-Agent", user_agent)
        content = urllib2.urlopen(request)
        soup = BeautifulSoup(content)
        trs = soup.find('table', {"id":"ip_list"}).findAll('tr')
        for tr in trs[1:]:
            tds = tr.findAll('td')
            ip = tds[2].text.strip()
            port = tds[3].text.strip()
            protocol = tds[6].text.strip()
            if protocol == 'HTTP' or protocol == 'HTTPS':
                f.write('%s=%s:%s\n' % (protocol, ip, port))
                print '%s://%s:%s' % (protocol, ip, port)
                
def caiji(self):    #采集“有代理IP”网的代理，这个网站不是用表单呈现页面，不便于使用xpath，
    of = open('proxy.txt', 'w')
    url = 'http://www.youdaili.net/Daili/guonei/3661'
    #URL地址尾号是一个数字，相邻两篇文章，数字相差6，例如3361之后是3367，再之后是3373
    for i in range(1,4):
        if i == 1:
            Url = url+'.html'
        else:
            Url = url+'_%s.html' %i
        html = requests.get(Url).text
        res = re.findall(r'\d+\.\d+\.\d+\.\d+\:\d+', html)
        for pro in res:
            of.write('http=%s\n' %pro)
            print pro
    of.closed
    
def caiji2(self):   #“好代理IP”
    # 这个网站采取IP封杀爬虫，如果要爬取这个网站的代理，首先要使用代理来应对反爬虫
    of = open('proxy.txt', 'w')
    url = 'http://www.haodailiip.com/guonei/'
    for i in range(1,20):
        Url = 'http://www.haodailiip.com/guonei/' + str(i)
        print u"正在采集"+Url
        html = requests.get(Url).text
        bs = BeautifulSoup(html)
        table = bs.find('table',{"class":"proxy_table"})
        tr = table.findAll('tr')
        for i in range(1,31):
            td = tr[i].findAll('td')
            proxy_ip = td[0].text.strip()
            proxy_port = td[1].text.strip()
            of.write('http=%s:%s\n' %(proxy_ip,proxy_port))
            print 'http=%s:%s\n' %(proxy_ip,proxy_port)
        time.sleep(2)
    of.closed
    
    
class yanzheng(Thread):
    inFile = open('proxy.txt', 'r')
    outFile = open('available.txt', 'a')
    url = 'http://www.lindenpat.com/search/detail/index?d=CN03819011@CN1675532A@20050928'
    lock = threading.Lock()

    def test(self):
        self.lock.acquire()  #获得锁
        line = self.inFile.readline().strip()    #从文件中读取一行
        self.lock.release()  #释放锁
        if len(line) == 0: 
            return  #多进程启动的时候，如果没有IP可查询，那么return
        protocol, proxy = line.split('=')
        #cookie = "PHPSESSID=5f7mbqghvk1kt5n9illa0nr175; kmsign=56023b6880039; KMUID=ezsEg1YCOzxg97EwAwUXAg=="
        try:
            proxy_support = urllib2.ProxyHandler({protocol.lower():'://'.join(line.split('='))})
            opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
            urllib2.install_opener(opener)
            #request = urllib2.Request(self.url)
            request = urllib2.Request('http://www.baidu.com')
            #request.add_header("cookie",cookie)
            content = urllib2.urlopen(request,timeout=8).read()
            if len(content) > 0:
                self.lock.acquire()
                try:
                    self.outFile.write('%s=%s\n' % (protocol, proxy))
                    print ('add proxy %s=%s\n' % (protocol, proxy))
                finally:
                    self.lock.release()
            else:
                print u'出现验证码或IP被封杀'
        except timeout, tout:
        #except socket.timeout,tout
            print u"出现如下错误:"
            timeout_f = open("ip/timeout.txt","a")
            timeout_f.write('%s=%s\n' % (protocol, proxy))
            timeout_f.close()
            print tout
        ##区分两个不同的异常
        except ConnectionError,conerr:
            conerr_f = open("ip/conerr.txt","a")
            conerr_f.write('%s=%s\n' % (protocol, proxy))
            conerr_f.close()
            print conerr
        except URLError,urlerr:
            urlerr_f = open("ip/urlerr.txt","a")
            urlerr_f.write('%s=%s\n' % (protocol, proxy))
            urlerr_f.close()
            print urlerr
        self.lock.acquire()  #获得锁
        self.count += 1
        print "test %d record!" %self.count
        self.lock.release()  
        return self.test()  
        
    def main(self):
        self.count = 0
        all_thread = []
        for i in range(500):
            t = threading.Thread(target=self.test)
            all_thread.append(t)
            t.start()
         
        for t in all_thread:
            t.join()
        
        #self.test()
        self.inFile.close()
        self.outFile.close()
        print "yanzheng end!"
    
###############################
from multiprocessing import Process
from multiprocessing import Pool
import os, time, random

if __name__=='__main__':
    print('Parent process %s.' % os.getpid())
    #p1 = Process(target=ProxyIPSpider, args=('',))
    #p2 = Process(target=caiji, args=('',))
    #p3 = Process(target=caiji2, args=('',))
    yz = yanzheng()
    p4 = Process(target=yz.main(), args=('',))
    
    print('Waiting for all subprocesses done...')
    #p1.start()
    #p2.start()
    #p3.start()
    p4.start()
    #p1.join()
    #p2.join()
    #p3.join()
    p4.join()
    print('All subprocesses done.')
###############################
'''
启动500条线程，只验证了500条（实际由于线程异常，导致只验证四百五十条）数据
怎么才能把文件中全部记录都验证呢？
为什么抛出ConnectionError、timeout，却没有记录到文件呢
'''
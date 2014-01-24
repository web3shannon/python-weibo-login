#!/usr/bin/env python
# coding=utf8

'Email: zhengyi.bupt@qq.com'

import urllib
import urllib2
import cookielib
import base64
import re
import json
import rsa
import binascii

class WeiboLogin:

	username = ''
	password = ''
	serverUrl = ''
	loginUrl = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.11)'

	postData = {
		'entry': 'weibo',
		'gateway': '1',
		'from': '',
		'savestate': '7',
		'userticket': '1',
		'pagerefer': 'http://weibo.com/a/download',
		'vsnf': '1',
		'su': '',
		'service': 'miniblog',
		'servertime': '',
		'nonce': '',
		'pwencode': 'rsa2',
		'rsakv': '',
		'sp': '',
		'encoding': 'UTF-8',
		'prelt': '60',
		'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
		'returntype': 'META'
	}

	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.serverUrl = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.11)' % username
		
		cookiejar = cookielib.LWPCookieJar()
		cookie_support = urllib2.HTTPCookieProcessor(cookiejar)
		opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler(debuglevel=1))
		urllib2.install_opener(opener)


	def login(self):
		servertime, nonce, pubkey, rsakv = self.getServerTime()

		self.postData['servertime'] = servertime
		self.postData['nonce'] = nonce
		self.postData['rsakv'] = rsakv
		self.postData['su'] = self.getSu()
		self.postData['sp'] = self.getSp(servertime, nonce, pubkey)
		
		text = self.getUrl(self.loginUrl, self.postData, 'POST')

		p = re.compile('location\.replace\(\"(.*)\"\)')
		
		try:
			loginUrl = p.search(text).group(1)
			self.getUrl(loginUrl)
			print "Login success!"
			return True
		except:
			print 'Login error!'
			return False

	def getServerTime(self):
		data = self.getUrl(self.serverUrl)
		p = re.compile('\((.*)\)')
		
		try:
			jsonData = p.search(data).group(1)
			data = json.loads(jsonData)
			servertime = str(data['servertime'])
			nonce = data['nonce']
			pubkey = data['pubkey']
			rsakv = data['rsakv']
			return servertime, nonce, pubkey, rsakv
		except:
			print 'getServerTime error!'
			return None

	def getSu(self):
		username = urllib.quote(self.username)
		su = base64.encodestring(username)[:-1]
		return su

	def getSp(self, servertime, nonce, pubkey):
		rsaPublickey = int(pubkey, 16)
		key = rsa.PublicKey(rsaPublickey, 65537)
		message = str(servertime) + '\t' + str(nonce) + '\n' + str(self.password)
		passwd = rsa.encrypt(message, key)
		sp = binascii.b2a_hex(passwd)
		return sp
	
	def getUrl(self, url, para = {}, m = 'GET'):
		header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'}
		data = urllib.urlencode(para)

		if m == 'GET':
			if para == {}:
				req = urllib2.Request(
					url = url,
					headers = header
				)
			else:
				req = urllib2.Request(
					url = url + "?" + data,
					headers = header
				)

		elif m == 'POST':
			req = urllib2.Request(
				url = url,
				data = data,
				headers = header
			)
		else:
			req = ''
			
		result = urllib2.urlopen(req)
		text = result.read()
		
		return text
	
	def follow(self, uid):
		url = 'http://weibo.com/aj/f/followed?_wv=5'
		para = {
			'uid': uid,
			'f': '1',
			'location': 'profile',
			'wforce': '1',
			'refer_sort': 'profile',
			'refer_flag': '',
			'_t': '0'
		}
		data = urllib.urlencode(para)
		req = urllib2.Request(
			url = url,
			data = data,
			headers = {
				'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
				'Referer':'http://weibo.com/u/' + uid
			}
		)
		urllib2.urlopen(req)
	
	def savePage(self, pageName, data):
		fout = open(pageName, 'w')  
		fout.write(data)  
		fout.close() 


if __name__ == '__main__':
		weibo = WeiboLogin('name', 'password')
		
		weibo.login()
		weibo.follow('1682175375')


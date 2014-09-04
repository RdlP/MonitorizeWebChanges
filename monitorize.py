from HTMLParser import HTMLParser
import urllib2
import time
try:
    import pynotify
except ImportError:
    from win32api import *
    from win32gui import *
    import win32con

import sys, os
import struct
import datetime
import platform
import requests # sudo pip install requests
from random import randint

class WindowsBalloonTip:
    def __init__(self, title, msg):
        message_map = {
            win32con.WM_DESTROY: self.OnDestroy,
        }
        wc = WNDCLASS()
        hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = "Python"
        wc.lpfnWndProc = message_map
        classAtom = RegisterClass(wc)
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = CreateWindow( classAtom, "Taskbar", style, \
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, \
                0, 0, hinst, None)
        UpdateWindow(self.hwnd)
        iconPathName = os.path.abspath(os.path.join( sys.path[0], "balloontip.ico" ))
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
           hicon = LoadImage(hinst, iconPathName, \
                    win32con.IMAGE_ICON, 0, 0, icon_flags)
        except:
          hicon = LoadIcon(0, win32con.IDI_APPLICATION)
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, "tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY, \
                         (self.hwnd, 0, NIF_INFO, win32con.WM_USER+20,\
                          hicon, "Balloon  tooltip",msg,200,title))
        # self.show_balloon(title, msg)
        time.sleep(10)
        DestroyWindow(self.hwnd)
    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0) # Terminate the app.

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)  
        self.isArticle = False
        self.isA = False
        self.isFrame = False
        self.previous = []
        self.offer = ""
        self.url = ""
        self.isURL = False
        self.post = False
        self.code = ""
        print platform.system()
        if platform.system() == "Linux":
            pynotify.init("markup")
        
    def reset(self):
        HTMLParser.reset(self)
        self.isArticle = False
        self.isA = False
        self.isFrame = False
    
    def showNotifyUnix(self, text):
        n = pynotify.Notification("<b>ha actualizado</b>",
        text
        )
        n.show()
        
    def showNotifyWindows(self, text):
        w=WindowsBalloonTip("ha actualizado", text)
        
    def getUrl(self):
        if self.isURL == False:
            return None
        else:
            return self.url
            
    def sendPost(self):
        self.post = True
        
    def disablePost(self):
        self.post = False
        
    def handle_starttag(self, tag, attrs):
        if self.isArticle == False:
            if tag == "article":
                if self.previous != attrs:
                    self.previous = attrs
                self.isArticle = True
        if self.isArticle == True and self.isA == False:
            if tag == "a":
                if self.offer != attrs[1][1]:
                    if platform.system() == "Linux":
                        self.showNotifyUnix(attrs[1][1])
                    else:
                        self.showNotifyWindows(attrs[1][1])
                    self.offer = attrs[1][1]
                self.isA = True
        if self.isArticle == True and self.isA == True and self.isFrame == False:
            if tag == "iframe":
                if self.url != attrs[3][1]:
                    print "Nueva url encontrada:",attrs[3][1]
                    self.isURL = True
                    self.url = attrs[3][1]
                else:
                    self.isURL = False
                self.isFrame = True
        if self.post == True:
            if tag == "input":
                if attrs[0][0] == "type" and attrs[0][1] == "hidden" and attrs[1][0] == "id" and attrs[1][1] == "gdkd":
                    self.code = attrs[3][1]
                    email = "me@email.com"
                    payload = {'gdkd': self.code, 'email': email, 'email_repeat': email}
                    r = requests.post(self.url, data=payload)
                    print "Peticion POST enviada"

parser = MyHTMLParser()

while 1:
    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0')]
        response = opener.open('http://www.web.es/')
        encoding = response.headers.getparam('charset')
        html = response.read().decode(encoding)
        parser.feed(html)
        url = parser.getUrl()
        parser.reset()
        opener.close()
        rand = randint(1,2)
        print "Tiempo a esperar:", rand
        if url != None:
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0')]
            response = opener.open(url)
            encoding = response.headers.getparam('charset')
            if encoding != None:
                html = response.read().decode(encoding)
            else:
                html = response.read()
            #print html
            parser.sendPost()
            parser.feed(html)
            parser.disablePost()
        time.sleep(rand)
    except urllib2.URLError, e:
        print "Error de red a las ", datetime.datetime.now()

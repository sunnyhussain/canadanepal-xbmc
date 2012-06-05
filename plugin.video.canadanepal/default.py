# CanadaNepal plugin written by humla.

import re
import os
import urlresolver
import urllib,urllib2
import xbmcplugin,xbmcgui
import xbmcaddon

# Taken from desitvforum xbmc plugin.
def GetDomain(url):
    print url
    tmp = re.compile('//(.+?)/').findall(url)
    domain = 'Unknown'
    if len(tmp) > 0:
        domain = tmp[0].replace('www.', '')
    return domain

def CATEGORIES():
    cwd = xbmcaddon.Addon().getAddonInfo('path')
    img_path = cwd + '/images/'
    addDir('Latest Videos', 'http://www.canadanepal.info', 1, 'http://canadanepal.info/images/tvprograms.gif')
    addDir('Live TV', cwd + '/resources/live_tv.xml', 6, 'http://canadanepal.info/images/banner/onlinetvf.jpg')
    addDir('Live Radio', 'http://canadanepal.info/fm/',4, 'http://canadanepal.info/images/listenfmlogo.gif')
    addDir('Daily News', 'http://canadanepal.info/dailynews/',7,'http://canadanepal.info/images/banner/samachar20.jpg')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def get_news(m_url, name):
    get_today_news()
    url = 'http://canadanepal.info/dailynews/update.htm'
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    match = re.compile('<a href="(.+?)" .+?>.+?>(.+?)<') .findall(link)
    for u,name in match:
        addDir(name, m_url+u, 2 ,"")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
def get_today_news():
    url = 'http://canadanepal.info/dailynews/'
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link = response.read()
    response.read()
    name=re.compile('Today\'s(.+?)<').findall(link)
    address = get_youtube_link(link)
    print name[0], address[0]
    addDir(name[0],address[0],3,"")

def SHOWRADIO(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match=re.compile('<li><a href="(.+?)"  class="normal"  target="_self" ><span>(.+?)</span></a></li>').findall(link)
    for fm_url,name in match:
            addDir(name,url + fm_url,5,"")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

# Scans the page to find streaming url for live radio.
def get_radio_links(link):
    match=re.compile('(.+?)file=(.+?)&amp').findall(link)
    if (len(match) == 0):
        match=re.compile('(.+?)stream1=(.+?)&amp;').findall(link)
    return [b for a,b in match]

# Scans the main FM page looking for stations that are available
def AUDIOLINKS(url, name):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    
    match = get_radio_links(link)
    if (len(match) > 0):
        xbmc.Player().play(match[0], "")
    return 

# Removes html tags from NAME
def clear_htmltags(name):
    tags = ['&quot;', '-', '&amp;', '</font>', '<font color="#bf4040">', '<font color="#af5050">', '<font color="#0e0e0e">', '<strong>', '</strong>', '<font size="2">', '&nbsp;']
    for tag in tags:
        name = name.replace(tag,'')
    return name

# Lists the new episodes of TV series
def INDEX(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match=re.compile('<div><font size="2"><strong>(.+?)<a href="(.+?)" title="" target="_blank">Click').findall(link)
    image_base_url = xbmcaddon.Addon().getAddonInfo('path') + '/images/'
    for name,url in match:
        name = clear_htmltags(name)
        image_name = name[:4]
        image_url = image_base_url + image_name + '.jpg'
        print image_url
        addDir(name,url,2,image_url)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

# Show the list of live tv 
def SHOWLIVETVLIST(url):
    openfile = open(url, 'r')
    result = openfile.read()
    openfile.close()
    match = re.compile('<channel>((.|\n)+?)</channel>').findall(result)
    for info,_ in match:
        #print info
        name = re.compile('<name>(.+?)</name').findall(info)
        picture = re.compile('<image>(.+?)</image>').findall(info)
        url = re.compile('<link>(.+?)</link>').findall(info)
        addLink(name[0], url[0],picture[0]) 

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return

def get_dailymotion_link(link):
    print "Scraping Dailymotion link"
    match=re.compile('<a href="(.+?)" target="_blank"> </a>').findall(link)
    return match

def get_youtube_link(link):
    print "Scraping youtube link"
    match=re.compile('<.+? value="http://www.youtube.com/v/(.+?)"').findall(link)
    return ["http://www.youtube.com/watch?v="+a for a in match]

def get_blip_tv_link(link):
    print "Scraping blip tv link"
    match=re.compile('<iframe (allowfullscreen="" frameborder="0" height="\d\d\d" )?src="(.+?)\?p=1"').findall(link)
    print match
    return [b for a,b,c in match]
    
def VIDEOLINKS(url,name):
    print "Getting video links"
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match = get_youtube_link(link)
    if (len(match) == 0):
        match = get_blip_tv_link(link)
    if (len(match) == 0):
        match = get_dailymotion_link(link)
    i = 1
    length = len(match)
    image_path = xbmcaddon.Addon().getAddonInfo('path') + '/images/'
    for url in match:
        domain = GetDomain(url)
        addDir(domain + " : Part  " + str(i) + " of " + str(length), url, 3, image_path + domain + '.jpg')
        i = i + 1
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play_video(url,name):
    domain = GetDomain(url)
    if domain == "blip.tv":
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        res=response.read()
        redirect =  response.geturl()
        v_id=re.compile('flash%2F(\d\d\d\d\d\d\d)').findall(redirect)
        stream_url= 'plugin://plugin.video.bliptv/?action=play_video&videoid=' + v_id[0]
        response.close()
    else:    
        stream_url = urlresolver.resolve(url)
    xbmc.Player().play(stream_url, "")

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

def addLink(name,url,iconimage):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok


def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok
        
              
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: " + str(mode)
print "Name: " + str(name)
print "URL: " + str(url)

# Modes
# 0: The main Categories Menu
# 1: For latest videos
# 2: Give the link of a page a serial (Meri Bassai 12th May) 
# 3: Play the video given the link
# 4: Give the list of available radio stations
# 5: Get link for each radio station
# 6: Chose live Tv from the main menu
# 7: Daily News scrapign for link

if mode==None or url==None or len(url)<1:
        CATEGORIES()
elif mode==1:
        INDEX(url)
elif mode==4:
        SHOWRADIO(url)
elif mode==6:
        SHOWLIVETVLIST(url)
elif mode==2:
        VIDEOLINKS(url,name)
elif mode==5:
        AUDIOLINKS(url,name)
elif mode==3:
        play_video(url, name) 
elif mode==7:
        get_news(url, name)

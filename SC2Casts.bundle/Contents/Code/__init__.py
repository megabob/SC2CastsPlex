import urllib, urllib2, re

VIDEO_PREFIX = "/video/sc2casts"

SC2CASTS_URL = "http://sc2casts.com"

BROWSE_URL = "/browse"
RECENT_URL = "/"
TOP24_URL = "/top"
TOPWEEK_URL = "/top?week"
TOPMONTH_URL = "/top?month"
TOPALL_URL = "/top?all"

NAME = "SC2Casts"

ART = "art-default.jpg"
ICON = "icon-default.png"

def Start():
	Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	MediaContainer.art = R(ART)
	MediaContainer.title1 = NAME
	MediaContainer.viewGroup = "List"
	DirectoryItem.thumb = R(ICON)
	Log("Started")
	
def MainMenuWorks():
	oc = ObjectContainer()
	url = "http://www.youtube.com/watch?v=johJGsJmf3U"
	oc.add(VideoClipObject(
			url = url,
			title = "using object container and video clip object",
			summary = "gameTitle summary"))
	return oc
	
def MainMenu():
	dir = MediaContainer(viewMode="List")
	dir.Append(Function(DirectoryItem(GameList, "Recent Casts"), page=RECENT_URL))
	dir.Append(Function(DirectoryItem(SubMenuList, "Top Casts"), pageType=0))
	dir.Append(Function(DirectoryItem(SubMenuList, "Browse"), pageType=1))
	return dir

def SubMenuList(sender, pageType=None):
	dir = MediaContainer(viewMode="List")
	if pageType == 0:
		dir.Append(Function(DirectoryItem(GameList, "Last 24 Hours"), page=TOP24_URL))
		dir.Append(Function(DirectoryItem(GameList, "This Week"), page=TOPWEEK_URL))
		dir.Append(Function(DirectoryItem(GameList, "This Month"), page=TOPMONTH_URL))
		dir.Append(Function(DirectoryItem(GameList, "All Time"), page=TOPALL_URL))
	if pageType == 1:
		dir.Append(Function(DirectoryItem(BrowseList, "Browse Events"), pageNum=0))
		dir.Append(Function(DirectoryItem(BrowseList, "Browse Players"), pageNum=1))
		dir.Append(Function(DirectoryItem(BrowseList, "Browse Casters"), pageNum=2))
		dir.Append(Function(DirectoryItem(BrowseList, "Browse Matchups"), pageNum=3))
	return dir
	
def BrowseList(sender, pageNum):
	dir = MediaContainer(viewMode="List")
	page = HTML.ElementFromURL(SC2CASTS_URL+BROWSE_URL)
	pageElement = page.xpath("//td[@valign='top']")[pageNum]
	pageParts = pageElement.xpath("./h3")
	for element in pageParts:
		url = element.xpath("./a")[0].get("href")
		name = element.xpath("./a/text()")[0]
		if pageNum == 3:
			url = "/"+url
		dir.Append(Function(DirectoryItem(GameList, name), page=url))
	
	return dir;

def GameList(sender, page="", pageNum=0):
	dir = MediaContainer(viewMode="List")
	page = HTML.ElementFromURL(SC2CASTS_URL+page)
	
	casts = page.xpath("//div[@class='content']/div")
	dates = page.xpath("//div[@class='content']/div[@style='padding-top: 10px;']")
	dateCount = len(dates)
	Log("DateCount = "+str(dateCount))
	date = ""
	dIndex = 0
	for cast in casts:
		if (cast.get("class")==None):
			if (dIndex<dateCount):
				date = page.xpath("//div[@class='content']/div[@style='padding-top: 10px;']/text()")[dIndex]
				dIndex += 1
				date = date.strip()+" - "
		if (cast.get("class")=="latest_series"):
			url = cast.xpath(".//a")[0].get("href")
			gameCount = cast.xpath(".//a/text()")[1]
			gameType = cast.xpath(".//span[@style='color:#cccccc']")[0].text		
			player1 = cast.xpath(".//b")[0].text
			player2 = cast.xpath(".//b")[1].text
			event = cast.xpath(".//span[@class='event_name']")[0].text
			eventRound = cast.xpath(".//span[@class='round_name']")[0].text
			caster = cast.xpath(".//span[@class='caster_name']")[0].text
			source = cast.xpath(".//span[@class='source_name']")[0].text
			thumbnail = ICON
			if gameType==None:
				gameType = ""
			else:
				gameSType = gameType[1:-1]
				thumbnail = gameSType+".png"	
				gameType = gameType + " "
			Log("Thumb = "+thumbnail)		
			name = gameType + player1.strip() + " vs " + player2 + gameCount+" - " + event + " (" + eventRound + ") Cast By " + caster
			summary = gameType+" "+player1.strip()+" vs "+player2+gameCount+"\n" + date+event + " (" + eventRound + ")\nCast By " + caster
			dir.Append(Function(DirectoryItem(GamePartList, title=name, summary=summary, thumb=R(thumbnail)), url=url, thumbnail=thumbnail, summary=summary))
		
	return dir
	
def GamePartList(sender, url="", thumbnail="", summary=""):
	oc = ObjectContainer()
	Log("thumbnail = "+thumbnail)
	page = HTML.ElementFromURL(SC2CASTS_URL+url)
	games = page.xpath("//div[@class='videoViewer']/a")
	if len(games)>0:
		i = 0
		for game in games:
			i+=1
			gameSummary = "Game "+str(i)+"\n"+summary
			parts = page.xpath("//div[@id='g"+str(i)+"']//embed")
			partCount = len(parts)
			if partCount==2:
				gameTitle = "Game "+str(i)+" - Part 1"
				#dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=parts[0].get("src")))
				oc.add(VideoClipObject(url = NormalizeURL(parts[0].get("src")), title=gameTitle))
				gameTitle = "Game "+str(i)+" - Part 2"
				#dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=parts[1].get("src")))
				oc.add(VideoClipObject(url = NormalizeURL(parts[1].get("src")), title=gameTitle))
			if partCount==1:
				Log("BOB ADDING VIDEO CLIP")
				gameTitle = "Game "+str(i)
				#dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=parts[0].get("src")))
				oc.add(VideoClipObject(url = NormalizeURL(parts[0].get("src")), title=gameTitle))
			if partCount==0:
				gameTitle = "Game "+str(i)
				#dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=""))
				oc.add(VideoClipObject(""))
	else:
		parts = page.xpath("//embed")
		partCount = len(parts)

		if partCount==2:
			gameTitle = "Game - Part 1"
			#dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=parts[0].get("src")))
			oc.add(VideoClipObject(url = NormalizeURL(parts[0].get("src")), title=gameTitle))
			gameTitle = "Game - Part 2"
			#dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=parts[1].get("src")))
			oc.add(VideoClipObject(url = NormalizeURL(parts[1].get("src")), title=gameTitle))
		if partCount==1:
			gameTitle = "Game"
			#dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=parts[0].get("src")))
			oc.add(VideoClipObject(url = NormalizeURL(parts[0].get("src")), title=gameTitle))
		if partCount==0:
			gameTitle = "Game"
			#dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=""))
			oc.add(VideoClipObject(""))			
	
	return oc
	
def NormalizeURL(url):
	if url.find('/v/') != -1:
		url = url.replace('/v/', '/watch?v=')
	return VideoClipObject(url = url)
	
def GamePartListOld(sender, url="", thumbnail="", summary=""):
	dir = MediaContainer(viewMode="List")
	oc = ObjectContainer()
	Log("thumbnail = "+thumbnail)
	page = HTML.ElementFromURL(SC2CASTS_URL+url)
	games = page.xpath("//div[@class='videoViewer']/a")
	if len(games)>0:
		i = 0
		for game in games:
			i+=1
			gameSummary = "Game "+str(i)+"\n"+summary
			parts = page.xpath("//div[@id='g"+str(i)+"']//embed")
			partCount = len(parts)
			if partCount==2:
				gameTitle = "Game "+str(i)+" - Part 1"
				dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=parts[0].get("src")))
				gameTitle = "Game "+str(i)+" - Part 2"
				dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=parts[1].get("src")))
			if partCount==1:
				Log("BOB ADDING VIDEO CLIP")
				gameTitle = "BOBGame "+str(i)
				#dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=parts[0].get("src")))
				oc.add(VideoClipObject(
					url = parts[0].get("src"),
					title = gameTitle,
					summary = gameTitle+"\n"+summary))# Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=parts[0].get("src")))
			if partCount==0:
				gameTitle = "Game "+str(i)
				dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=""))
	else:
		parts = page.xpath("//embed")
		partCount = len(parts)
		if partCount==2:
			gameTitle = "Game - Part 1"
			dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=parts[0].get("src")))
			gameTitle = "Game - Part 2"
			dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=parts[1].get("src")))
		if partCount==1:
			gameTitle = "Game"
			dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=parts[0].get("src")))
		if partCount==0:
			gameTitle = "Game"
			dir.Append(Function(VideoItem(PlayVideo, thumb=R(thumbnail), title=gameTitle, summary=gameTitle+"\n"+summary), url=""))		
	
	return dir
	
def RetrieveUrlOld(url, referer):
	req = urllib2.Request(url)
	req.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.3) Gecko/20100402 Namoroka/3.6.3")
	req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
	req.add_header("Accept-Language", "en-us,en;q=0.5")
	req.add_header("Accept-Encoding", "deflate")
	req.add_header("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.7")
	if(referer != ""):
		req.add_header("Referer", referer)
	response = urllib2.urlopen(req)
	file = response.read()
	response.close()
	return file
	
def RetrieveUrl(url, referer):
	return HTTP.Request(url).content

	
def PlayVideoOld(sender, url):
	if url=="":
		return
	Log(url)
	vidID = re.compile("http://www.youtube.com/v/([^\"]+)").findall(url)[0]
	Log(vidID)
	infoURL = "http://www.youtube.com/watch?v="+vidID
	Log(infoURL)
	html = urllib.unquote(RetrieveUrl(infoURL, "http://www.youtube.com"))
	videoURL = urllib.unquote(re.compile("url_encoded_fmt_stream_map=url=([^&]+)&quality").findall(html)[0])
	Log(videoURL)
	return Redirect(videoURL)
	
def PlayVideo(sender, url):
	if url=="":
		return
	#Log(url)
	#new_url = url.replace('www.youtube', 'youtube.googleapis')
	#Log(new_url)
	#vidID = re.compile("http://www.youtube.com/v/([^\"]+)").findall(url)[0]
	#Log(vidID)
	#infoURL = "http://www.youtube.com/watch?v="+vidID
	infoURL = url
	Log(infoURL)
	html = urllib.unquote(HTTP.Request(infoURL).content)
	
	#urls = re.compile("url_encoded_fmt_stream_map=url=([^&]+)&quality").findall(html)
	Log(html[:200])
	Log('Test 1' + re.compile("url_encoded_fmt_stream_map.*?url=(.*?)\\\\u0026").findall(html)[0])
	urls = re.compile("url_encoded_fmt_stream_map.*?url=(.*?)\\\\u0026").findall(html)
	Log("!!!!URLS: %s" % urls)
	videoURL = urllib.unquote(urls[0])
	Log(videoURL)
	return Redirect(videoURL)

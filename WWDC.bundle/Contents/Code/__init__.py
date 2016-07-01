import collections, os, re, urllib
from dateutil.parser import parse

SOURCE_URL = "https://devimages-cdn.apple.com/wwdc-services/g7tk3guq/xhgbpyutb6wvn2xcrbcz/videos.json"
DEFAULT_CACHE_TIME = 3600

# Locate first 2 or 4 digit number as year (optional), and first 3+ digit number in filename as session id
FILENAME_PARSE_RE = re.compile("^(?:(?:[\w\W]*\D)?(\d{2}|\d{4})\D)?(?:[\w\W]*\D)?(\d{3,})(?:\D[\w\W]*)?$")

# Locate first 2 or 4 digit number in parent directory name as year
PARENT_DIR_PARSE_RE = re.compile("^(?:[\w\W]*\D)?(\d{2}|\d{4})(?:\D[\w\W]*)?$")

TITLE_CLEAN_RE = re.compile("([^a-z0-9 ]+)")

##################################################

def Start():
  pass

##################################################

class WwdcSession:
  def __init__(self):
    self.year = None
    self.id = None
    self.title = None
    self.description = None
    self.date = None
    self.categories = []
    self.thumbnail = None
    self.score = 0

  @staticmethod
  def fromFilename(path):
      
    def parseYear(s):
      year = None
      if s != None:
        year = int(s)
        if year < 100:
          year += 2000
      return year
    
    session = WwdcSession()

    splitPath = os.path.split(path)
    filename = splitPath[1]

    match = FILENAME_PARSE_RE.search(filename)
    if match:
      session.year = parseYear(match.group(1))
      session.id = int(match.group(2))

    if session.year == None:
      parent_directory = os.path.split(splitPath[0])[1]
      match = PARENT_DIR_PARSE_RE.search(parent_directory)
      if match:
        session.year = parseYear(match.group(1))

    return session

  @staticmethod
  def fromJson(sessionJson):
    session = WwdcSession()
    session.year = int(sessionJson["year"])
    session.id = int(sessionJson["id"])
    session.title = sessionJson["title"]
    session.description = sessionJson["description"]

    dateString = sessionJson["date"]
    if dateString != None and dateString != session.year:
      try:
        session.date = parse(dateString)
      except:
        pass

    track = sessionJson["track"]
    if isinstance(track, str):
      session.categories.append(track)

    focus = sessionJson["focus"]
    if isinstance(focus, collections.Sequence):
      session.categories.extend([x for x in focus if isinstance(x, str)])
    
    images = sessionJson["images"]
    if "shelf" in images:
      session.thumbnail = images["shelf"]

    return session

  @staticmethod
  def fromMetadataId(id):
    session = WwdcSession()

    match = re.search("(\d+)-(\d+)", id)
    if match != None:
      session.year = int(match.group(1))
      session.id = int(match.group(2))

    return session

  def getMetadataId(self):
    return "{}-{}".format(self.year, self.id)

##################################################

def rankMatch(query, candidate):
  if query == None or candidate == None:
    return 0

  queryWords = TITLE_CLEAN_RE.sub("", query.lower()).split(" ")
  candidateWords = TITLE_CLEAN_RE.sub("", candidate.lower()).split(" ")

  candidateLength = 0
  matchLength = 0
  for word in candidateWords:
    candidateLength += len(word)
    if word in queryWords:
      matchLength += len(word)

  if candidateLength == 0:
    return 0

  return float(matchLength) / candidateLength

##################################################

def fetchSessions(year, id, exact, name=None):
  result = []

  sessions = JSON.ObjectFromURL(SOURCE_URL, cacheTime=DEFAULT_CACHE_TIME)

  for sessionJson in sessions["sessions"]:
    session = WwdcSession.fromJson(sessionJson)
    score = 0

    if year == session.year:
      score += 30
    
    if id == session.id:
      score += 70

    if score < 100 and name != None:
      score += int((100 - score) * rankMatch(name, session.title))

    session.score = score
    if (exact and year == session.year and id == session.id) or (not exact and score > 0):
      result.append(session)

  return result

##################################################

class WwdcAgent(Agent.Movies):
  name = "WWDC"
  languages = [
    Locale.Language.English
  ]
  primary_provider = True
  fallback_agent = False
  accepts_from = None
  contributes_to = None

  def search(self, results, media, lang, manual):
    filename = urllib.unquote(media.filename)
    session = WwdcSession.fromFilename(filename)

    if session.year == None and media.year != None:
      session.year = int(media.year)

    if session.year == None and session.id == None:
      return

    sessions = fetchSessions(session.year, session.id, False, media.name)
    for session in sessions:
      results.Append(MetadataSearchResult(id=session.getMetadataId(), name=session.title, year=session.year, score=session.score, lang=lang))

  def update(self, metadata, media, lang, force):
    session = WwdcSession.fromMetadataId(metadata.id)

    if session.year == None and session.id == None:
      return

    sessions = fetchSessions(session.year, session.id, True)

    if len(sessions) != 1:
      return

    session = sessions[0]

    if force or metadata.title == None or len(metadata.title) == 0:
      metadata.title = session.title

    if force or metadata.year == None or len(metadata.year) == 0:
      metadata.year = session.year

    if (force or metadata.originally_available_at == None) and session.date != None:
      metadata.originally_available_at = session.date

    if force or metadata.summary == None or len(metadata.summary) == 0:
      metadata.summary = session.description

    if force or metadata.collections == None or len(metadata.collections) == 0:
      metadata.collections = session.categories

    if session.thumbnail != None and session.thumbnail not in metadata.art:
      try:
        metadata.art[session.thumbnail] = Proxy.Media(HTTP.Request(session.thumbnail))
      except:
        pass

import collections, os, re, urllib
from dateutil.parser import parse

SOURCE_URL = "https://devimages-cdn.apple.com/wwdc-services/g7tk3guq/xhgbpyutb6wvn2xcrbcz/videos.json"
DEFAULT_CACHE_TIME = 3600

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
    self.images = None

  @staticmethod
  def fromFilename(path):
    session = WwdcSession()

    splitPath = os.path.split(path)
    filename = splitPath[1]
    parent_directory = os.path.split(splitPath[0])[1]

    # Locate first 3+ digit number in filename as session id
    match = re.search("^(?:[\w\W]*\D)?(\d{3,})(?:\D[\w\W]*)?$", filename)
    if match != None:
      session.id = int(match.group(1))

    # Locate first 2 or 4 digit number in parent directory name as year
    match = re.search("^(?:[\w\W]*\D)?(\d{2}|\d{4})(?:\D[\w\W]*)?$", parent_directory)
    if match != None:
      session.year = int(match.group(1))
      if session.year < 100:
        session.year = session.year + 2000

    return session

  @staticmethod
  def fromJson(sessionJson):
    session = WwdcSession()
    session.year = int(sessionJson["year"])
    session.id = int(sessionJson["id"])
    session.title = sessionJson["title"]
    session.description = sessionJson["description"]
    session.images = sessionJson["images"]

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

def fetchSessions(year, id):
  result = []

  sessions = JSON.ObjectFromURL(SOURCE_URL, cacheTime=DEFAULT_CACHE_TIME)

  for sessionJson in sessions["sessions"]:
    session = WwdcSession.fromJson(sessionJson)
    if (year == None or year == session.year) and (id == None or id == session.id):
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

    # TODO: Enable fuzzy matching on session name and improve scoring
    sessions = fetchSessions(session.year, session.id)

    score = 100
    if session.year == None:
      score -= 20
    if session.id == None:
      score -= 50

    for session in sessions:
      results.Append(MetadataSearchResult(id=session.getMetadataId(), name=session.title, year=session.year, score=score, lang=lang))

  def update(self, metadata, media, lang, force):
    session = WwdcSession.fromMetadataId(metadata.id)

    if session.year == None and session.id == None:
      return

    sessions = fetchSessions(session.year, session.id)

    if len(sessions) != 1:
      return

    session = sessions[0]

    # TODO: Use 'hero'/'playback'/'shelf' images

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

from typing import List
import re

class RezkaSubtitle:
  lang: str = None
  url: str = None

  def __init__(self, url_string) -> None:
    self.lang, self.url = self._parse_string(url_string)

  @staticmethod
  def _parse_string(string: str) -> tuple[str, str]:
    pattern = r'\[(.*?)\](https?://\S+)'
    matches = re.match(pattern, string)
    if not matches:
      raise ValueError('Given string is broken!')
    return matches.group(1), matches.group(2)

  @property
  def language(self) -> str:
    languages = {'Русский': 'ru', 'English': 'en', 'Украинский': 'ua'}
    return languages[self.lang]
  
  @property
  def json(self) -> dict:
    return dict(lang=self.lang, url=self.url)

  def __repr__(self) -> str:
    return f'<Subtitle {self.lang}>'
  
  def __str__(self) -> str:
    return f'[{self.lang}]{self.url}'


class RezkaSubtitles(List[RezkaSubtitle]):
  def __init__(self, *args) -> None:
    for arg in args:
      self.append(RezkaSubtitle(arg))

  def __getitem__(self, lang: str) -> RezkaSubtitle:
    for item in self:
      if item.lang == lang or item.language == lang:
        return item
      
  @property
  def json(self):
    return [a.json for a in self]

  def __repr__(self) -> str:
    return f'<Subtitles [{",".join(item.lang for item in self)}]>'
  
  def __str__(self) -> str:
    return f"[{','.join(item.lang for item in self)}]"
  

class RezkaStream:
  quality: str = None
  url: str = None

  def __init__(self, quality, url) -> None:
    self.quality = quality
    self.url = url

  @property
  def qual(self) -> int:
    qual = int(re.search(r'(\d+)', self.quality).group(1))
    if 'Ultra' in self.quality: qual += 1
    return qual
  
  @property
  def json(self):
    return dict(quality=self.quality, url=self.url)
  
  def __lt__(self, other) -> bool:
    return self.qual < other.qual
  
  def __gt__(self, other) -> bool:
    return self.qual > other.qual
  
  def __ge__(self, other) -> bool:
    return self.qual >= other.qual
  
  def __le__(self, other) -> bool:
    return self.qual <= other.qual
  
  def __repr__(self) -> str:
    return f'<Stream [{self.quality}]>'
  
  def __str__(self) -> str:
    return f'[{self.quality}]{self.url}'
  

class RezkaStreams:
  _name: str = None
  translator: int = None
  subtitles: RezkaSubtitles = None
  season: int = None
  episode: int = None
  streams: List[RezkaStream] = []

  def __init__(self, translator, subtitles=None, season=None, episode=None):
    self.translator = translator
    self.subtitles = RezkaSubtitles(*subtitles) if subtitles else None
    self.season = season
    self.episode = episode
  
  def add(self, stream) -> None:
    self.streams.append(RezkaStream(**stream))

  @property
  def name(self) -> str:
    return self._name
  
  @name.setter
  def name(self, value) -> None:
    self._name = value 

  @property
  def highest(self) -> str:
    return max(sorted(self.streams, reverse=True))
  
  @property
  def json(self) -> dict:
    return dict(translator=self.translator, subtitles=self.subtitles.json(), season=self.season, episode=self.episode, streams=[a.json for a in self.streams])
    
  def __getitem__(self, value) -> RezkaStream:
    for item in self.streams:
      if item.quality == value:
        return item
    return None
  
  def __call__(self, lang) -> RezkaSubtitle:
    for subtitle in self.subtitles:
      if subtitle.lang == lang or subtitle.language == lang:
        return subtitle
  
  def __repr__(self) -> str:
    return f'<RezkaStream for {self._name}>'
  
  def __str__(self) -> str:
    return f'Rezka Stream {self.name} (voice={self.translator} subtitles={str(self.subtitles)})'

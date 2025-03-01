from typing import List
import re


class SearchItem:
  id: int = None
  url: str = None
  cover: str = None
  media_type: str = None
  ended: bool = None
  name: str = None
  year: str = None
  country: str = None

  def __init__(self, id, url, cover, media_type, ended, name, year, country, **kwargs) -> None:
    self.id = id
    self.url = url
    self.cover = cover
    self.media_type = self._detect_media_type(media_type)
    self.ended = self._is_ended(ended, self.media_type)
    self.name = name
    self._year = self._extract_years(year)
    self.country = country

  @staticmethod
  def _detect_media_type(mt) -> str:
    mts = {'Сериал': 'tv', 'Фильм': 'movie', 'Аниме': 'anime', 'Мультфильм': 'cartoon'}
    return mts[mt]
  
  @staticmethod
  def _extract_years(text: str) -> dict | str:
    years = re.findall(r'\b\d{4}\b', text)
    if len(years) > 1:
      return {'start': years[0], 'end': years[1]}
    return years[0]
  
  @staticmethod
  def _is_ended(status, mt) -> bool | None:
    if not status: return None
    if mt == 'tv': return mt == 'Завершен'

  @property
  def years(self) -> str:
    if type(self._year) == int or type(self._year) == str:
      return self._year
    return f'{self._year["start"]}-{self._year["end"]}'
  
  @property
  def json(self) -> dict:
    return dict(id=self.id, url=self.url, cover=self.cover, media_type=self.media_type, ended=self.ended, name=self.name, country=self.country, year=self.year)

  def __str__(self) -> str:
    return f'[{self.media_type}] {self.name} ({self.years})'

class SearchItems(List[SearchItem]):
  def __init__(self, *args) -> None:
    for arg in args:
      self.append(SearchItem(**arg))

  def __getitem__(self, value) -> SearchItem:
    if type(value) == int:
      tmp = self.copy()
      return tmp[value]
    for item in self:
      if item.name == value:
        return item
      if item.id == value:
        return item
    return None
  
  def add(self, items) -> None:
    for item in items:
      if not self[item['id']]:
        self.append(SearchItem(**item))

  @property
  def json(self):
    return [a.json for a in self]
  
  def __repr__(self) -> str:
    return f'<SearchItems>'

  def __str__(self) -> str:
    return f'{len(self)} SearchItem'

class SearchResponse:
  keyword: str = None
  pages: str = None
  items: SearchItems = None

  def __init__(self, keyword, pages, items) -> None:
    self.keyword = keyword
    self.pages = pages
    self.items = SearchItems(*items)

  def append(self, new_items) -> None:
    self.items.add(new_items)

  @property
  def json(self):
    return dict(keyword=self.keyword, pages=self.pages, items=self.items.json)

  def __repr__(self) -> str:
    return f'<Search response for {self.keyword}>'
  
  def __str__(self) -> str:
    return f'{str(self.items)} for keyword: {self.keyword}\n' + '\n'.join(f'{item.name} | {item.years}' for item in self.items)

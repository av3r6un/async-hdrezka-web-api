from wrappers import RezkaStreams as Streams, SearchResponse
from base64 import b64encode, b64decode
from bs4 import BeautifulSoup
from itertools import product
from .request import Request
import time
import re


class RezkaSearch:
  def __init__(self, request, debug=False) -> None:
    self._debug = debug
    self.keyword = None
    self.response = None
    self.page = 1
    self._request: Request = request

  @staticmethod
  def _free_from_brackets(text: str) -> str:
    return re.sub(r'\(.*?\)', '', text).strip()
  
  @staticmethod
  def _count_pages(soup) -> int:
    pages_cont = soup.select_one('.b-content__inline_items > .b-navigation')
    if not pages_cont:
      return 1
    pages = pages_cont.find_all('a', href=True)
    page_numbers = [int(re.search(r'page=(\d+)', link['href']).group(1)) for link in pages]
    return max(page_numbers) if page_numbers else 1
  
  def _parse_page(self, html) -> list:
    items = []
    soup = BeautifulSoup(html, 'html.parser')
    results = soup.find_all('div', attrs={'class': 'b-content__inline_item'})
    for result in results:
      ri = dict()
      ri['id'] = result.get('data-id')
      ri['url'] = result.get('data-url')
      ri['cover'] = result.select_one('.b-content__inline_item-cover > a > img').get('src')
      ri['ended'] = result.select_one('.b-content__inline_item-cover > a > span.info')
      ri['media_type'] = self._free_from_brackets(result.select_one('.b-content__inline_item-cover > a > span.cat > .entity').get_text())
      ri['name'] = result.select_one('.b-content__inline_item-link > a').get_text(strip=True)
      years, place, _ = result.select_one('.b-content__inline_item-link > div').get_text(strip=True).split(',')
      ri['year'] = years
      ri['country'] = place.strip()
      items.append(ri)
    pages = self._count_pages(soup) if len(results) >= 1 else 0
    return pages, items
  
  async def by_keyword(self, keyword, **kwargs) -> SearchResponse:
    self.keyword = keyword
    params = {'do': 'search', 'subaction': 'search', 'q': keyword}
    text = await self._request.get_page('search/', params)
    pages, info = self._parse_page(text)
    self.response = SearchResponse(keyword, pages, info)
    return self.response

  async def next_page(self, page_num=None) -> None:
    page_num += 1
    params = {'do': 'search', 'subaction': 'search', 'q': self.keyword, 'page': page_num}
    text = await self._request.get_page('search/', params)
    _, info = self._parse_page(text)
    self.response.append(info)


class RezkaStreams:
  def __init__(self, request, debug) -> None:
    self._debug = debug
    self._request: Request = request
    self.max_attempts = 3

  @staticmethod
  def _clear_trash(data) -> str:
    trashList = ['@', '#', '!', '^', '$']
    trashCodesSet = []
    for i in range(2, 4):
      startchar = ''
      for chars in product(trashList, repeat=i):
        data_bytes = startchar.join(chars).encode('utf-8')
        trash_combo = b64encode(data_bytes)
        trashCodesSet.append(trash_combo)
    arr = data.replace('#h', '').split('//_//')
    trash_string = ''.join(arr)

    for i in trashCodesSet:
      temp = i.decode('utf-8')
      trash_string = trash_string.replace(temp, '')
    
    final_string = b64decode(trash_string+"==")
    return final_string.decode('utf-8')
  
  async def get_episode(self, id, season, episode, translation='238', index = 0, **kwargs):
    attempt = 0
    while attempt <= self.max_attempts:
      try:
        info = await self._get_stream(id, season, episode, translation, index)
        self._append_stream_info(info)
        return self.streams
      except UnicodeDecodeError:
        attempt += 1
    else:
      raise ConnectionError('Failed to receive answer from server!')
    
  async def _get_stream(self, id, season, episode, translation, index):
    data = {'action': 'get_stream', 'translator_id': translation, 'season': season, 'episode': episode, 'id': id}
    params = {'t': int(time.time_ns() / 1000000)}
    info = await self._request.post('ajax/get_cdn_series/', params, data)
    if self._request['success']:
      subtitles = info['subtitle'].split(',') if info.get('subtitle') else None
      self.streams = Streams(translation, subtitles, season, episode)
      return self._clear_trash(info['url']).split(',')
    
  def _append_stream_info(self, info):
    for i in info:
      temp = i.split('[')[1].split(']')
      quality = str(temp[0])
      links = filter(lambda x: x.endswith('.mp4'))
      for video in links:
        self.streams.add({'quality': quality, 'url': video})


class Rezka:
  base_url = 'https://hdrezka.ag/'

  def __init__(self, debug=False):
    self._debug = debug
    self._request = Request(self.base_url, debug)
    self.search = RezkaSearch(self._request, debug)
    self.streams = RezkaStreams(self._request, debug)




  
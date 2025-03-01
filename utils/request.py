from aiohttp import ClientSession, ClientTimeout, ClientError
from dotenv import load_dotenv, find_dotenv
from fake_useragent import UserAgent
from asyncio import TimeoutError
from .logger import setup_logger
from wrappers import Response
import os


load_dotenv(find_dotenv())
logger = setup_logger('Request')

class Request:
  _headers = {
    'User-Agent': UserAgent().random,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Cookie': os.getenv('Cookie'), # access hdrezka.ag, create .env in root folder and paste your Cookie Header
    'Host': 'hdrezka.ag'
  }
  _base_uri: str = None


  def __init__(self, base_uri, debug=False):
    self._base_uri = base_uri
    self._debug = debug
    self._session = None

  async def _init_session(self):
    self._session = ClientSession(
      base_url=self._base_uri,
      headers=self._headers, response_class=Response,
      timeout=ClientTimeout(total=30.0),
      raise_for_status=False,
      trust_env=True,
    )

  async def __send(self, method, url, params=None, data=None, response='json') -> dict | str:
    await self._init_session()
    try:
      async with self._session.request(method, url, params=params, json=data) as resp:
        if self._debug:
          logger.debug(f'{resp.status} {resp.reason} | {resp.url}\n\n{resp.headers}\n\n{await resp.text()}')
        return await getattr(resp, response)()
    except (ClientError, TimeoutError) as err:
      logger.error(err)
      return None
    except AttributeError:
      logger.error(f'Bad response from server. Cant parse json. Traceback: {await resp.text()}')
    finally:
      await self._close()

  async def get(self, url, params=None) -> dict:
    return await self.__send('GET', url, params)

  async def get_page(self, url, params=None) -> str:
    return await self.__send('GET', url, params, response='text')
  
  async def post(self, url, params=None, data=None) -> dict:
    return await self.__send('POST', url, params, data)
  
  async def post_to_page(self, url, params=None, data=None) -> dict:
    return await self.__send('POST', url, params, data, response='text')
  
  async def _close(self):
    await self._session.close()

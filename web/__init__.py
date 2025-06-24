from aiohttp.web import json_response, Request
from utils.logger import setup_logger
from utils import Rezka
from aiohttp import web


routes = web.RouteTableDef()
rezka = Rezka(False)
logger = setup_logger('WebHandler')

@routes.get('/search')
async def search_media(req: Request):
  keyword = req.query.get('keyword')
  page = req.query.get('page')
  try:
    if page:
      long_response = None
      if rezka.search.response:
        await rezka.search.next_page(int(page))
        long_response = dict(status='success', body=rezka.search.response.json)
      else:
        info = await rezka.search.by_keyword(keyword)
        await rezka.search.next_page(int(page))
        long_response = dict(status='success', body=info.json)
      return json_response(data=long_response)
    info = await rezka.search.by_keyword(keyword)
    return json_response(data=dict(status='success', body=info.json))
  except ConnectionError as err:
    logger.error(str(err))
    return json_response(data=dict(status='error', message=str(err)), status=500)


@routes.get('/streams/{id}')
async def get_streams(req: Request):
  id = req.match_info.get('id')
  data = {
    'id': id, 'season': int(req.query.get('season', '1')), 'episode': int(req.query.get('episode', '1')),
    'translator': req.query.get('translator', None),
  }
  data = await rezka.streams.get_episode(**data)
  return json_response(data=dict(status='success', body=data.json))


def create_app(host='0.0.0.0', port=8080):
  app = web.Application()
  app.add_routes(routes)

  web.run_app(app, host=host, port=port)

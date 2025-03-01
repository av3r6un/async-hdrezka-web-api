from aiohttp import ClientResponse, JsonPayload

class Response(ClientResponse):
  success: bool = None
  message: str = ''

  @property
  def status_code(self):
    return self.status

  async def json(self, encoding=None, content_type='application/json'):
    if not self.status == 200:
      raise AttributeError('Bad response from server')
    json_data = await super().json(encoding, content_type=content_type)
    self.success = json_data.pop('success')
    self.message = json_data.pop('message')
    self.status_code = self.status
    return json_data

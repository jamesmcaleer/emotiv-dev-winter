This directory features the updates made to the [cortex.py](https://github.com/jamesmcaleer/emotiv-dev-winter/tree/main/python-cortex-api-change-v1-threading/cortex.py) file from my [python-cortex-api-change-v1-threading](https://github.com/jamesmcaleer/emotiv-dev-winter/tree/main/python-cortex-api-change-v1-threading) directory.

It also includes a text-based interface, demo.py, that features using the new library to interact with most components of the Cortex API.

# Setup
Clone the repository: `git clone https://github.com/jamesmcaleer/python-cortex-api-change-v2-asyncio.git`

# Requirements
- This example works with Python >= 3.7
- Install websockets via `pip install websockets`

# Demo

Use the new Cortex library to call the Cortex API and receieve a response in just _four_ lines of Python code:
```python
from cortex import Cortex
import asyncio

cortex = Cortex(client_id, client_secret, debug=False) # instantiate Cortex object - also opens WebSocket connection
await cortex.connect() # open connection and start recieving responses on event loop

res = await cortex.authorize(client_id, client_secret)
token = res['result']['cortexToken']
# make an authorization request to the Cortex API

await cortex.close() # closes the WebSocket connection
```

To call a different API method, simply replace _get_user_login_ with another method from the Cortex API [documentation](https://emotiv.gitbook.io/cortex-api/overview-of-api-flow), as well as its necessary parameters.

# Quick Documentation

To call and store the result of any function in the Cortex API:
```python
response = await cortex.[function_name](parameter_one=[value_one], parameter_two=[value_two])
result = response['result']
```
Replace _method_name_ with any method listed in the Cortex API [documentation](https://emotiv.gitbook.io/cortex-api/overview-of-api-flow), converted from _camelCase_ to _snake_case_.

## Important ⚠️

This is what the result variable would contain for an example API call (content of result **will** vary):
```json
{
  "cortexToken": "xxx",
  "message": "..."
}
```

## Error Handling
If the API call does not go through, your _result_ variable will instead contain an error with two fields:
```json
{
  "code": -32600,
  "message": "..."
}
```

## Warnings and Stream Data
You don't have to explicitly wait for warnings and stream data. Instead, Cortex and the event loop will constantly check for incoming responses with that information and send it to the user.

Here is an example warning:
```json
Warning received: {'jsonrpc': '2.0', 'warning': {'code': 142, 'message': {'behavior': 'Headset discovering complete.', 'headsetId': ''}}}
```

### Example

```python
from cortex import Cortex
import asyncio

class Cortex_Example:
  def __init__(...):
    self.cortex = Cortex(client_id, client_secret, debug=False)
    ...

  async def setup(self):
    res = await self.cortex.authorize(self.client_id, self.client_secret)
    self.token = res['result']['cortexToken']
    await self.cortex.control_device("refresh")
    res = await self.cortex.query_headsets()
    self.headset_id = res['result'][0]['id']
    await self.cortex.control_device("connect", self.headset_id)
  
  async def start_stream(self):
    res = await self.cortex.create_session(self.token, "active", self.headset_id)
    self.session_id = res['result']['id']
    await self.cortex.subscribe(self.token, self.session_id, ['pow'])
  
  async def stop_stream(self):
    await self.cortex.update_session(self.token, self.session_id, "close")
  
async def main():
  example = Cortex_Example(client_id, client_secret, debug=False)

  await example.cortex.connect()
  
  await example.setup()

  await example.start_stream()

  # some logic in between

  await example.stop_stream()

  await example.cortex.close()

asyncio.run(main())
```

# Key Changes
These are the key changes I made to the [cortex.py](https://github.com/jamesmcaleer/emotiv-dev-winter/tree/main/python-cortex-api-change-v1-threading/cortex.py) file from my [python-cortex-api-change-v1-threading](https://github.com/jamesmcaleer/emotiv-dev-winter/tree/main/python-cortex-api-change-v1-threading) directory, as well as the overall approach.

## **Adoption of `asyncio`**
The Python Cortex API now leverages Python's `asyncio` framework, enabling developers to use asynchronous functions throughout the library. This update provides more flexibility when integrating the API into event-driven applications.

#### Details:
- Previously synchronous methods were refactored to be asynchronous.
- All API functions can now be awaited, enabling non-blocking execution.

#### Example Usage:
```python
# Old usage (blocking call):
response = api.some_function(params)

# New usage (non-blocking with asyncio):
response = await api.some_function(params)
```

## async support for all Cortex API functions

In version 1, API calls were defined as such:
```python
def get_current_profile(self, cortex_token, headset_id):
  print('get current profile:')
  request = {
      "jsonrpc": "2.0",
      "method": "getCurrentProfile",
      "id": GET_CURRENT_PROFILE,
      "params": {
          "cortexToken": cortex_token,
          "headset": headset_id
      }
  }
  self.ws.send(json.dumps(request))
```

In this version, they instead look like this:

```python
async def get_current_profile(self, cortex_token, headset_id):
  print('get current profile')
  request = {
      "jsonrpc": "2.0",
      "method": "getCurrentProfile",
      "id": GET_CURRENT_PROFILE,
      "params": {
          "cortexToken": cortex_token,
          "headset": headset_id
      }
  }

  return await self.send_request(request)
```

## Conclusion

While this does not cover _every_ change I made to the library, it covers the fundamental changes I made while converting from synchronous to asynchronous.

I am thankful for the team at Emotiv for creating all of these tools as well as giving me the opportunity to learn more about how APIs and event-driven architecture work.

I hope that developers can find this rework useful for developing third-party Python applications with Emotiv EEG Headsets.






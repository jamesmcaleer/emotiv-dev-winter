# EMOTIV Winter Work Showcase

## Learning Cortex API

Over the winter, I spent time studying the Cortex API to learn all of the features and how each command works.

I implemented the commands in Python by working off of the EMOTIV provided [python](https://github.com/Emotiv/cortex-example/tree/master/python) Cortex API example.

## Cortex API Python lib update 1 (threading)

I made changes to the EMOTIV provided [cortex.py](https://github.com/Emotiv/cortex-example/blob/master/python/cortex.py) file to allow developers to control the flow of the application by simplifying API calls with threading.

The documentation, implementation, and demo for this is in the [python-cortex-api-change-v1-threading](https://github.com/jamesmcaleer/emotiv-dev-winter/tree/main/python-cortex-api-change-v1-threading) folder.

## Cortex API Python lib update 2 (async)

I then changed the updated [cortex.py](https://github.com/jamesmcaleer/emotiv-dev-winter/tree/main/python-cortex-api-change-v1-threading/cortex.py) file to work with the [asyncio](https://docs.python.org/3/library/asyncio.html) library.

The documentation, implementation, and demo for this is in the [python-cortex-api-change-v2-asyncio](https://github.com/jamesmcaleer/emotiv-dev-winter/tree/main/python-cortex-api-change-v2-asyncio) folder.

## Inner Voice (Cortex API Demo)

Finally, I created a React application called Inner Voice that gives speech insights from your brainwaves. It works by leveraging the Cortex API, specifically the [Performance Metrics](https://emotiv.gitbook.io/cortex-api/data-subscription/data-sample-object#performance-metric) data stream, to tell the speaker the emotions in which they delivered their speech.

Inner Voice is located in the [Inner Voice](https://github.com/jamesmcaleer/emotiv-dev-winter/tree/main/InnerVoice) directory.

The code for the [FastAPI](https://fastapi.tiangolo.com/) backend of Inner Voice is in the [backend](https://github.com/jamesmcaleer/emotiv-dev-winter/tree/main/InnerVoice/backend) folder.

The demo video is in my [LinkedIn Post](https://www.linkedin.com/feed/update/urn:li:activity:7286010756205064193/).

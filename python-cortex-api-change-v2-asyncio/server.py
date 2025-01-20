from fastapi import FastAPI, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import asyncio
import time

from cortex_handler import CortexHandler
from audio import webm_to_mp3, transcribe_to_chunks, metrics_on_chunks

@asynccontextmanager
async def lifespan(app: FastAPI):
    # before starts
    
    await cortex_handler.cortex.connect()
    yield
    await cortex_handler.cortex.close()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.post("/connect")
async def slash_connect():
    
    await cortex_handler.setup()

    return {'message': 'connection complete'}

@app.post("/start")
async def slash_start():
    await cortex_handler.start_stream()

    global start_time
    start_time = time.time()
    print('server stream start:', start_time)

    return {'message': 'stream started'}

@app.post("/stop")
async def slash_stop():
    
    await cortex_handler.stop_stream()
    
    stream_data = cortex_handler.cortex.stream_data

    global first_data_time
    first_data_time = stream_data[0]['time']

    return {'message': 'stream stopped'}

@app.post("/analyze")
async def slash_analyze(audio: UploadFile = File(...)):
    

    mp3 = await webm_to_mp3(audio)
    print('fdt', first_data_time)
    print('st', start_time)
    
    rel_first_data_time = first_data_time - start_time
    offset = 10 - rel_first_data_time
    print('offset', offset)

    
    stream_data = cortex_handler.cortex.stream_data

    # transcribe it
    transcribed_chunks = transcribe_to_chunks(mp3, offset, stream_data)
    print('transcribed chunks', transcribed_chunks)

    

    final_chunks = metrics_on_chunks(transcribed_chunks, stream_data)

    print('final chunks ----------')
    print(final_chunks)
    # align sentences from the transcription with these timestamped chunks

    # look at mental state at these timestamps in brainwave data

    # reset stream_data to allow for more records
    cortex_handler.cortex.stream_data = []

    # return a object with data about each chunk
    return {
        'message': 'analysis complete',
        'chunks': final_chunks
    }




client_id = 'vdKgSHlfEJillybmFxYQuGRhRu71cxRBaFzY4zQg'
client_secret =                                                                                                                                                 'ZlMnhrQGEelAALvY27FYFaf8COVOyXMcuGjscnzU0HbMBb66JP8ggsVfgqi00oFJ37QFSJN9fWtqZ2xCqt7Q5XSkhaKYw6TS6qc52T0w4IUm2Diukb62P2NYY16IK1Rk'
debug = True
cortex_handler = CortexHandler(client_id, client_secret, debug)

start_time = 0
first_data_time = 0

'''
{isRecording ? (
                <button className="stop-recording" onClick={handleStopRecording}>Stop Recording</button>
                ) : (
                <button 
                    className="start-recording" 
                    /*onClick={handleStartRecording}*/
                    style={{
                        backgroundColor: isRecording ? "red" : "grey",
                        cursor: isRecording ? "default" : "pointer",
                    }}
                    
                >
                    <img 
                        src={microphoneIcon} 
                        alt="record"
                        onClick={() => setIsRecording(true)}
                    />
                </button>
                )}
'''
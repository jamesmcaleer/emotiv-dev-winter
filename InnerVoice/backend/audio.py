import whisper
import ffmpeg
import os

whisper_model = whisper.load_model("tiny.en")

def delete_audio(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
        print(f"File deleted: {file_name}")
    else:
        print(f"File does not exist: {file_name}")

async def webm_to_mp3(audio):

    # take in a webm file
    # Access the file metadata
    print(f"Filename: {audio.filename}")
    print(f"Content Type: {audio.content_type}")
    
    # Read the file content
    file_content = await audio.read()
    print(f"File size: {len(file_content)} bytes")
    
    # save webm locally
    with open(f"audios/{audio.filename}", "wb") as f:
        f.write(file_content)

    # convert to mp3
    try:
        input_file = f"audios/{audio.filename}"
        output_file = input_file.split('.')[0]+'.mp3'
        ffmpeg.input(input_file).output(output_file, format='mp3', audio_bitrate='192k').run()
        print(f"Conversion successful! MP3 saved at: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error during conversion: {e.stderr.decode()}")
    
    # delete webm
    delete_audio(input_file)

    return output_file # name of mp3 file

def transcribe_to_chunks(mp3_file_name, offset, stream_data):
    result = whisper_model.transcribe(mp3_file_name, word_timestamps=True)
    delete_audio(mp3_file_name)
    
    segments = result['segments']
    words = []
    for segment in segments:
        for word in segment['words']:
            words.append(word)

    

    #print(words)
    #print('next-------')
    chunks = []
    for i in range(len(stream_data)):
        chunks.append({'text': ''})
    
    for word in words:
        index = int((word['start'] + offset)//10)
        try:
            chunks[index]['text'] += word['word']
        except Exception:
            chunks.append( {'text': word['word']} ) # chunk w/ no stream data
    
    for chunk in chunks:
        chunk['text'] = chunk['text'].strip() # get rid of first space

    return chunks



def metrics_on_chunks(chunks, stream_data):
    for i in range(len(stream_data)): # there can be more chunks than stream data, but not more stream data than chunks
        chunk = chunks[i] # ^ so the chunks w no stream data simply wont have a 'metric' field attached
        met_info = stream_data[i]['met']
        print('met info',met_info)

        ''' how its shown in the docs
        metrics = {
            'eng': met_info[1],
            'exc': met_info[3],
            'str': met_info[6],
            'rel': met_info[8],
            'int': met_info[10],
            'foc': met_info[12]
        }
        '''

        metrics = {
            'eng': met_info[3],
            'exc': met_info[5],
            'str': met_info[8],
            'rel': met_info[10],
            'int': met_info[12],
            'foc': met_info[1]
        }
        print('chunk', chunk['text'])
        print('metrics', metrics)
        
        max_met_name = ''
        max_met_val = 0.4
        for met in metrics.keys():
            if metrics[met] and metrics[met] > max_met_val:
                max_met_val = metrics[met]
                max_met_name = met
                print('new max', met, max_met_val)
        
        if max_met_name:
            chunk['metric'] = max_met_name
    
    return chunks
        
import websockets
import asyncio
import pathlib
from datetime import datetime
import json
import ssl
import time
import sys
import warnings


# define request id
GET_CORTEX_INFO = 1
GET_USER_LOGIN = 2
REQUEST_ACCESS = 3
HAS_ACCESS_RIGHT = 4
AUTHORIZE = 5
GENERATE_NEW_TOKEN = 6
GET_USER_INFORMATION = 7
GET_LICENSE_INFO = 8
CONTROL_DEVICE = 9
QUERY_HEADSETS = 10
UPDATE_HEADSET = 11
UPDATE_HEADSET_CUSTOM_INFO = 12
SYNC_WITH_HEADSET_CLOCK = 13
CREATE_SESSION = 14
UPDATE_SESSION = 15
QUERY_SESSIONS = 16
SUBSCRIBE = 17
UNSUBSCRIBE = 18
CREATE_RECORD = 19
STOP_RECORD = 20
UPDATE_RECORD = 21
DELETE_RECORDS = 22
EXPORT_RECORD = 23
QUERY_RECORDS = 24
GET_RECORD_INFOS = 25
CONFIG_OPT_OUT = 26
REQUEST_TO_DOWNLOAD_RECORD_DATA = 27
INJECT_MARKER = 28
UPDATE_MARKER = 29
CREATE_SUBJECT = 30
UPDATE_SUBJECT = 31
DELETE_SUBJECTS = 32
QUERY_SUBJECTS = 33
GET_DEMOGRAPHIC_ATTRIBUTES = 34
QUERY_PROFILE = 35
GET_CURRENT_PROFILE = 36
SETUP_PROFILE = 37
LOAD_GUEST_PROFILE = 38
GET_DETECTION_INFO = 39
TRAINING = 40
GET_TRAINED_SIGNATURE_ACTIONS = 41
GET_TRAINING_TIME = 42
FACIAL_EXPRESSION_SIGNATURE_TYPE = 43
FACIAL_EXPRESSION_THRESHOLD = 44
MENTAL_COMMAND_ACTIVE_ACTION = 45
MENTAL_COMMAND_BRAIN_MAP = 46
MENTAL_COMMAND_GET_SKILL_RATING = 47
MENTAL_COMMAND_TRAINING_THRESHOLD = 48
MENTAL_COMMAND_ACTION_SENSITIVITY = 49

#define error_code
ERR_PROFILE_ACCESS_DENIED = -32046

# define warning code
CORTEX_STOP_ALL_STREAMS = 0
CORTEX_CLOSE_SESSION = 1
USER_LOGIN = 2
USER_LOGOUT = 3
ACCESS_RIGHT_GRANTED = 9
ACCESS_RIGHT_REJECTED = 10
PROFILE_LOADED = 13
PROFILE_UNLOADED = 14
CORTEX_AUTO_UNLOAD_PROFILE = 15
EULA_ACCEPTED = 17
DISKSPACE_LOW = 19
DISKSPACE_CRITICAL = 20
CORTEX_RECORD_POST_PROCESSING_DONE = 30
HEADSET_CANNOT_CONNECT_TIMEOUT = 102
HEADSET_DISCONNECTED_TIMEOUT = 103
HEADSET_CONNECTED = 104
HEADSET_CANNOT_WORK_WITH_BTLE = 112
HEADSET_CANNOT_CONNECT_DISABLE_MOTION = 113
HEADSET_SCANNING_FINISHED = 142


class Cortex:
    def __init__(self, client_id, client_secret, debug_mode=False, debit=0, **kwargs):

        self.debug = debug_mode
        self.debit = debit
        self.ws = None
        self.receiver = None
        self.pending_futures = {}

        self.stream_data = []
        

        if client_id == '':
            raise ValueError('Empty client_id. Please fill in client_id before running.')
        else:
            self.client_id = client_id

        if client_secret == '':
            raise ValueError('Empty client_secret. Please fill in client_secret before running.')
        else:
            self.client_secret = client_secret
    
    async def on_message(self, message):
        print(f"Message received: {message}")
    
    async def on_error(self, error):
        print(f"Error: {error}")
    
    async def on_close(self):
        print("WebSocket closed")
    
    async def on_open(self):
        print("WebSocket opened")
    
    async def open(self):
        url = "wss://localhost:6868"
        
        # Set SSL options
        #sslopt = {'cert_reqs': ssl.CERT_NONE}
        #sslopt = {'ca_certs': "certificates/rootCA.pem", "cert_reqs": ssl.CERT_REQUIRED}
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        
        # Load the default trusted certificates (e.g., system CA certificates)
        ssl_context.load_default_certs()

        # If you only have the certificate (no private key), you can load the cert only for verification
        ssl_context.load_verify_locations(pathlib.Path("certificates/rootCA.pem"))

        self.ws = await websockets.connect(url, ssl=ssl_context)
        print('ws open')

    async def connect(self):
        await self.open()
        self.start_receiver()

    async def close(self):
        if self.ws:
            self.stop_receiver_task()
            await self.ws.close()
            print('ws closed')

    def start_receiver(self):
        """Start the receive_messages task."""
        if not self.receiver or self.receiver.done():
            self.stop_receiver = False  # Reset the stop flag
            self.receiver = asyncio.create_task(self.receive_ws())

    def stop_receiver_task(self):
        """Signal the receiver task to stop."""
        self.stop_receiver = True
        if self.receiver:
            self.receiver.cancel()

    async def receive_ws(self):
        while True:
            response = json.loads(await self.ws.recv())
            
            try:
                if response['id']:
                    response_id = response['id']
                else:
                    response_id = None
            except Exception:
                response_id = None

            if response_id and response_id in self.pending_futures:
                if self.debug:
                    print(f"Response received: {response}")
                self.pending_futures[response_id].set_result(response)
                del self.pending_futures[response_id]
            elif response.get('warning'):
                print(f"Warning received: {response}")
            else:
                print(f"Stream data received: {response}")
                self.stream_data.append(response)

    
    # REQ FUNCTIONS ---------------
    # sections will match those listen in the Cortex API Documentation 
    
    async def send_request(self, request):
        """Send a request and return the Future that will hold the response."""
        request_id = request["id"]
        future = asyncio.get_event_loop().create_future()
        self.pending_futures[request_id] = future

        # Send the request
        if self.debug:
            print("Sending request:", json.dumps(request, indent=4))
        await self.ws.send(json.dumps(request))

        if self.debug:
            print('request sent')

        try:
            response = await future  # This will block until the response is received
            return response
        except asyncio.CancelledError:
            print(f"Request with ID {request_id} was cancelled")
            raise
        finally:
            # Cleanup pending future to avoid memory leaks
            self.pending_futures.pop(request_id, None)

        '''
        response = json.loads(await self.ws.recv())

        if self.debug:
            print('incoming response:', response)
        while response['id'] != request_id:
 
            response = json.loads(await self.ws.recv())
 
            print('incoming response:', response)
        
        return response
        '''

    # AUTHENTICATION - https://emotiv.gitbook.io/cortex-api/authentication

    async def get_cortex_info(self):
        print('get cortex info --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getCortexInfo",
            "id":GET_CORTEX_INFO
        }

        return await self.send_request(request)
    
    async def get_user_login(self):
        print('get user login --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getUserLogin",
            "id":GET_USER_LOGIN
        }

        return await self.send_request(request)

    async def request_access(self, client_id, client_secret):
        print('request access --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "requestAccess",
            "id": REQUEST_ACCESS,
            "params": {
                "clientId": client_id, 
                "clientSecret": client_secret
            }
        }

        return await self.send_request(request)
    
    async def has_access_right(self, client_id, client_secret):
        print('has access right --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "hasAccessRight",
            "id": HAS_ACCESS_RIGHT,
            "params": {
                "clientId": client_id, 
                "clientSecret": client_secret
            }
        }

        return await self.send_request(request)
    
    async def authorize(self, client_id, client_secret):
        print('authorize --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "authorize",
            "id": AUTHORIZE,
            "params": {
                "clientId": client_id, 
                "clientSecret": client_secret
            }
        }

        return await self.send_request(request)

    async def generate_new_token(self, cortex_token, client_id, client_secret):
        print('generate new token --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "generateNewToken",
            "id": GENERATE_NEW_TOKEN,
            "params": {
                "cortexToken": cortex_token,
                "clientId": client_id, 
                "clientSecret": client_secret
            }
        }
        
        return await self.send_request(request)
    
    async def get_user_information(self, cortex_token):
        print('get user information --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getUserInformation",
            "id": GET_USER_INFORMATION,
            "params": {
                "cortexToken": cortex_token
            }
        }

        return await self.send_request(request)

    async def get_license_info(self, cortex_token):
        print('get license info --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getLicenseInfo",
            "id": GET_LICENSE_INFO,
            "params": {
                "cortexToken": cortex_token
            }
        }

        return await self.send_request(request)

    # HEADSETS - https://emotiv.gitbook.io/cortex-api/headset

    async def control_device(self, command, headset_id=None):
        print('control device --------------------------------')

        request = {
            "jsonrpc": "2.0",
            "method": "controlDevice",
            "id": CONTROL_DEVICE,
            "params": {
                "command": command
            }
        }

        if headset_id:
            request["params"]["headset"] = headset_id

        return await self.send_request(request)

    async def query_headsets(self, headset_id=None):
        print('query headsets --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "queryHeadsets",
            "id": QUERY_HEADSETS
        }

        if headset_id:
            request["params"] = { "id": headset_id }

        return await self.send_request(request)

    # come back when need to make epoc accessible
    async def update_headset(self):
        print('update headset --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "updateHeadset",
            "id": UPDATE_HEADSET,
            "params": {}
        }

        return await self.send_request(request)

    async def update_headset_custom_info(self):
        print('update headset custom info --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "updateHeadsetCustomInfo",
            "id": UPDATE_HEADSET_CUSTOM_INFO,
            "params": {}
        }

        return await self.send_request(request)

    async def sync_with_headset_clock(self, headset_id, monotonic_time, system_time):
        print('sync with headset clock --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "syncWithHeadsetClock",
            "id": SYNC_WITH_HEADSET_CLOCK,
            "params": {
                "headset": headset_id,
                "monotonicTime": monotonic_time,
                "systemTime": system_time
            }
        }

        return await self.send_request(request)

    # SESSIONS - https://emotiv.gitbook.io/cortex-api/session

    async def create_session(self, cortex_token, status, headset_id=None):
        print('create session --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "createSession",
            "id": CREATE_SESSION,
            "params": {
                "cortexToken": cortex_token,
                "status": status
            }
        }

        if headset_id:
            request["params"]["headset"] = headset_id
        else:
            request["params"]["headset"] = ""

        return await self.send_request(request)

    async def update_session(self, cortex_token, session_id, status):
        print('update session --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "updateSession",
            "id": UPDATE_SESSION,
            "params": {
                "cortexToken": cortex_token,
                "session": session_id,
                "status": status
            }
        }

        return await self.send_request(request)

    async def query_sessions(self, cortex_token):
        print('query sessions --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "querySessions",
            "id": QUERY_SESSIONS,
            "params": {
                "cortexToken": cortex_token
            }
        }

        return await self.send_request(request)

    # DATA SUBSCRIPTION - https://emotiv.gitbook.io/cortex-api/data-subscription

    async def subscribe(self, cortex_token, session_id, streams):
        print('subscribe --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "subscribe",
            "id": SUBSCRIBE,
            "params": {
                "cortexToken": cortex_token,
                "session": session_id,
                "streams": streams
            }
        }

        return await self.send_request(request)

    async def unsubscribe(self, cortex_token, session_id, streams):
        print('unsubscribe --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "unsubscribe",
            "id": UNSUBSCRIBE,
            "params": {
                "cortexToken": cortex_token,
                "session": session_id,
                "streams": streams
            }
        }

        return await self.send_request(request)

    # RECORDS - https://emotiv.gitbook.io/cortex-api/records

    async def create_record(self, cortex_token, session_id, title, **kwargs):
        print('create record --------------------------------')

        if (len(title) == 0):
            warnings.warn('Empty record_title. Please fill the record_title before running script.')
            return

        params_val = {"cortexToken": cortex_token, "session": session_id, "title": title}

        for key, value in kwargs.items():
            params_val.update({key: value})

        request = {
            "jsonrpc": "2.0", 
            "method": "createRecord",
            "params": params_val, 
            "id": CREATE_RECORD
        }

        return await self.send_request(request)

    async def stop_record(self, cortex_token, session_id):
        print('stop record --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "stopRecord",
            "id": STOP_RECORD,
            "params": {
                "cortexToken": cortex_token,
                "session": session_id
            }
        }

        return await self.send_request(request)

    async def update_record(self, cortex_token, record_id, title, **kwargs):
        print('update record --------------------------------')

        if (len(title) == 0):
            warnings.warn('Empty record_title. Please fill the record_title before running script.')
            return

        params_val = {"cortexToken": cortex_token, "record": record_id, "title": title}

        for key, value in kwargs.items():
            params_val.update({key: value})

        request = {
            "jsonrpc": "2.0",
            "method": "updateRecord",
            "id": UPDATE_RECORD,
            "params": params_val
        }

        return await self.send_request(request)

    async def delete_record(self, cortex_token, record_ids):
        print('delete record --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "deleteRecord",
            "id": DELETE_RECORD,
            "params": {
                "cortexToken": cortex_token,
                "records": record_ids
            }
        }

        return await self.send_request(request)

    async def export_record(self, cortex_token, folder, stream_types, export_format, record_ids, version, **kwargs):
        print('export record --------------------------------: ')
        #validate destination folder
        if (len(folder) == 0):
            warnings.warn('Invalid folder parameter. Please set a writable destination folder for exporting data.')
            return

        params_val = {"cortexToken": cortex_token, 
                      "folder": folder,
                      "format": export_format,
                      "streamTypes": stream_types,
                      "recordIds": record_ids}

        if export_format == 'CSV':
            params_val.update({'version': version})

        for key, value in kwargs.items():
            params_val.update({key: value})

        request = {
            "jsonrpc": "2.0",
            "id": EXPORT_RECORD,
            "method": "exportRecord", 
            "params": params_val
        }

        return await self.send_request(request)

    async def query_records(self, cortex_token, query, order_by, **kwargs):
        print('query records --------------------------------')

        params_val = {
            "cortexToken": cortex_token,
            "query": query,
            "orderBy": order_by
        }

        for key, value in kwargs.items():
            params_val.update({key: value})

        request = {
            "jsonrpc": "2.0",
            "method": "queryRecords",
            "id": QUERY_RECORDS,
            "params": params_val
        }

        return await self.send_request(request)

    async def get_record_infos(self, cortex_token, record_ids):
        print('get record infos --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getRecordInfos",
            "id": GET_RECORD_INFOS,
            "params": {
                "cortexToken": cortex_token,
                "recordIds": record_ids
            }
        }

        return await self.send_request(request)

    # come back to this
    async def config_opt_out(self):
        print('config opt out --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "configOptOut",
            "id": CONFIG_OPT_OUT,
            "params": {}
        }

        return await self.send_request(request)

    async def request_to_download_record_data(self, cortex_token, record_ids):
        print('request to download record data --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "requestToDownloadRecordData",
            "id": REQUEST_TO_DOWNLOAD_RECORD_DATA,
            "params": {
                "cortexToken": cortex_token,
                "recordIds": record_ids
            }
        }

        return await self.send_request(request)
    
    # MARKERS - https://emotiv.gitbook.io/cortex-api/markers

    async def inject_marker(self, cortex_token, session_id, time, value, label, **kwargs):
        print('inject marker --------------------------------')

        params_val = {
            "cortexToken": cortex_token,
            "session": session_id,
            "time": time,
            "value": value,
            "label": label
        }

        for key, value in kwargs.items():
            params_val.update({key: value})

        request = {
            "jsonrpc": "2.0",
            "method": "injectMarker",
            "id": INJECT_MARKER,
            "params": params_val
        }

        return await self.send_request(request)

    async def update_marker(self, cortex_token, session_id, marker_id, time, **kwargs):
        print('update marker --------------------------------')
        params_val = {
            "cortexToken": cortex_token,
            "session": session_id,
            "markerId": marker_id,
            "time": time
        }

        for key, value in kwargs.items():
            params_val.update({key: value})

        request = {
            "jsonrpc": "2.0",
            "method": "updateMarker",
            "id": UPDATE_MARKER,
            "params": params_val
        }

        return await self.send_request(request)

    # SUBJECTS - https://emotiv.gitbook.io/cortex-api/subjects

    async def create_subject(self, cortex_token, subject_name, **kwargs):
        print('create subject --------------------------------')

        params_val = {
            "cortexToken": cortex_token,
            "subjectName": subject_name
        }

        for key, value in kwargs.items():
            params_val.update({key: value})

        request = {
            "jsonrpc": "2.0",
            "method": "createSubject",
            "id": CREATE_SUBJECT,
            "params": params_val
        }

        return await self.send_request(request)

    async def update_subject(self, cortex_token, subject_name, **kwargs):
        print('update subject --------------------------------')

        params_val = {
            "cortexToken": cortex_token,
            "subjectName": subject_name
        }

        for key, value in kwargs.items():
            params_val.update({key: value})

        request = {
            "jsonrpc": "2.0",
            "method": "updateSubject",
            "id": UPDATE_SUBJECT,
            "params": params_val
        }

        return await self.send_request(request)

    async def delete_subjects(self, cortex_token, subject_names):
        print('delete subjects --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "deleteSubjects",
            "id": DELETE_SUBJECTS,
            "params": {
                "cortexToken": cortex_token,
                "subjects": subject_names
            }
        }

        return await self.send_request(request)

    async def query_subjects(self, cortex_token, query, order_by, **kwargs):
        print('query subjects --------------------------------')

        params_val = {
            "cortexToken": cortex_token,
            "query": query,
            "orderBy": order_by
        }

        for key, value in kwargs.items():
            params_val.update({key: value})

        request = {
            "jsonrpc": "2.0",
            "method": "querySubjects",
            "id": QUERY_SUBJECTS,
            "params": params_val
        }

        return await self.send_request(request)

    async def get_demographic_attributes(self, cortex_token):
        print('get demographic attributes --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getDemographicAttributes",
            "id": GET_DEMOGRAPHIC_ATTRIBUTES,
            "params": {
                "cortexToken": cortex_token
            }
        }

        return await self.send_request(request)

    # BCI - https://emotiv.gitbook.io/cortex-api/bci
    
    async def query_profile(self, cortex_token):
        print('query profile --------------------------------')

        request = {
            "jsonrpc": "2.0",
            "method": "queryProfile",
            "id": QUERY_PROFILE,
            "params": {
                "cortexToken": cortex_token
            }
        }

        return await self.send_request(request)

    async def get_current_profile(self, cortex_token, headset_id):
        print('get current profile --------------------------------')
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

    # come back to this
    async def setup_profile(self):
        print('setup profile --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "setupProfile",
            "id": SETUP_PROFILE,
            "params": {

            }
        }

        return await self.send_request(request)

    async def load_guest_profile(self, cortex_token, headset_id):
        print('load guest profile --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "loadGuestProfile",
            "id": LOAD_GUEST_PROFILE,
            "params": {
                "cortexToken": cortex_token,
                "headset": headset_id
            }
        }

        return await self.send_request(request)

    async def get_detection_info(self, detection):
        print('get detection info --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getDetectionInfo",
            "id": GET_DETECTION_INFO,
            "params": {
                "detection": detection
            }
        }

        return await self.send_request(request)

    async def training(self, cortex_token, session_id, detection, status, action):
        print('training --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "training",
            "id": TRAINING,
            "params": {
                "cortexToken": cortex_token,
                "session": session_id,
                "detection": detection,
                "status": status,
                "action": action
            }
        }

        return await self.send_request(request)
    
    # ADVANCED BCI - https://emotiv.gitbook.io/cortex-api/advanced-bci

    async def get_trained_signature_actions(self):
        print('get trained signature actions --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getTrainedSignatureActions",
            "id": GET_TRAINED_SIGNATURE_ACTIONS,
            "params": {

            }
        }

        return await self.send_request(request)

    async def get_training_time(self):
        print('get training time --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getTrainingTime",
            "id": GET_TRAINING_TIME,
            "params": {

            }
        }

        return await self.send_request(request)

    async def facial_expression_signature_type(self):
        print('facial expression signature type --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "facialExpressionSignatureType",
            "id": FACIAL_EXPRESSION_SIGNATURE_TYPE,
            "params": {

            }
        }

        return await self.send_request(request)

    async def facial_expression_threshold(self):
        print('facial expression threshold --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "facialExpressionThreshold",
            "id": FACIAL_EXPRESSION_THRESHOLD,
            "params": {

            }
        }

        return await self.send_request(request)

    async def mental_command_active_action(self):
        print('mental command active action --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "mentalCommandActiveAction",
            "id": MENTAL_COMMAND_ACTIVE_ACTION,
            "params": {

            }
        }

        return await self.send_request(request)

    async def mental_command_brain_map(self):
        print('mental command brain map --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "mentalCommandBrainMap",
            "id": MENTAL_COMMAND_BRAIN_MAP,
            "params": {

            }
        }

        return await self.send_request(request)

    async def mental_command_get_skill_rating(self):
        print('mental command get skill rating --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "mentalCommandGetSkillRating",
            "id": MENTAL_COMMAND_GET_SKILL_RATING,
            "params": {

            }
        }

        return await self.send_request(request)

    async def mental_command_training_threshold(self):
        print('mental command training threshold --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "mentalCommandTrainingThreshold",
            "id": MENTAL_COMMAND_TRAINING_THRESHOLD,
            "params": {

            }
        }

        return await self.send_request(request)

    async def mental_command_action_sensitivity(self):
        print('mental command action sensitivity --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "mentalCommandActionSensitivity",
            "id": MENTAL_COMMAND_ACTION_SENSITIVITY,
            "params": {

            }
        }

        return await self.send_request(request)

    # END OF REQ FUNCTIONS ----- ^


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------

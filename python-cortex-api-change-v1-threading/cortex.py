import websocket #'pip install websocket-client' for install
from datetime import datetime
import json
import ssl
import time
import sys
from pydispatch import Dispatcher
import warnings
import threading


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

REQUEST_TO_EMIT = {
    GET_CORTEX_INFO: 'get_cortex_info_done',
    GET_USER_LOGIN: 'get_user_login_done',
    REQUEST_ACCESS: 'request_access_done',
    HAS_ACCESS_RIGHT: 'has_access_right_done',
    AUTHORIZE: 'authorize_done',
    GENERATE_NEW_TOKEN: 'generate_new_token_done',
    GET_USER_INFORMATION: 'get_user_information_done',
    GET_LICENSE_INFO: 'get_license_info_done',
    CONTROL_DEVICE: 'control_device_done',
    QUERY_HEADSETS: 'query_headsets_done',
    UPDATE_HEADSET: 'update_headset_done',
    UPDATE_HEADSET_CUSTOM_INFO: 'update_headset_custom_info_done',
    SYNC_WITH_HEADSET_CLOCK: 'sync_with_headset_clock_done',
    CREATE_SESSION: 'create_session_done',
    UPDATE_SESSION: 'update_session_done',
    QUERY_SESSIONS: 'query_sessions_done',
    SUBSCRIBE: 'subscribe_done',
    UNSUBSCRIBE: 'unsubscribe_done',
    CREATE_RECORD: 'create_record_done',
    STOP_RECORD: 'stop_record_done',
    UPDATE_RECORD: 'update_record_done',
    DELETE_RECORDS: 'delete_records_done',
    EXPORT_RECORD: 'export_record_done',
    QUERY_RECORDS: 'query_records_done',
    GET_RECORD_INFOS: 'get_record_infos_done',
    CONFIG_OPT_OUT: 'config_opt_out_done',
    REQUEST_TO_DOWNLOAD_RECORD_DATA: 'request_to_download_record_data_done',
    INJECT_MARKER: 'inject_marker_done',
    UPDATE_MARKER: 'update_marker_done',
    CREATE_SUBJECT: 'create_subject_done',
    UPDATE_SUBJECT: 'update_subject_done',
    DELETE_SUBJECTS: 'delete_subjects_done',
    QUERY_SUBJECTS: 'query_subjects_done',
    GET_DEMOGRAPHIC_ATTRIBUTES: 'get_demographic_attributes_done',
    QUERY_PROFILE: 'query_profile_done',
    GET_CURRENT_PROFILE: 'get_current_profile_done',
    SETUP_PROFILE: 'setup_profile_done',
    LOAD_GUEST_PROFILE: 'load_guest_profile_done',
    GET_DETECTION_INFO: 'get_detection_info_done',
    TRAINING: 'training_done',
    GET_TRAINED_SIGNATURE_ACTIONS: 'get_trained_signature_actions_done',
    GET_TRAINING_TIME: 'get_training_time_done',
    FACIAL_EXPRESSION_SIGNATURE_TYPE: 'facial_expression_signature_type_done',
    FACIAL_EXPRESSION_THRESHOLD: 'facial_expression_threshold_done',
    MENTAL_COMMAND_ACTIVE_ACTION: 'mental_command_active_action_done',
    MENTAL_COMMAND_BRAIN_MAP: 'mental_command_brain_map_done',
    MENTAL_COMMAND_GET_SKILL_RATING: 'mental_command_get_skill_rating_done',
    MENTAL_COMMAND_TRAINING_THRESHOLD: 'mental_command_training_threshold_done',
    MENTAL_COMMAND_ACTION_SENSITIVITY: 'mental_command_action_sensitivity_done'
}

WARNING_TO_EMIT = {
    CORTEX_STOP_ALL_STREAMS: 'cortex_stop_all_streams_warning',
    CORTEX_CLOSE_SESSION: 'cortex_close_session_warning',
    USER_LOGIN: 'user_login_warning',
    USER_LOGOUT: 'user_logout_warning',
    ACCESS_RIGHT_GRANTED: 'access_right_granted_warning',
    ACCESS_RIGHT_REJECTED: 'access_right_rejected_warning',
    PROFILE_LOADED: 'profile_loaded_warning',
    PROFILE_UNLOADED: 'profile_unloaded_warning',
    CORTEX_AUTO_UNLOAD_PROFILE: 'cortex_auto_unload_profile_warning',
    EULA_ACCEPTED: 'eula_accpeted_warning',
    DISKSPACE_LOW: 'diskspace_low_warning',
    DISKSPACE_CRITICAL: 'diskspace_critical_warning',
    CORTEX_RECORD_POST_PROCESSING_DONE: 'cortex_record_post_processing_done_warning',
    HEADSET_CANNOT_CONNECT_TIMEOUT: 'headset_cannot_connected_timeout_warning',
    HEADSET_DISCONNECTED_TIMEOUT: 'headset_disconnected_timeout_warning',
    HEADSET_CONNECTED: 'headset_connected_warning',
    HEADSET_CANNOT_WORK_WITH_BTLE: 'headset_cannot_work_with_blte_warning',
    HEADSET_CANNOT_CONNECT_DISABLE_MOTION: 'headset_cannot_connect_disable_motion_warning',
    HEADSET_SCANNING_FINISHED: 'headset_scanning_finished_warning'
}

class Cortex(Dispatcher):

    _events_ = [
    'inform_error', 'ws_open',
    
    # API EVENTS
    'get_cortex_info_done', 'get_user_login_done', 'request_access_done', 'has_access_right_done', 'authorize_done', 'generate_new_token_done', 
    'get_user_information_done', 'get_license_info_done', 'control_device_done', 'query_headsets_done', 'update_headset_done', 
    'update_headset_custom_info_done', 'sync_with_headset_clock_done', 'create_session_done', 'update_session_done', 'query_sessions_done', 
    'subscribe_done', 'unsubscribe_done', 'create_record_done', 'stop_record_done', 'update_record_done', 'delete_records_done', 
    'export_record_done', 'query_records_done', 'get_record_infos_done', 'config_opt_out_done', 'request_to_download_record_data_done', 
    'inject_marker_done', 'update_marker_done', 'create_subject_done', 'update_subject_done', 'delete_subjects_done', 'query_subjects_done', 
    'get_demographic_attributes_done', 'query_profile_done', 'get_current_profile_done', 'setup_profile_done', 'load_guest_profile_done', 
    'get_detection_info_done', 'training_done', 'get_trained_signature_actions_done', 'get_training_time_done', 
    'facial_expression_signature_type_done', 'facial_expression_threshold_done', 'mental_command_active_action_done', 'mental_command_brain_map_done', 
    'mental_command_get_skill_rating_done', 'mental_command_training_threshold_done', 'mental_command_action_sensitivity_done', 
    
    # WARNING EVENTS
    'cortex_stop_all_streams_warning', 'cortex_close_session_warning', 'user_login_warning', 'user_logout_warning', 'access_right_granted_warning', 
    'access_right_rejected_warning', 'profile_loaded_warning', 'profile_unloaded_warning', 'cortex_auto_unload_profile_warning', 
    'eula_accpeted_warning', 'diskspace_low_warning', 'diskspace_critical_warning', 'cortex_record_post_processing_done_warning', 
    'headset_cannot_connected_timeout_warning', 'headset_disconnected_timeout_warning', 'headset_connected_warning', 
    'headset_cannot_work_with_blte_warning', 'headset_cannot_connect_disable_motion_warning', 'headset_scanning_finished_warning',
    
    # STREAM EVENTS
    'new_data_labels', 'new_com_data', 'new_fe_data', 'new_eeg_data', 'new_mot_data', 'new_dev_data', 'new_eq_data', 'new_met_data', 'new_pow_data', 'new_sys_data'
    ]



    def __init__(self, client_id, client_secret, debug_mode=False, debit=0, **kwargs):

        self.api_events = ['inform_error', 'get_cortex_info_done', 'get_user_login_done', 'request_access_done', 'has_access_right_done', 'authorize_done', 'generate_new_token_done', 
        'get_user_information_done', 'get_license_info_done', 'control_device_done', 'query_headsets_done', 'update_headset_done', 
        'update_headset_custom_info_done', 'sync_with_headset_clock_done', 'create_session_done', 'update_session_done', 'query_sessions_done', 
        'subscribe_done', 'unsubscribe_done', 'create_record_done', 'stop_record_done', 'update_record_done', 'delete_records_done', 
        'export_record_done', 'query_records_done', 'get_record_infos_done', 'config_opt_out_done', 'request_to_download_record_data_done', 
        'inject_marker_done', 'update_marker_done', 'create_subject_done', 'update_subject_done', 'delete_subjects_done', 'query_subjects_done', 
        'get_demographic_attributes_done', 'query_profile_done', 'get_current_profile_done', 'setup_profile_done', 'load_guest_profile_done', 
        'get_detection_info_done', 'training_done', 'get_trained_signature_actions_done', 'get_training_time_done', 
        'facial_expression_signature_type_done', 'facial_expression_threshold_done', 'mental_command_active_action_done', 'mental_command_brain_map_done', 
        'mental_command_get_skill_rating_done', 'mental_command_training_threshold_done', 'mental_command_action_sensitivity_done']

        self.warning_events = ['cortex_stop_all_streams_warning', 'cortex_close_session_warning', 'user_login_warning', 'user_logout_warning', 'access_right_granted_warning', 
        'access_right_rejected_warning', 'profile_loaded_warning', 'profile_unloaded_warning', 'cortex_auto_unload_profile_warning', 
        'eula_accpeted_warning', 'diskspace_low_warning', 'diskspace_critical_warning', 'cortex_record_post_processing_done_warning', 
        'headset_cannot_connected_timeout_warning', 'headset_disconnected_timeout_warning', 'headset_connected_warning', 
        'headset_cannot_work_with_blte_warning', 'headset_cannot_connect_disable_motion_warning', 'headset_scanning_finished_warning']

        self.stream_events = ['new_data_labels', 'new_com_data', 'new_fe_data', 'new_eeg_data', 'new_mot_data', 'new_dev_data', 'new_met_data', 'new_pow_data', 'new_sys_data']

        self.debug = debug_mode
        self.debit = debit
        

        if client_id == '':
            raise ValueError('Empty client_id. Please fill in client_id before running.')
        else:
            self.client_id = client_id

        if client_secret == '':
            raise ValueError('Empty client_secret. Please fill in client_secret before running.')
        else:
            self.client_secret = client_secret
        
        self.bind(ws_open=self.on_ws_open)
        self.ws_ready_event = threading.Event()

        self.open()

        self.ws_ready_event.wait()
        print("WebSocket connection established. Proceeding...")

        self.current_result = None
        self.response_event = threading.Event()

        for event in self.api_events:
            self.bind(**{event: self.on_request_done})

        self.current_warning = None
        self.warning_event = threading.Event()

        for event in self.warning_events:
            self.bind(**{event: self.on_warning_done})

        self.current_stream_data = None
        self.stream_event = threading.Event()

        for event in self.stream_events:
            self.bind(**{event: self.on_stream_done})

    def open(self):
        url = "wss://localhost:6868"
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(url, 
                                        on_message=self.on_message,
                                        on_open = self.on_open,
                                        on_error=self.on_error,
                                        on_close=self.on_close)
        threadName = "WebsockThread:-{:%Y%m%d%H%M%S}".format(datetime.utcnow())
        
        # As default, a Emotiv self-signed certificate is required.
        # If you don't want to use the certificate, please replace by the below line  by sslopt={"cert_reqs": ssl.CERT_NONE}
        #sslopt={"cert_reqs": ssl.CERT_NONE}
        sslopt = {'ca_certs': "certificates/rootCA.pem", "cert_reqs": ssl.CERT_REQUIRED}

        self.websock_thread = threading.Thread(target=self.ws.run_forever, args=(None, sslopt), name=threadName)
        self.websock_thread.daemon = True
        self.websock_thread.start()
        #self.websock_thread.join() - this is blocking flow of rest of my programs
        

    def close(self):
        print("WebSocket connection closing...")
        self.ws.close()

    # LOCAL EVENT HANDLING ----------
    def on_ws_open(self, *args, **kwargs):
        """Handle WebSocket open event."""
        print("WebSocket is ready in Receiver")
        self.ws_ready_event.set()  # Signal that the WebSocket is ready

    def on_request_done(self, result_dic):
        self.current_result = result_dic
        self.response_event.set()  # Signal that the response is ready

    def on_warning_done(self, warning_dic):
        self.current_warning = warning_dic
        self.warning_event.set() 
    
    def on_stream_done(self, data):
        self.current_stream_data = data
        self.stream_event.set() 

    def await_response(self, api_call, **kwargs):
        self.response_event.clear()  # Reset the event
        api_call(**kwargs)  # Call the provided API function
        self.response_event.wait()  # Wait for the corresponding event
        result_dic = self.current_result

        expected_event = api_call.__name__ + '_done'
        #print(f"Data received for {expected_event}: {result_dic}")
        return result_dic

    def await_warning(self, **kwargs):
        self.warning_event.clear()  # Reset the event

        self.warning_event.wait()  # Wait for the corresponding event
        warning_dic = self.current_warning

        return warning_dic

    def await_stream_data(self, **kwargs):
        self.stream_event.clear()  # Reset the event

        self.stream_event.wait()  # Wait for the corresponding event
        data = self.current_stream_data

        return data

    # WEBSOCKET EVENTS ----------

    def on_message(self, *args):
        res_dic = json.loads(args[1])
        if 'sid' in res_dic:
            self.emit_stream_data(res_dic)
        elif 'result' in res_dic:
            self.emit_result(res_dic)
        elif 'error' in res_dic:
            self.emit_error(res_dic)
        elif 'warning' in res_dic:
            self.emit_warning(res_dic['warning'])
        else:
            raise KeyError

    def on_open(self, *args, **kwargs):
        print("websocket opened")

        self.emit("ws_open")
        #self.do_prepare_steps() ## THIS TRIGGERS THE EVENTS

    def on_error(self, *args):
        if len(args) == 2:
            print('on_error', str(args[1]))

    def on_close(self, *args, **kwargs):
        print("WebSocket connection closed.")
    
    # END OF WEBSOCKET EVENTS --- ^

    # EMITTERS -----------------

    def emit_result(self, res_dic):
        # lets just get the result and emit it
        if self.debug:
            print('res_dic:', res_dic)

        req_id = res_dic['id']
        result_dic = res_dic['result']

        self.emit(REQUEST_TO_EMIT[req_id], result_dic)

    def emit_error(self, res_dic):
        req_id = res_dic['id']
        print('emit_error: request Id ' + str(req_id))
        result_dic = res_dic['error']
        self.emit('inform_error', result_dic)
    
    def emit_warning(self, warning_dic):

        if self.debug:
            print(warning_dic)

        self.emit(WARNING_TO_EMIT[warning_dic['code']], warning_dic)

    def emit_stream_data(self, result_dic):
        
        if result_dic.get('com') != None:
            com_data = {}
            com_data['act'] = result_dic['com'][0]
            com_data['pow'] = result_dic['com'][1]
            com_data['time'] = result_dic['time']
            self.emit('new_com_data', data=com_data)
        elif result_dic.get('fac') != None:
            fe_data = {}
            fe_data['eyeAct'] = result_dic['fac'][0]    #eye action
            fe_data['uAct'] = result_dic['fac'][1]      #upper action
            fe_data['uPow'] = result_dic['fac'][2]      #upper action power
            fe_data['lAct'] = result_dic['fac'][3]      #lower action
            fe_data['lPow'] = result_dic['fac'][4]      #lower action power
            fe_data['time'] = result_dic['time']
            self.emit('new_fe_data', data=fe_data)
        elif result_dic.get('eeg') != None:
            eeg_data = {}
            eeg_data['eeg'] = result_dic['eeg']
            eeg_data['eeg'].pop() # remove markers
            eeg_data['time'] = result_dic['time']
            self.emit('new_eeg_data', data=eeg_data)
        elif result_dic.get('mot') != None:
            mot_data = {}
            mot_data['mot'] = result_dic['mot']
            mot_data['time'] = result_dic['time']
            self.emit('new_mot_data', data=mot_data)
        elif result_dic.get('dev') != None:
            dev_data = {}
            dev_data['signal'] = result_dic['dev'][1]
            dev_data['dev'] = result_dic['dev'][2]
            dev_data['batteryPercent'] = result_dic['dev'][3]
            dev_data['time'] = result_dic['time']
            self.emit('new_dev_data', data=dev_data)
        elif result_dic.get('eq') != None:
            eq_data = {}
            eq_data['batteryPercent'] = result_dic['eq'][0]
            eq_data['overall'] = result_dic['eq'][1]
            eq_data['sampleRateQuality'] = result_dic['eq'][2]
            eq_data['sensors'] = result_dic['eq'][3:]
            self.emit('new_eq_data', data=eq_data)
        elif result_dic.get('met') != None:
            met_data = {}
            met_data['met'] = result_dic['met']
            met_data['time'] = result_dic['time']
            self.emit('new_met_data', data=met_data)
        elif result_dic.get('pow') != None:
            pow_data = {}
            pow_data['pow'] = result_dic['pow']
            pow_data['time'] = result_dic['time']
            self.emit('new_pow_data', data=pow_data)
        elif result_dic.get('sys') != None:
            sys_data = result_dic['sys']
            self.emit('new_sys_data', data=sys_data)
        else:
            print('unknown:',result_dic)

    # END OF EMITTERS ------------- ^


    # REQ FUNCTIONS ---------------
    # sections will match those listen in the Cortex API Documentation 
    
    # AUTHENTICATION - https://emotiv.gitbook.io/cortex-api/authentication

    def get_cortex_info(self):
        print('get cortex info --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getCortexInfo",
            "id":GET_CORTEX_INFO
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))
    
    def get_user_login(self):
        print('get user login --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getUserLogin",
            "id":GET_USER_LOGIN
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def request_access(self, client_id, client_secret):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))
    
    def has_access_right(self, client_id, client_secret):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))
    
    def authorize(self, client_id, client_secret):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def generate_new_token(self, cortex_token, client_id, client_secret):
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
        
        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))
    
    def get_user_information(self, cortex_token):
        print('get user information --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getUserInformation",
            "id": GET_USER_INFORMATION,
            "params": {
                "cortexToken": cortex_token
            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def get_license_info(self, cortex_token):
        print('get license info --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getLicenseInfo",
            "id": GET_LICENSE_INFO,
            "params": {
                "cortexToken": cortex_token
            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    # HEADSETS - https://emotiv.gitbook.io/cortex-api/headset

    def control_device(self, command, headset_id=None):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def query_headsets(self, headset_id=None):
        print('query headsets --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "queryHeadsets",
            "id": QUERY_HEADSETS
        }

        if headset_id:
            request["params"] = { "id": headset_id }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    # come back when need to make epoc accessible
    def update_headset(self):
        print('update headset --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "updateHeadset",
            "id": UPDATE_HEADSET,
            "params": {}
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def update_headset_custom_info(self):
        print('update headset custom info --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "updateHeadsetCustomInfo",
            "id": UPDATE_HEADSET_CUSTOM_INFO,
            "params": {}
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def sync_with_headset_clock(self, headset_id, monotonic_time, system_time):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    # SESSIONS - https://emotiv.gitbook.io/cortex-api/session

    def create_session(self, cortex_token, headset_id, status):
        print('create session --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "createSession",
            "id": CREATE_SESSION,
            "params": {
                "cortexToken": cortex_token,
                "headset": headset_id,
                "status": status
            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def update_session(self, cortex_token, session_id, status):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def query_sessions(self, cortex_token):
        print('query sessions --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "querySessions",
            "id": QUERY_SESSIONS,
            "params": {
                "cortexToken": cortex_token
            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    # DATA SUBSCRIPTION - https://emotiv.gitbook.io/cortex-api/data-subscription

    def subscribe(self, cortex_token, session_id, streams):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def unsubscribe(self, cortex_token, session_id, streams):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    # RECORDS - https://emotiv.gitbook.io/cortex-api/records

    def create_record(self, cortex_token, session_id, title, **kwargs):
        print('create record --------------------------------')

        if (len(title) == 0):
            warnings.warn('Empty record_title. Please fill the record_title before running script.')
            # close socket
            self.close()
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def stop_record(self, cortex_token, session_id):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def update_record(self, cortex_token, record_id, title, **kwargs):
        print('update record --------------------------------')

        if (len(title) == 0):
            warnings.warn('Empty record_title. Please fill the record_title before running script.')
            # close socket
            self.close()
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def delete_record(self, cortex_token, record_ids):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def export_record(self, cortex_token, folder, stream_types, export_format, record_ids, version, **kwargs):
        print('export record --------------------------------: ')
        #validate destination folder
        if (len(folder) == 0):
            warnings.warn('Invalid folder parameter. Please set a writable destination folder for exporting data.')
            # close socket
            self.close()
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))
        
        self.ws.send(json.dumps(request))

    def query_records(self, cortex_token, query, order_by, **kwargs):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def get_record_infos(self, cortex_token, record_ids):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    # come back to this
    def config_opt_out(self):
        print('config opt out --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "configOptOut",
            "id": CONFIG_OPT_OUT,
            "params": {}
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def request_to_download_record_data(self, cortex_token, record_ids):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))
    
    # MARKERS - https://emotiv.gitbook.io/cortex-api/markers

    def inject_marker(self, cortex_token, session_id, time, value, label, **kwargs):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def update_marker(self, cortex_token, session_id, marker_id, time, **kwargs):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    # SUBJECTS - https://emotiv.gitbook.io/cortex-api/subjects

    def create_subject(self, cortex_token, subject_name, **kwargs):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def update_subject(self, cortex_token, subject_name, **kwargs):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def delete_subjects(self, cortex_token, subject_names):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def query_subjects(self, cortex_token, query, order_by, **kwargs):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def get_demographic_attributes(self, cortex_token):
        print('get demographic attributes --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getDemographicAttributes",
            "id": GET_DEMOGRAPHIC_ATTRIBUTES,
            "params": {
                "cortexToken": cortex_token
            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    # BCI - https://emotiv.gitbook.io/cortex-api/bci
    
    def query_profile(self, cortex_token):
        print('query profile --------------------------------')

        request = {
            "jsonrpc": "2.0",
            "method": "queryProfile",
            "id": QUERY_PROFILE,
            "params": {
                "cortexToken": cortex_token
            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def get_current_profile(self, cortex_token, headset_id):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    # come back to this
    def setup_profile(self):
        print('setup profile --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "setupProfile",
            "id": SETUP_PROFILE,
            "params": {

            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def load_guest_profile(self, cortex_token, headset_id):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def get_detection_info(self, detection):
        print('get detection info --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getDetectionInfo",
            "id": GET_DETECTION_INFO,
            "params": {
                "detection": detection
            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def training(self, cortex_token, session_id, detection, status, action):
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

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))
    
    # ADVANCED BCI - https://emotiv.gitbook.io/cortex-api/advanced-bci

    def get_trained_signature_actions(self):
        print('get trained signature actions --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getTrainedSignatureActions",
            "id": GET_TRAINED_SIGNATURE_ACTIONS,
            "params": {

            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def get_training_time(self):
        print('get training time --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "getTrainingTime",
            "id": GET_TRAINING_TIME,
            "params": {

            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def facial_expression_signature_type(self):
        print('facial expression signature type --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "facialExpressionSignatureType",
            "id": FACIAL_EXPRESSION_SIGNATURE_TYPE,
            "params": {

            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def facial_expression_threshold(self):
        print('facial expression threshold --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "facialExpressionThreshold",
            "id": FACIAL_EXPRESSION_THRESHOLD,
            "params": {

            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def mental_command_active_action(self):
        print('mental command active action --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "mentalCommandActiveAction",
            "id": MENTAL_COMMAND_ACTIVE_ACTION,
            "params": {

            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def mental_command_brain_map(self):
        print('mental command brain map --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "mentalCommandBrainMap",
            "id": MENTAL_COMMAND_BRAIN_MAP,
            "params": {

            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def mental_command_get_skill_rating(self):
        print('mental command get skill rating --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "mentalCommandGetSkillRating",
            "id": MENTAL_COMMAND_GET_SKILL_RATING,
            "params": {

            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def mental_command_training_threshold(self):
        print('mental command training threshold --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "mentalCommandTrainingThreshold",
            "id": MENTAL_COMMAND_TRAINING_THRESHOLD,
            "params": {

            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    def mental_command_action_sensitivity(self):
        print('mental command action sensitivity --------------------------------')
        request = {
            "jsonrpc": "2.0",
            "method": "mentalCommandActionSensitivity",
            "id": MENTAL_COMMAND_ACTION_SENSITIVITY,
            "params": {

            }
        }

        if self.debug:
            print('request:\n', json.dumps(request, indent=4))

        self.ws.send(json.dumps(request))

    # END OF REQ FUNCTIONS ----- ^
    
    # this can be used in the emit reciever class - see commented out SUB handler

    def extract_data_labels(self, stream_name, stream_cols):
        labels = {}
        labels['streamName'] = stream_name

        data_labels = []
        if stream_name == 'eeg':
            # remove MARKERS
            data_labels = stream_cols[:-1]
        elif stream_name == 'dev':
            # get cq header column except battery, signal and battery percent
            data_labels = stream_cols[2]
        else:
            data_labels = stream_cols

        labels['labels'] = data_labels
        print(labels)
        self.emit('new_data_labels', data=labels)

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------

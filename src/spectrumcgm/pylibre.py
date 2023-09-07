import requests
from datetime import datetime
# set_token(email, password)
# patient_id = getPatientID()
# data = getpatientid()


def trend_map(trend_arr):
    single_down = u'\u2193'
    forty_five_down = u'\u2198'
    flat = u'\u2192'
    forty_five_up = u'\u2197'
    single_up = u'\u2191'
    trend_list = ['', single_down, forty_five_down, flat, forty_five_up, single_up, '']
    return trend_list[trend_arr]


def getlatestmeasurement(data):
    """ Returns the latest measurement information

        Parameters:
        - Expects data dictionary
    """
    latest_measurement = data['data']['connection']['glucoseMeasurement']['Value']
    return latest_measurement


class Libre:
    def __init__(self, email, password, location):

        self.patient_id = None
        #self.arrow = None
        #self.bg = None
        #self.libre_stamp = None
        self.email = email
        self.password = password

        if location == 'Europe':
            self.api_endpoint = 'https://api-eu.libreview.io'
        else:
            self.api_endpoint = 'https://api.libreview.io'

        self.connect_to_linkup()

    headers: dict[str, str] = {
        'accept-encoding': 'gzip',
        'cache-control': 'no-cache',
        'connection': 'Keep-Alive',
        'content-type': 'application/json',
        'product': 'llu.android',
        'version': '4.3.0'
    }

    def get_libre_latest(self):
        data = self.getdata(self.patient_id)
        bg = str(getlatestmeasurement(data))
        libre_stamp = data['data']['connection']['glucoseMeasurement']['Timestamp']
        libre_datetime = datetime.strptime(libre_stamp, "%m/%d/%Y %H:%M:%S %p")
        arr = data['data']['connection']['glucoseMeasurement']['TrendArrow']
        try:
            arrow = trend_map(arr)
        except:
            arrow = ''
        return bg, libre_datetime, arrow

    def connect_to_linkup(self):
        """ Tries to make a connection to LibreLinkUp and requests patiend_id
        """
        self.set_token(self.email, self.password)
        self.patient_id = self.getpatientid()

    def set_token(self, email, password):
        """ Requests authentication token and sets it automatically in the header files.

            Parameters:
            - Expects login credentials
        """

        login_data = {"email": email, "password": password}
        r = requests.post(url=self.api_endpoint + "/llu/auth/login", headers=self.headers, json=login_data)
        data = r.json()
        jwt_token = data['data']['authTicket']['token']
        extra_header_info = {'authorization': 'Bearer ' + jwt_token}
        self.headers.update(extra_header_info)

    def getpatientid(self):
        """ Requests and returns patient_id
        """

        r = requests.get(url=self.api_endpoint + "/llu/connections", headers=self.headers)
        data = r.json()
        return data['data'][0]['patientId']

    def getdata(self, patient_id):
        """ Requests and returns data

            Parameters:
            - Patient_id
        """

        r = requests.get(url=self.api_endpoint + "/llu/connections/" + patient_id + "/graph", headers=self.headers)
        return r.json()

    @staticmethod
    def getallmeasurements(data):
        """ Returns all measurements with information

            Parameters:
            - Expects data dictionary
        """
        all_measurements = data['data']['graphData']
        return all_measurements

#debugging if i need I instead of H in datetime
a = Libre('glenrubin@tutamail.com','mypassword1!GRR','USA')
b = a.getpatientid()
c = a.getdata(b)
d = a.getallmeasurements(c)

print(d)
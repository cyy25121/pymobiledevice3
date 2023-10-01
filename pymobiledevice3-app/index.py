from flask import Flask, request
from flask_cors import CORS
import sys
sys.path.append('../')
from pymobiledevice3.remote.remote_service_discovery import RemoteServiceDiscoveryService
from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation
import threading
import time

app = Flask(__name__, static_folder="../pymobiledevice3-ui/dist/", static_url_path="/")
CORS(app)

lat = None
lng = None
rsd_string = None

def setLocation():
    global lat
    global lng
    global rsd_string
    
    while True:
        if rsd_string is not None:
            host = rsd_string.split(' ')[0]
            port = rsd_string.split(' ')[1]
            with RemoteServiceDiscoveryService((host, port)) as rsd:
                with DvtSecureSocketProxyService(rsd) as dvt:
                    while True:
                        LocationSimulation(dvt).simulate_location(lat, lng)
                        time.sleep(3)
        else:
            time.sleep(2)

background_thread = threading.Thread(target=setLocation)
background_thread.daemon = True
background_thread.start()


@app.route('/setting')
def rsd():
    global rsd_string
    global lat
    global lng

    rsd_string = request.args.get('rsd')
    lat = float(request.args.get('lat'))
    lng = float(request.args.get('lng'))
    return {"rsd_string": rsd_string, "lat": lat, "lng": lng}

@app.route('/location')
def go():
    new_lat = request.args.get('lat')
    new_lng = request.args.get('lng')

    if new_lat is None or new_lng is None:
        return 'lat or lng is None'
    else:
        global lat
        global lng
        lat = float(new_lat)
        lng = float(new_lng)
        return f'lat: {lat}, lng: {lng}'
    
if __name__ == '__main__':
    app.run(host='localhost', port=3000)
    
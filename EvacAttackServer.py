from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from sys import argv
from EvacAttackModel import EvacAttackModel
from EvacAttackShared import BimJsonObject
from functools import reduce
import json

class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # refuse to receive non-json content
        if self.headers.get('content-type') != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))
        
        self._set_headers()

        if self.path == '/exits':
            # подсчёт количества шагов из каждой комнаты к выходам
            zones_with_exit_id_counter: dict[str, dict[str, int]] = dict()
            for _ in range(60):
                model.step()
                for _, zone in model.moving.zones.items():
                    if zone['Id'] in zones_with_exit_id_counter:
                        if zone['ExitTransitId'] in zones_with_exit_id_counter[zone['Id']]:
                            zones_with_exit_id_counter[zone['Id']][zone['ExitTransitId']] += 1
                        else:
                            zones_with_exit_id_counter[zone['Id']] = {
                                zone['ExitTransitId']: 1
                            }
                    else:
                        zones_with_exit_id_counter[zone['Id']] = {
                            zone['ExitTransitId']: 1
                        }
                
                if not model.moving.active or model.moving.num_of_people_inside_building() < 0:
                    break
            
            # поиск в какой выход было больше шагов для всех комнат
            zones_with_exit_id: dict[str, str] = dict()
            for zone_id, exits in zones_with_exit_id_counter.items():
                zone_with_exit_id = reduce(lambda a, b: a if a[1] > b[1] else b, exits.items())
                zones_with_exit_id[zone_id] = zone_with_exit_id[0]
            self.wfile.write(json.dumps(zones_with_exit_id).encode('utf-8'))
        else:
            if "Level" in message:
                model.override = message
            if "step" in message:
                model.step()
            self.wfile.write(json.dumps(model.bim).encode("utf-8"))

def run(server_class=ThreadingHTTPServer, handler_class=Server, port=8008):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    print('Starting httpd on port %d...' % port)
    httpd.serve_forever()


if len(argv) == 3:
    with open(argv[1]) as f:
        j: BimJsonObject = json.load(f)
    model = EvacAttackModel(j)
    model.moving.set_density(0.5)
    model.moving.set_people_by_density()
    run(port=int(argv[2]))
else:
    print("File name and port needed")
    print('Test: curl --data "{\"step\":\"True\"}" --header "Content-Type: application/json" http://localhost:8008')
   
        

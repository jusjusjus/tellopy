
import logging
logging.basicConfig(level=logging.DEBUG)

from tellopy.control import UDPSocket
from tellopy.speech import Speech

drone_ip = '192.168.10.1'
app_cmd_addr = (drone_ip, 8889)
command_sock = UDPSocket(port=8889, listen=False, name='cmd')

def send_command(txt):
    byts = txt.lower().replace(' ', '').encode('utf-8')
    command_sock.send(app_cmd_addr, byts)
    return True

send_command('command')

sp = Speech(callback=send_command)
sp.start_listening()

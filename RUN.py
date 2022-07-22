import sys
from osp.wrappers.simnanodome.dockersession import NanoDOMEDockerSession
from osp.wrappers.simcfd.dockersession import CFDDockerSession
from osp.core.session.transport.transport_session_server import \
    TransportSessionServer

def run_session(host, port):
	serverO=TransportSessionServer(CFDDockerSession, host, port)
    serverO.startListening()
    serverN=TransportSessionServer(NanoDOMEDockerSession, host, port)
    serverN.startListening()

if __name__ == '__main__':
    host=sys.argv[-2]
    port=int(sys.argv[-1])
    run_session(host, port)

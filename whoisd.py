# stdlib imports
import json
import logging
import logging.handlers
import socket
import socketserver

CONFIG_PATH = 'server.conf'
DATA_PATH = 'data.json'
LOG_PATH = 'log.txt'

class WhoisRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        logger = logging.getLogger('whoisd')

        request = self.rfile.readline()
        request = request.decode().strip().lower()

        # process request
        logger.info("Processing request '{}' from {}...".format(
            request, self.client_address[0]))

        hits = []
        for entry in self.server.whois_data['entries']:
            for k, v in entry.items():
                if k.startswith('!'):
                    if request in v.lower():
                        hits.append(entry)
                        break

        # prepare response
        response = "No matches found.\r\n"
        if hits:
            response = self.server.whois_data['header'] + "\r\n"
            counter = 0

            for hit in hits:
                counter += 1
                response += "\r\n-- Record {} of {} --\r\n".format(
                    counter, len(hits))
                for k, v in hit.items():
                    k = k[1:] if k.startswith('!') else k
                    response += "{}: {}\r\n".format(k, v)
            response += "\r\n{}\r\n".format(self.server.whois_data['footer'])

        logger.info("Response:\n{}".format(response))
        logger.info("--------------------------------------")
        self.wfile.write(response.encode())


def main():
    # logging
    logger = logging.getLogger('whoisd')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.handlers.RotatingFileHandler(
            LOG_PATH, maxBytes=50*1024*1024, backupCount=5))

    # read config
    config = {}
    with open(CONFIG_PATH, 'rt') as conf:
        content = json.load(conf)
        if content:
            if ('listen_ip' not in content or 
                not isinstance(content['listen_ip'], str)):
                raise Exception("Expected 'listen_ip' string.")
            if ('listen_port' not in content or 
                not isinstance(content['listen_port'], int)):
                raise Exception("Expected 'listen_port' integer.")
            config = content

    # read database
    data = None
    with open(DATA_PATH, 'rt') as conf:
        content = json.load(conf)
        if content:
            if ('header' not in content or 
                not isinstance(content['header'], str)):
                raise Exception("Expected 'header' string.")
            if ('footer' not in content or 
                not isinstance(content['footer'], str)):
                raise Exception("Expected 'footer' string.")
            if ('entries' not in content or 
                not isinstance(content['entries'], list)):
                raise Exception("Expected 'entries' list.")
            data = content

    # start server
    logger.info("***************************************")
    logger.info("************* STARTING UP *************")
    logger.info("***************************************")
    srv = socketserver.ThreadingTCPServer(
        (config['listen_ip'], config['listen_port']), WhoisRequestHandler,
        False)
    srv.whois_data = data
    srv.allow_reuse_address = True
    srv.server_bind()
    srv.server_activate()
    srv.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Encountered exception: {}".format(e))


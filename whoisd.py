import json
import logging
import logging.handlers
import socket
import socketserver

CONFIG_PATH = 'config.json'
LOG_PATH = 'log.txt'

class WhoisRequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        logger = logging.getLogger('whoisd')
        config = self.server.whois_config
        hits = []
        request = self.rfile.readline()
        request = request.decode().strip().lower()

        # process request
        logger.info("Processing request '{}' from {}...".format(
            request, self.client_address[0]))
        for entry in self.server.whois_config['entries']:
            for k, v in entry.items():
                if k.startswith('!'):
                    if request in v.lower():
                        hits.append(entry)
                        break

        # prepare response
        response = "No matches found.\r\n"
        if hits:
            response = self.server.whois_config['header'] + "\r\n"
            counter = 0

            for hit in hits:
                counter += 1
                response += "\r\n-- Record {} of {} --\r\n".format(counter, len(hits))
                for k, v in hit.items():
                    k = k[1:] if k.startswith('!') else k
                    response += k + ": " + v + "\r\n"
            response += "\r\n" + self.server.whois_config['footer'] + "\r\n"

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
    with open(CONFIG_PATH, 'rt') as conf:
        data = json.load(conf)
        if data:
            if 'header' not in data:
                raise Exception("Expected 'header' string.")
            if 'footer' not in data:
                raise Exception("Expected 'footer' string.")
            if 'entries' not in data or not isinstance(data['entries'], list):
                raise Exception("Expected 'entries' list.")
            config = data

    # start server
    logger.info("***************************************")
    logger.info("************* STARTING UP *************")
    logger.info("***************************************")
    srv = socketserver.ThreadingTCPServer(
        ('0.0.0.0', 43), WhoisRequestHandler, False)
    srv.whois_config = config
    srv.allow_reuse_address = True
    srv.server_bind()
    srv.server_activate()
    srv.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Encoutered exception: {}".format(e))


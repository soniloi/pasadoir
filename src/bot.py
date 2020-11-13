import argparse

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl

import config
from request_handler import RequestHandler


class PasadoirBot(irc.IRCClient):

    nickname = config.BOT_NICK

    def __init__(self, channel, source_dir):
        self.channel = channel
        self.handler = RequestHandler(source_dir)


    def signedOn(self):
        self.join(self.channel)


    def privmsg(self, user, channel, input_message):
        output_message = self.handler.handle(input_message)
        if output_message:
            self.msg(channel, output_message)


class PasadoirBotFactory(protocol.ClientFactory):

    def __init__(self, channel, source_dir):
        self.channel = channel
        self.source_dir = source_dir


    def buildProtocol(self, addr):
        return PasadoirBot(self.channel, self.source_dir)


    def clientConnectionLost(self, connector, reason):
        connector.connect()


    def clientConnectionFailed(self, connector, reason):
        reactor.stop()


if __name__ == "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument("host")
    argparser.add_argument("port")
    argparser.add_argument("channel")
    argparser.add_argument("source_dir")
    argparser.add_argument("--ssl", action="store_true")
    args = argparser.parse_args()

    factory = PasadoirBotFactory(args.channel, args.source_dir)
    if args.ssl:
        reactor.connectSSL(args.host, int(args.port), factory, ssl.ClientContextFactory())
    else:
        reactor.connectTCP(args.host, int(args.port), factory)
    reactor.run()


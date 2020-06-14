import argparse

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol


class PasadoirBot(irc.IRCClient):

    nickname = "pasadoir"

    def __init__(self, channel):
        self.channel = channel


    def signedOn(self):
        self.join(self.channel)


class PasadoirBotFactory(protocol.ClientFactory):

    def __init__(self, channel):
        self.channel = channel


    def buildProtocol(self, addr):
        return PasadoirBot(self.channel)


    def clientConnectionLost(self, connector, reason):
        connector.connect()


    def clientConnectionFailed(self, connector, reason):
        reactor.stop()


if __name__ == "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument("host")
    argparser.add_argument("port")
    argparser.add_argument("channel")
    args = argparser.parse_args()

    factory = PasadoirBotFactory(args.channel)
    reactor.connectTCP(args.host, int(args.port), factory)
    reactor.run()

from meltano.stream import MeltanoStream


class MeltanoExtractor:
    def __init__(self, stream: MeltanoStream, service: 'MeltanoService'):
        self.service = service
        self.stream = stream


    async def extract_all(self):
        pass


    def send_all(self):
        writer = self.stream.create_writer(self)
        #self.start_extract()
        writer.send_all()
        #self.end_extract()

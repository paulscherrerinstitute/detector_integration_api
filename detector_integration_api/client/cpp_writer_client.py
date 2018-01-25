class CppWriterClient(object):

    def __init__(self, writer_url):
        self.writer_url = writer_url
        self.writer_config = None

    def start(self):
        pass

    def stop(self):
        pass

    def get_status(self):
        return {"is_running": True}

    def set_parameters(self, writer_config):
        self.writer_config = writer_config

    def reset(self):
        self.stop()

        self.writer_config = None

    def get_statistics(self):
        return None
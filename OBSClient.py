import obsws_python as obs

class OBSClient:
    def __init__(self):
        self.client = obs.ReqClient(host = "localhost", port = 4455, password = "", timeout = 3)

    def switchToAdsScene(self):
        self.client.set_current_program_scene("ads")

    def switchToContentScene(self):
        self.client.set_current_program_scene("content")

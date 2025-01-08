import obsws_python as obs

class OBSClient:
    # create a connection to the running OBS instance
    def __init__(self):
        self.client = obs.ReqClient(host = "localhost", port = 4455, password = "", timeout = 3)

    def switch_to_scene(self, scene):
        self.client.set_current_program_scene(scene)

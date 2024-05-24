import obsws_python as obs

class OBSClient:
    """Represents a client to connect with the OBS websocket server plugin."""
    
    def __init__(self):
        """Initializes a connection with the OBS websocket server on the default host and port."""
        self.client = obs.ReqClient(host = "localhost", port = 4455, password = "", timeout = 3)

    def switch_to_ads_scene(self):
        """Changes the current scene to 'ads' in OBS."""
        self.client.set_current_program_scene("ads")

    def switch_to_content_scene(self):
        """Changes the current scene to 'content' in OBS."""
        self.client.set_current_program_scene("content")

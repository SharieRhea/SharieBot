import asyncio
import obsws_python as obs


class OBSClient:
    # create a connection to the running OBS instance
    def __init__(self):
        self.client = obs.ReqClient(host="localhost", port=4455, password="", timeout=3)

    def switch_to_scene(self, scene):
        self.client.set_current_program_scene(scene)

    async def display_notification(self):
        item_id = self.client.get_scene_item_id(
            scene_name="overlays", source_name="_notification"
        ).scene_item_id  # pyright: ignore
        self.client.set_scene_item_enabled(
            scene_name="overlays", item_id=item_id, enabled=True
        )
        await asyncio.sleep(5)
        self.client.set_scene_item_enabled(
            scene_name="overlays", item_id=item_id, enabled=False
        )

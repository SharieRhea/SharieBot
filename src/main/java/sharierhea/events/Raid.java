package sharierhea.events;

import com.github.philippheuer.credentialmanager.domain.OAuth2Credential;
import com.github.philippheuer.events4j.simple.SimpleEventHandler;
import com.github.twitch4j.TwitchClient;
import com.github.twitch4j.chat.events.channel.RaidEvent;

public class Raid extends EventListener<RaidEvent> {
    private final OAuth2Credential credential;

    public Raid(SimpleEventHandler eventHandler, TwitchClient client, OAuth2Credential credential) {
        super(eventHandler, client, RaidEvent.class);
        this.credential = credential;
    }

    @Override
    public void handleEvent(RaidEvent event) {
        sendMessage("Thanks for the raid @%s!".formatted(event.getRaider().getName()));
        twitchClient.getHelix().sendShoutout(credential.getAccessToken(), "170582504", event.getRaider().getId(), "957074857").execute();
    }

}

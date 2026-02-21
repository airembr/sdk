from airembr.sdk.chat_client import AiRembrChatClient
from airembr.sdk.model.instance import Instance
from airembr.sdk.model.observation import ObservationEntity

observer, person, agent = AiRembrChatClient.get_references()
actor = ObservationEntity(
    instance=Instance.type("person", "1"),
    traits={"name": "Mark"}
)

client = AiRembrChatClient(
    api="http://localhost:4002",
    source_id="cfbfccdb-e513-4632-9232-31b5af2ed94c",
    entities={  # Entities that take part in the conversation.
        observer: actor,
        person: actor,
        agent: ObservationEntity(
            instance=Instance.type("agent"),
            traits={"name": "ChatGPT", "model": "openai-5"}
        )
    },
    observer=observer,  # Which entiti is an observer? Observer is the owner of the conversation.
    chat_id="chat-1"
)

client.chat("Hello there!", person)
client.chat("Hi How are you!", agent)

status, response = client.remember(realtime='collect,store,destination')

if status.ok():
    print(response.get_chat_memory(client.chat_id).format())
    # Print raw object
    print(response.get_chat_memory(person))
else:
    print(status)

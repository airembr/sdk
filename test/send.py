from sdk.airembr.client import AiRembrClient


def load_messages_from_file(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    messages = [m.strip() for m in content.split("---[NEXT]---") if m.strip()]
    return messages

def pair_messages(messages: list[str]) -> list[tuple[str, str]]:
    return list(zip(messages[::2], messages[1::2]))

client = AiRembrClient(
        api="http://localhost:4002",
        source_id="8351737-a9ad-4c29-a01b-2f3180bec592",
        person_instance="person #1",
        person_traits={"name": "Adam"},
        agent_traits={"name": "ChatGPT", "model": "openai-5"},
        chat_id="chat-1"
    )


messages = load_messages_from_file("test1.txt")
for message1, message2 in pair_messages(messages):
    client.chat(message1, "person")
    client.chat(message2, "agent")

print(client.remember(realtime='collect,store,destination'))

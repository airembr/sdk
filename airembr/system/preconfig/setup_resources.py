from airembr.model.resource_settings import ResourceSettings, DestinationData
from typing import List


def get_resource_types() -> List[ResourceSettings]:
    resource_types = [
        ResourceSettings(
            id="api",
            name="API endpoint",
            icon="cloud",
            config={
                "url": "<url>",
                "proxy": "<proxy>",
                "username": "<username>",
                "password": "<password>",
                "headers": {}
            },
            tags=['api', "destination"],
            destination=DestinationData(
                package="airembr.system.process.dispatching.plugin.http_connector.HttpConnector",
                init={
                    "timeout": 30,
                    "cookies": {},
                    "ssl_check": True
                }
            )
        ),
        ResourceSettings(
            id="semantic-api",
            name="Semantic API endpoint",
            icon="cloud",
            config={
                "url": "<url>",
                "proxy": "<proxy>",
                "username": "<username>",
                "password": "<password>",
                "headers": {},
                "timeout": 30,
                "ssl_check": True
            },
            tags=['api', "destination"],
            destination=DestinationData(
                package="airembr.system.process.dispatching.plugin.semantic_api_connector.SemanticApiConnector",
                init={}
            )
        ),
        ResourceSettings(
            id="telegram",
            name="Telegram",
            tags=["telegram"],
            config={
                "bot_token": "<bot-token>",
                "chat_id": "<chat-id>"
            },
            manual='telegram_resource'
        ),
        ResourceSettings(
            id='fact-attachment-queue',
            icon='pulsar',
            tags=['pulsar', 'apache', 'queue'],
            name='Fact Attachment Queue',
            config={},
            destination=DestinationData(
                package="airembr.system.process.dispatching.plugin.attachment_connector.FactAttachmentConnector",
                outbound='resource'
            )
        ),
        ResourceSettings(
            id='fact-printer-queue',
            icon='pulsar',
            tags=['pulsar', 'apache', 'queue'],
            name='Fact Printer Queue (Debugging)',
            config={},
            destination=DestinationData(
                package="airembr.system.process.dispatching.plugin.printer_connector.FactPrinterConnector",
                outbound='resource'
            )
        )
    ]

    return resource_types


def get_type_of_resources():
    resource_types = get_resource_types()
    for resource_type in resource_types:
        if resource_type.pro is None:
            yield resource_type.id, resource_type.dict()

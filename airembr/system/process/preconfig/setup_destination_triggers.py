from airembr.model.gui.form import Form, FormGroup, FormField, FormComponent
from airembr.model.destination_trigger import DestinationTrigger

DT_ENTITY_CHANGE_TRIGGER = 'entity-change-trigger'
DT_EVENT_TRIGGER = 'event-trigger'
DT_OBSERVATION_END_TRIGGER = 'observation-end-trigger'
DT_EVENT_ATTACHMENT_TRIGGER = 'event-attachment-trigger'
DT_EMBEDDER = 'embedder'

embedder_trigger = DestinationTrigger(
    id=DT_EMBEDDER,
    name="Fact Embedding (Real-Time)",
    description="Embedding process will be triggered real-time on new collected facts",
    config={
        "source": {"id": "", "name": ""},
        "event_type": {"id": "", "name": ""}
    },
    form=Form(groups=[
        FormGroup(
            name="Trigger Configuration",
            fields=[
                FormField(
                    id="source",
                    name="Send only when data comes from event source",
                    component=FormComponent(
                        type="source",
                        props={
                            "label": "Data Source"

                        })
                ),
                FormField(
                    id="event_type",
                    name="Send only selected event type",
                    component=FormComponent(
                        type="eventType",
                        props={
                            "label": "Event Type",
                            "fullWidth": False
                        })
                ),
                FormField(
                    id="bulk_size",
                    name="Bulk facts for embedding.",
                    description="Max number of facts to be embedded at once.",
                    component=FormComponent(
                        type="text",
                        props={
                            "label": "Bulk Size",
                        })
                ),
                FormField(
                    id="bulk_timeout",
                    name="Bulking timeout (in seconds).",
                    description="The maximum number of seconds to wait for facts before starting the embedding process.",
                    component=FormComponent(
                        type="text",
                        props={
                            "label": "Timeout",
                        })
                ),
                FormField(
                    id="max_questions",
                    name="Generate max questions for each fact.",
                    description="Defined number of questions for each fact to be generate. If 0 than none will be generated. It requires LLM provider to be defined in the destination configuration.",
                    component=FormComponent(
                        type="text",
                        props={
                            "label": "Max Questions",
                            "value": "0"
                        })
                )
            ])
    ])
)

event_trigger = DestinationTrigger(
    id=DT_EVENT_TRIGGER,
    name="Fact Collected (Real-Time)",
    description="It is triggered real-time on new collected facts",
    config={
        "source": {"id": "", "name": ""},
        "event_type": {"id": "", "name": ""}
    },
    form=Form(groups=[
        FormGroup(
            name="Trigger Configuration",
            fields=[
                FormField(
                    id="source",
                    name="Send only when data comes from event source",
                    component=FormComponent(
                        type="source",
                        props={
                            "label": "Data Source"

                        })
                ),
                FormField(
                    id="event_type",
                    name="Send only selected event type",
                    component=FormComponent(
                        type="eventType",
                        props={
                            "label": "Event Type",
                            "fullWidth": False
                        })
                )
            ])
    ])
)

event_attachment_trigger = DestinationTrigger(
    id=DT_EVENT_ATTACHMENT_TRIGGER,
    name="Fact Attachment (Defered)",
    description="The destination will be triggered for all defined facts, including previously existing data.",
    config={
        "source": {"id": "", "name": ""},
        "event_type": {"id": "", "name": ""},
        "since": None
    },
    form=Form(groups=[
        FormGroup(
            name="Trigger Configuration",
            fields=[
                FormField(
                    id="source",
                    name="Trigger only when data comes from event source",
                    component=FormComponent(
                        type="source",
                        props={
                            "label": "Data Source"

                        })
                ),
                FormField(
                    id="event_type",
                    name="Trigger only selected event type",
                    component=FormComponent(
                        type="eventType",
                        props={
                            "label": "Event Type",
                            "fullWidth": False
                        })
                ),
                FormField(
                    id="since",
                    name="Select only facts after this date",
                    component=FormComponent(
                        type="text",
                        props={
                            "label": "Date",
                        })
                )
            ])
    ])
)

observation_ended_trigger = DestinationTrigger(
    id=DT_OBSERVATION_END_TRIGGER,
    name="Observation Ended (Defered)",
    description="Destination will be triggered when select observations end.",
    config={
        "observation_types": "",
    },
    form=Form(groups=[
        FormGroup(
            name="Trigger Configuration",
            fields=[
                FormField(
                    id="observation_types",
                    description="Types of observation that will trigger this trigger. Separate types with comma.",
                    name="Observation types",
                    component=FormComponent(
                        type="text",
                        props={
                            "label": "Observation Type"
                        })
                ),
                FormField(
                    id="idle_timeout",
                    description="How many minutes of no activity should pass to consider the observation finished and trigger the action?",
                    name="Idle time",
                    component=FormComponent(
                        type="text",
                        props={
                            "label": "Idle Time in Minutes"
                        })
                )
            ])
    ])
)

destination_triggers = [
    event_trigger,
    event_attachment_trigger,
    # entity_change_trigger,
    observation_ended_trigger,
    embedder_trigger
]

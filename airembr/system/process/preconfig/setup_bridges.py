import os

from airembr.model.metadata.sys_bridge import Bridge
from airembr.model.gui.form import Form, FormGroup, FormField, FormComponent

_local_dir = os.path.dirname(__file__)

IMAP_BRIDGE_ID = 'imap-91be-476d-a4e5-a495159f'
REDIRECT_BRIDGE_ID = 'redirect-91be-476d-a4e5-1b2d7e005403'
API_BRIDGE_ID = "api-4ff3-4e08-9a86-72c0195fa95d"
JS_BRIDGE_ID = "js-adff-6e08-9a86-72c0195fa95d"
WEBHOOK_BRIDGE_ID = "webhook-28d1-4a38-b19c-d0c1fbb71e22"

with open(os.path.join(_local_dir, "bridges/manual/rest_manual.md"), "r", encoding="utf-8") as fh:
    rest_manual = fh.read()

open_rest_source_bridge = Bridge(
    id=API_BRIDGE_ID,
    type="rest",
    name="REST API Bridge",
    description="API /track collector",
    manual=rest_manual
)

open_js_source_bridge = Bridge(
    id=JS_BRIDGE_ID,
    type="rest",
    name="Javascript Bridge",
    description="Javascript collector",
    config={
        "restrict_to": "none",
        "restriction": ""
    },
    form=Form(groups=[
        FormGroup(
            name="REST API Bridge Configuration",
            fields=[
                FormField(
                    id="restrict_to",
                    name="Allow collection only from defined domain",
                    description="Select if you would like to restrict event source to be able to collect data "
                                "from certain domain or IP.",
                    component=FormComponent(
                        type="select",
                        props={
                            "label": "Restriction type",
                            "items": {
                                "none": "None",
                                "url": "URL Address"}
                        })
                ),
                FormField(
                    id="restriction",
                    name="Restrict to URL Address",
                    description="Type URL (e.g http://www.example.com) if the restriction type was selected.",
                    component=FormComponent(
                        type="text",
                        props={
                            "label": "URL with Domain or IP Address"
                        })
                )
            ])
    ])
)

open_webhook_source_bridge = Bridge(
    id=WEBHOOK_BRIDGE_ID,
    type="webhook",
    name="Webhook API Bridge",
    description="API Webhook collector",
    config={
        "mapping": '{}'
    },
    form=Form(groups=[
        FormGroup(
            name="API Webhook Bridge Configuration",
            description="The webhook bridge needs data to be remapped to Observation object.",
            fields=[
                FormField(
                    id="mapping",
                    name="Please remap the webhook to Observation object.",
                    description="Use payload@ as data source. See documentation for details.",

                    component=FormComponent(type="json", props={"label": "Observation object"})
                )
            ])
    ])
)
with open(os.path.join(_local_dir, "bridges/manual/redirect_manual.md"), "r", encoding="utf-8") as fh:
    redirect_manual = fh.read()

redirect_bridge = Bridge(
    id=REDIRECT_BRIDGE_ID,
    type='redirect',
    name="Redirect URL Bridge",
    description="Redirects URLs and registers events.",
    manual=redirect_manual,
    form=Form(groups=[
        FormGroup(
            name="Redirect Bridge Configuration",
            description="The Redirect Bridge requires information about the destination URL and the event to be triggered when the link is clicked.",
            fields=[
                FormField(
                    id="event_type",
                    name="Please type event the will be raised when the link is clicked.",
                    component=FormComponent(type="text", props={"label": "Event Type"})
                ),
                FormField(
                    id="customer_id",
                    name="Which param to use to read customer ID.",
                    component=FormComponent(type="text", props={"label": "Customer ID URL Param."})
                ),
                FormField(
                    id="event_properties",
                    name="Event properties",
                    description="Please type event properties if any. Use payload@param to access URL parameters.",
                    component=FormComponent(type="json", props={"label": "Event Properties"})
                )
            ]),

        FormGroup(
            name="Redirect URL",
            description="The Redirect Bridge requires information about the destination URL and the event to be triggered when the link is clicked.",
            fields=[
                FormField(
                    id="redirect_url",
                    name="Where to redirect the traffic.",
                    component=FormComponent(type="text", props={"label": "URL"})
                )
            ])
    ])
)

with open(os.path.join(_local_dir, "bridges/manual/imap_manual.md"), "r", encoding="utf-8") as fh:
    imap_manual = fh.read()

imap_bridge = Bridge(
    id=IMAP_BRIDGE_ID,
    type='imap',
    name="E-mail IMAP Bridge",
    description="Reads emails and registers events.",
    manual=imap_manual,
    form=Form(groups=[
        FormGroup(name="E-mail owner",
                  fields=[
                      FormField(
                          id="owner_name",
                          name="Please type E-mail Owner Name and Surname",
                          component=FormComponent(type="text", props={"label": "Owner Name and Surname"}),
                          required=True
                      ),
                  ]),
        FormGroup(
            name="E-mail IMAP  Configuration",
            description="The Redirect Bridge requires information about the destination URL and the event to be triggered when the link is clicked.",
            fields=[
                FormField(
                    id="imap_server",
                    name="Please type imap server domain.",
                    component=FormComponent(type="text", props={"label": "E-Map Server"})
                ),
                FormField(
                    id="email_account",
                    name="Email account.",
                    component=FormComponent(type="text", props={"label": "Email Account"})
                ),
                FormField(
                    id="email_password",
                    name="Email password",
                    description="Please type e-mail password.",
                    component=FormComponent(type="password", props={"label": "E-mail password"})
                )
            ]),

        FormGroup(
            name="Initial Fetch in Days",
            description="How many e-mails should be fetched on source start. This allows to index previous e-mails. Define in days.",
            fields=[
                FormField(
                    id="initial",
                    name="Initial Fetch",
                    component=FormComponent(type="text", props={"label": "How many emails should I get on start."})
                )
            ])
    ])
)

with open(os.path.join(_local_dir, "bridges/manual/ical_manual.md"), "r", encoding="utf-8") as fh:
    ical_manual = fh.read()

ical_bridge = Bridge(
    id=IMAP_BRIDGE_ID,
    type='ical',
    name="Calendar ICAL Bridge",
    description="Reads meetings and registers events from ICAL file.",
    manual=imap_manual,
    form=Form(groups=[
        FormGroup(
            name="ICAL Configuration",
            description="The Redirect Bridge requires information about the URL ICAL file.",
            fields=[
                FormField(
                    id="account_email",
                    name="Please Type Calendar Account Email.",
                    component=FormComponent(type="text", props={"label": "E-mail"}),
                    required=True
                ),
                FormField(
                    id="account_owner",
                    name="Please Type Calendar Owner Name and Surname",
                    component=FormComponent(type="text", props={"label": "Owner Name and Surname"}),
                    required=True
                ),
                FormField(
                    id="calendar_name",
                    name="Please Type Calendar Name, e.g. Personal, Business, etc.",
                    component=FormComponent(type="text", props={"label": "Calendar Name"}),
                    required=True
                ),
                FormField(
                    id="ical_file",
                    name="Please type ical URL.",
                    component=FormComponent(type="text", props={"label": "ICAL URL"}),
                    required=True
                ),
            ]),

    ])
)

os_default_bridges = [
    open_js_source_bridge,
    open_rest_source_bridge,
    open_webhook_source_bridge,
    redirect_bridge,
    imap_bridge,
    ical_bridge
]

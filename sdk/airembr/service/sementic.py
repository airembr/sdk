from sdk.airembr.model.instance_link import InstanceLink
from jinja2 import Environment, Undefined
from jinja2.exceptions import UndefinedError


class DefaultUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return 'N/A'  # default value for missing attributes/variables

    def __str__(self):
        return 'N/A'

    def __getattr__(self, name):
        return self  # return self so chained attributes also return default

    def __getitem__(self, key):
        return self


def safe_attr(obj, attr, default=None):
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default


def render_description(template_str: str, actor_link: InstanceLink, object_link: InstanceLink, observation):
    data = observation.model_dump(mode='json')

    if actor_link:
        actor = observation.entities.get(actor_link.link)
        if actor:
            actor = actor.model_dump(mode='json')
            data['actor'] = actor
        data['_actor'] = actor_link.to_dict()

    if object_link:
        object = observation.entities.get(object_link.link)
        if object:
            object = object.model_dump(mode='json')
            data['object'] = object
        data['_object'] = object_link.to_dict()

    try:
        env = Environment()
        env.filters['attr'] = safe_attr
        template = env.from_string(template_str)
        return template.render(**data)
    except UndefinedError:
        env = Environment(undefined=DefaultUndefined)  # allow undefined variables silently
        env.filters['attr'] = safe_attr
        template = env.from_string(template_str)
        return template.render(**data)

from .project import Project  # noqa
from .dicts import GigaTariff, PaymentSystem, UserType  # noqa
from .payment import Payment  # noqa
from .subscription import Subscription  # noqa
from .user import User, UserProfile, ProfileTypes  # noqa


def parse_id(id_: str) -> tuple:
    if isinstance(id_, str):
        if ':' in id_:
            parsed_id, instance = id_.split(':', maxsplit=2)
            return int(parsed_id), instance
    return int(id_), None


def create_compound_id(id_, instance):
    return f'{id_}:{instance}'

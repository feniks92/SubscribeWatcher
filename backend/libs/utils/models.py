from pydantic.main import BaseModel


class ExcludeFields(BaseModel):
    """Model extends pydantic Config class.
    Allows to set exclude fields.
        example:

        class User(ExcludeFields):
            name: str
            password: Optional[str]

            class Config:
                exclude = {'password',}

        user = User(name='foo', password='bar')

        user.dict() --> {'name': 'foo'}
        user.json() --> {"name": "foo"}
    """

    def dict(self, **kwargs):
        self.make_exclude(kwargs)
        return super().dict(**kwargs)

    def json(self, **kwargs):
        self.make_exclude(kwargs)
        return super().json(**kwargs)

    def make_exclude(self, kwargs):
        exclude = getattr(self.Config, "exclude", set())
        tr = kwargs.get('exclude')
        if not tr:
            kwargs['exclude'] = exclude
        else:
            tr.update(exclude)

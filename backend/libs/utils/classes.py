class Singleton(object):
    def __new__(cls, *args: object, **kwargs: object) -> object:
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance

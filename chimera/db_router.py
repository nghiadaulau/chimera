class DbRouter(object):
    """
    A router to control all database operations on models in the auth applications.
    """

    @staticmethod
    def db_for_read(model, **hint):
        return "default"

    @staticmethod
    def db_for_write(model, **hint):
        return "default"

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        return True

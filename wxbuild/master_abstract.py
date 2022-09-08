from abc import ABC


class Master(ABC):
    def post_init(self):
        pass

    def handle_user_event(self, type, name, panel):
        pass
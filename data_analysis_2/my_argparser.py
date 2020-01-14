
class Argparser:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        print(self.kwargs)
        print(dir(kwargs))

asd = {"a": 1, "b": 2}
a = Argparser(**asd)
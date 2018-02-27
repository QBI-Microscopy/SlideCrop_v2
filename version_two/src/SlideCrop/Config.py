import random

class Config(object):

    test_folder = "E:/threshold"
    random_number = "1234"

    @staticmethod
    def change_random_number(cls):
        cls.random_number = str(random.randint(0, 10000))

class ApplicationContext(object):
    def __init__(self):
        self.instances = 1
        self.accountName = 'account10'


class ApplicationDeployment(object):
    def __init__(self):
        # user_slug = str(uuid.uuid4())[9:13]
        self.user_slug = 'c4dd'
        pass

    def install(self):
        pass

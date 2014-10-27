import numpy as np




verbose = True


class White:


    def __init__(self, policy):
        self.policy = policy

    def evaluate(self):
        df = self.policy.simulate()
        print df






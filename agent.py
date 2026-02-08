import numpy as np
import random


class QAgent:

    def __init__(self, state_size, action_size):

        self.state_size = state_size
        self.action_size = action_size

        self.q = {}

        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.2


    def get_key(self, state):

        return tuple(np.round(state, 1))


    def choose(self, state):

        key = self.get_key(state)

        # Exploration
        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)

        # Initialize if new state
        if key not in self.q:
            self.q[key] = np.zeros(self.action_size)

        # Exploitation
        return np.argmax(self.q[key])


    def learn(self, s, a, r, s2):

        k1 = self.get_key(s)
        k2 = self.get_key(s2)

        if k1 not in self.q:
            self.q[k1] = np.zeros(self.action_size)

        if k2 not in self.q:
            self.q[k2] = np.zeros(self.action_size)

        self.q[k1][a] += self.alpha * (
            r + self.gamma * np.max(self.q[k2])
            - self.q[k1][a]
        )

import numpy as np
import random


class CloudEnv:

    def __init__(self):

        self.max_vms = 10
        self.min_vms = 1

        self.reset()


    def reset(self):

        self.vms = 2
        self.cpu = np.zeros(self.vms)
        self.queue = []

        self.time = 0

        return self.get_state()


    def get_state(self):

        avg_cpu = np.mean(self.cpu)
        queue_len = len(self.queue)

        return np.array([
            self.vms,
            avg_cpu,
            queue_len
        ])


    def generate_task(self):

        cpu = random.uniform(0.1, 0.5)
        duration = random.randint(2, 5)

        return [cpu, duration]


    def step(self, action):

        cost = 0
        delay = 0


        # Scaling
        if action == 1 and self.vms < self.max_vms:

            self.vms += 1
            self.cpu = np.append(self.cpu, 0)


        elif action == 2 and self.vms > self.min_vms:

            self.vms -= 1
            self.cpu = self.cpu[:-1]


        # Scheduling
        if len(self.queue) > 0:

            vm_id = random.randint(0, self.vms - 1)

            task = self.queue.pop(0)

            self.cpu[vm_id] += task[0]

            delay = task[1]


        # Execute
        self.cpu = np.clip(self.cpu - 0.1, 0, 1)


        # Add new tasks
        for _ in range(random.randint(0, 2)):

            self.queue.append(self.generate_task())


        # Cost
        cost = self.vms * 0.5


        # Reward
        reward = -(cost + delay + len(self.queue))


        self.time += 1

        done = self.time > 500


        return self.get_state(), reward, done

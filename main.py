from cloud_env import CloudEnv
from agent import QAgent
import matplotlib.pyplot as plt

def baseline_policy(state):

    vms, cpu, queue = state

    # If CPU is high → Add VM
    if cpu > 0.8:
        return 1   # Add VM

    # If CPU is low → Remove VM
    if cpu < 0.3:
        return 2   # Remove VM

    # Otherwise → Do nothing
    return 0

env = CloudEnv()

agent = QAgent(
    state_size=3,
    action_size=3
)

episodes = 300
rewards = []

for ep in range(episodes):

    state = env.reset()
    total = 0

    done = False

    while not done:

        action = agent.choose(state)

        new_state, reward, done = env.step(action)

        agent.learn(state,action,reward,new_state)

        state = new_state
        total += reward

    rewards.append(total)

    print("Episode:",ep,"Reward:",total)
# ============================
# BASELINE TEST
# ============================

baseline_rewards = []

for ep in range(100):

    state = env.reset()
    total = 0
    done = False

    while not done:

        action = baseline_policy(state)

        new_state, reward, done = env.step(action)

        state = new_state
        total += reward

    baseline_rewards.append(total)

    print("Baseline Episode:", ep, "Reward:", total)

plt.plot(rewards, label="RL Agent")
plt.plot(baseline_rewards, label="Baseline")

plt.xlabel("Episode")
plt.ylabel("Total Reward")
plt.title("RL vs Baseline Performance")

plt.legend()
plt.show()

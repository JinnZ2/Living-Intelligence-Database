import math
import itertools

# --- Element and Environment classes reused from previous snippet ---
class Element:
    def __init__(self, name, type_, energy_profile, interaction_rules):
        self.name = name
        self.type_ = type_
        self.energy_profile = energy_profile
        self.interaction_rules = interaction_rules

    def interact(self, other, environment):
        rule = self.interaction_rules.get(other.type_, lambda e, env: 0)
        return rule(other.energy_profile, environment)

class Environment:
    def __init__(self, gravity=9.81, wind=0.0, temperature=25.0):
        self.gravity = gravity
        self.wind = wind
        self.temperature = temperature

    def update(self, delta_t):
        self.wind = math.sin(delta_t/10) * 2.0
        self.temperature = 25 + 5*math.sin(delta_t/20)

class Experiment:
    def __init__(self, elements, environment):
        self.elements = elements
        self.environment = environment

    def run(self, steps=10):
        history = []
        for t in range(steps):
            self.environment.update(t)
            total_effect = 0
            for a, b in itertools.combinations(self.elements, 2):
                total_effect += a.interact(b, self.environment)
                total_effect += b.interact(a, self.environment)
            history.append((t, total_effect))
            for el in self.elements:
                el.energy_profile *= 1 + 0.01 * math.tanh(total_effect)
        return history

# --- Prototype: Load database entries as Elements ---
# Sample placeholder for Living Intelligence Database entries
ldb_entries = [
    {"name": "Bee", "type": "animal", "energy": 0.8, "interactions": {"plant": 0.3, "animal": -0.1}},
    {"name": "Sunflower", "type": "plant", "energy": 1.0, "interactions": {"animal": 0.5, "plant": 0.2}},
    {"name": "Quartz", "type": "crystal", "energy": 1.2, "interactions": {"plant": 0.1, "animal": 0.2}},
    {"name": "Vortex", "type": "geometry", "energy": 1.5, "interactions": {"plant": 0.2, "animal": 0.3}}
]

elements = []
for entry in ldb_entries:
    # Convert interaction numeric values to callable functions
    interaction_rules = {}
    for target_type, factor in entry["interactions"].items():
        interaction_rules[target_type] = lambda e, env, f=factor: f*e*(1 + env.wind/10)
    elements.append(Element(entry["name"], entry["type"], entry["energy"], interaction_rules))

# --- Run experiment ---
env = Environment()
experiment = Experiment(elements, env)
history = experiment.run(steps=20)

for t, outcome in history:
    print(f"Step {t}: Pattern effect = {outcome:.3f}, Wind={env.wind:.2f}, Temp={env.temperature:.1f}")

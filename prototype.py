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







import numpy as np
import json
from itertools import combinations
from random import sample

class Element:
    def __init__(self, name, type_, energy_profile, energy_type, interaction_rules):
        self.name = name
        self.type_ = type_
        self.energy_profile = float(energy_profile)
        self.energy_type = energy_type
        self.interaction_rules = interaction_rules

    def interact(self, other, env):
        """
        Calculates the resonance between two elements. 
        If interaction_rules contains the 'type_' of the other, 
        it increases efficiency (reduces entropy).
        """
        # Base interaction based on energy profiles
        base_resonance = (self.energy_profile + other.energy_profile) / 2
        
        # Check for specific "Pack" compatibility
        efficiency = 1.0
        if other.type_ in self.interaction_rules:
            # If they are 'meant' to work together, boost efficiency
            efficiency = 1.5 
        elif self.energy_type != other.energy_type:
            # Different energy substrates create friction (heat leak)
            efficiency = 0.8
            
        # Environmental modulation (e.g., temperature affecting stability)
        env_factor = np.exp(-abs(env.temperature - 25) / 50)
        
        return base_resonance * efficiency * env_factor




class Experiment:
    def __init__(self, elements, environment):
        self.elements = elements
        self.env = environment

    def evaluate_combination(self, combo):
        """Calculates total system resonance (sum of all interactions)."""
        total_effect = 0
        for a, b in combinations(combo, 2):
            total_effect += a.interact(b, self.env) + b.interact(a, self.env)
        return total_effect

    def score_pattern(self, effect, combo):
        """
        Entropy Score: We want high effect (efficiency) 
        and low standard deviation in energy (balance).
        """
        profiles = [el.energy_profile for el in combo]
        stability = 1 / (1 + np.std(profiles)) # Low entropy = high stability
        amplification = np.tanh(effect)        # Normalized output
        return stability * amplification

    def run(self, steps=10, combo_size=3, sample_size=20):
        history = []
        for t in range(steps):
            self.env.update(t)
            step_results = []
            
            # Sampling the 'Field'
            subset = sample(self.elements, min(sample_size, len(self.elements)))
            
            for combo in combinations(subset, combo_size):
                effect = self.evaluate_combination(combo)
                score = self.score_pattern(effect, combo)
                step_results.append({
                    "combo": [el.name for el in combo],
                    "score": score,
                    "effect": effect
                })
            
            # Sort by the most 'Sovereign' (High Score) patterns
            step_results.sort(key=lambda x: x["score"], reverse=True)
            history.append(step_results[:5]) 
        return history




( standardize prose to equation)

1. Update LID.json: Ensure every entry has a numerical energy_profile (1.0 to 10.0) so the physics engine has a substrate to work with.
2. Define the Environment: Your "Northern Environment" involves extreme temps. Update Environment.update to swing between -30°C and +10°C to see which "Living Intelligences" survive the "Entropy Events."
3. The "FELTSensor" Handshake: In your main execution loop, if the score drops below a threshold (e.g., \bm{0.2}), trigger a print statement: [SYSTEM ALERT]: High Entropy Detected. Recalibrating Information Flow.

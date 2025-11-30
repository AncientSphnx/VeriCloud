import json
import os
from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import skfuzzy as fuzz
from skfuzzy import control as ctrl


@dataclass
class HyperparameterSpace:
    # Example ERNN hyperparameters: learning_rate, hidden_size, dropout
    learning_rate: Tuple[float, float] = (1e-4, 1e-2)
    hidden_size: Tuple[int, int] = (32, 256)
    dropout: Tuple[float, float] = (0.0, 0.6)


@dataclass
class FuzzyConfig:
    features_file: str  # CSV/JSON from feature extraction
    output_json: str
    space: HyperparameterSpace = HyperparameterSpace()

    # Which feature columns to use as inputs to the system
    feature_inputs: Tuple[str, str] = ("tonal_stable_ratio", "stress_energy_cv")

    # Performance target for validation to accept parameters
    validation_target: float = 0.7  # just stored; external trainer would evaluate


def _load_features(path: str) -> pd.DataFrame:
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    return pd.read_json(path)


def build_fuzzy_system(cfg: FuzzyConfig) -> Tuple[ctrl.ControlSystem, Dict[str, ctrl.Antecedent], Dict[str, ctrl.Consequent]]:
    """Build fuzzy variables, membership functions, and rules.

    Inputs: two features (x1, x2). Output: three hyperparameters.
    """
    # Antecedents
    x1 = ctrl.Antecedent(np.linspace(0, 1, 101), cfg.feature_inputs[0])
    x2 = ctrl.Antecedent(np.linspace(0, 2, 101), cfg.feature_inputs[1])  # energy cv roughly 0-2

    # Membership (triangular): low/medium/high
    x1['low'] = fuzz.trimf(x1.universe, [0.0, 0.0, 0.4])
    x1['med'] = fuzz.trimf(x1.universe, [0.2, 0.5, 0.8])
    x1['high'] = fuzz.trimf(x1.universe, [0.6, 1.0, 1.0])

    x2['low'] = fuzz.trimf(x2.universe, [0.0, 0.0, 0.6])
    x2['med'] = fuzz.trimf(x2.universe, [0.4, 0.9, 1.4])
    x2['high'] = fuzz.trimf(x2.universe, [1.2, 2.0, 2.0])

    # Consequents scaled to hyperparameter ranges
    lr_min, lr_max = cfg.space.learning_rate
    lr = ctrl.Consequent(np.linspace(lr_min, lr_max, 101), 'learning_rate')
    lr['low'] = fuzz.trimf(lr.universe, [lr_min, lr_min, (lr_min + lr_max) / 2])
    lr['med'] = fuzz.trimf(lr.universe, [lr_min, (lr_min + lr_max) / 2, lr_max])
    lr['high'] = fuzz.trimf(lr.universe, [(lr_min + lr_max) / 2, lr_max, lr_max])

    hs_min, hs_max = cfg.space.hidden_size
    hs = ctrl.Consequent(np.linspace(hs_min, hs_max, 101), 'hidden_size')
    hs['small'] = fuzz.trimf(hs.universe, [hs_min, hs_min, (hs_min + hs_max) / 2])
    hs['medium'] = fuzz.trimf(hs.universe, [hs_min, (hs_min + hs_max) / 2, hs_max])
    hs['large'] = fuzz.trimf(hs.universe, [(hs_min + hs_max) / 2, hs_max, hs_max])

    do_min, do_max = cfg.space.dropout
    do = ctrl.Consequent(np.linspace(do_min, do_max, 101), 'dropout')
    do['low'] = fuzz.trimf(do.universe, [do_min, do_min, (do_min + do_max) / 2])
    do['med'] = fuzz.trimf(do.universe, [do_min, (do_min + do_max) / 2, do_max])
    do['high'] = fuzz.trimf(do.universe, [(do_min + do_max) / 2, do_max, do_max])

    # ✅ Corrected rules (each consequent defined separately)
    rules = [
        # Case 1: stable tone + low stress
        ctrl.Rule(x1['low'] & x2['low'],   hs['medium']),
        ctrl.Rule(x1['low'] & x2['low'],   do['low']),
        ctrl.Rule(x1['low'] & x2['low'],   lr['high']),

        ctrl.Rule(x1['low'] & x2['med'],   hs['small']),
        ctrl.Rule(x1['low'] & x2['med'],   do['med']),
        ctrl.Rule(x1['low'] & x2['med'],   lr['low']),

        ctrl.Rule(x1['low'] & x2['high'],  hs['small']),
        ctrl.Rule(x1['low'] & x2['high'],  do['high']),
        ctrl.Rule(x1['low'] & x2['high'],  lr['low']),

        # 2. medium tone stability
        ctrl.Rule(x1['med'] & x2['low'],   hs['medium']),
        ctrl.Rule(x1['med'] & x2['low'],   do['low']),
        ctrl.Rule(x1['med'] & x2['low'],   lr['med']),

        ctrl.Rule(x1['med'] & x2['med'],   hs['medium']),
        ctrl.Rule(x1['med'] & x2['med'],   do['med']),
        ctrl.Rule(x1['med'] & x2['med'],   lr['med']),

        ctrl.Rule(x1['med'] & x2['high'],  hs['small']),
        ctrl.Rule(x1['med'] & x2['high'],  do['high']),
        ctrl.Rule(x1['med'] & x2['high'],  lr['low']),

        # 3. high tone stability
        ctrl.Rule(x1['high'] & x2['low'],  hs['large']),
        ctrl.Rule(x1['high'] & x2['low'],  do['low']),
        ctrl.Rule(x1['high'] & x2['low'],  lr['med']),

        ctrl.Rule(x1['high'] & x2['med'],  hs['large']),
        ctrl.Rule(x1['high'] & x2['med'],  do['med']),
        ctrl.Rule(x1['high'] & x2['med'],  lr['high']),

        ctrl.Rule(x1['high'] & x2['high'], hs['medium']),
        ctrl.Rule(x1['high'] & x2['high'], do['med']),
        ctrl.Rule(x1['high'] & x2['high'], lr['low']),
    ]

    system = ctrl.ControlSystem(rules)
    return system, {cfg.feature_inputs[0]: x1, cfg.feature_inputs[1]: x2}, {'learning_rate': lr, 'hidden_size': hs, 'dropout': do}


def run_fuzzy_optimization(cfg: FuzzyConfig) -> Dict[str, float]:
    features = _load_features(cfg.features_file)
    system, antecedents, consequents = build_fuzzy_system(cfg)
    sim = ctrl.ControlSystemSimulation(system)

    # Aggregate inputs over the dataset using robust statistics
    inputs = {
        cfg.feature_inputs[0]: float(np.clip(features[cfg.feature_inputs[0]].fillna(0.0).median(), 0.0, 1.0)),
        cfg.feature_inputs[1]: float(np.clip(features[cfg.feature_inputs[1]].fillna(0.0).median(), 0.0, 2.0)),
    }

    # Feed inputs safely into fuzzy system (avoid boundary issues)
    for name, value in inputs.items():
        antecedent = antecedents[name]
        low, high = antecedent.universe.min(), antecedent.universe.max()
        safe_value = min(max(value, low + 1e-6), high - 1e-6)  # nudge inside
        sim.input[name] = safe_value

    print("Simulation inputs:", sim.input)  # 🔎 Debug: see actual inputs
    sim.compute()

    # Collect outputs safely
    result = {
        'name': 'fuzzy_sugeno',
        'inputs_used': inputs,
    }
    for out_name in consequents.keys():
        if out_name in sim.output:
            result[out_name] = float(sim.output[out_name])
        else:
            result[out_name] = None  # fallback in case fuzzy system skipped

    # Persist results
    os.makedirs(os.path.dirname(cfg.output_json) or '.', exist_ok=True)
    with open(cfg.output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    return result


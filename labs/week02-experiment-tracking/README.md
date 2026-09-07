# Week 02 Lab

Instrument a provided training script (`train.py`) with MLflow experiment tracking; log params, metrics, and artifacts across a few runs, then compare them in the MLflow UI.

Starter files for this week's lab are pulled into your repo via `git fetch upstream && git merge upstream/main`, as introduced in the Week 1 lab.

## Reflection

Run 3 (n_estimators=200, max_depth=None) performed best at 0.9722 accuracy, about 14 points better than the baseline's 0.8306. More trees and no depth cap let the forest fit the digit boundaries more precisely without the earlier runs' underfitting. This week's MLflow setup covers the "config" leg of reproducibility — the bare script printed results to the terminal and lost them the moment you changed a hyperparameter; now every run's config and outcome is permanently logged and comparable.

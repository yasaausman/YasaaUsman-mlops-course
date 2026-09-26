# Week 04 Lab

Build a reusable preprocessing pipeline (sklearn Pipeline/ColumnTransformer); PCA as a worked stateful-transform example.

Starter files for this week's lab will be added here before the lab session
(pulled into your repo via `git fetch upstream && git merge upstream/main`,
as introduced in the Week 1 lab).

## Reflection

The original script's accuracy (0.6375) and the fixed pipeline's accuracy (0.65, from the GridSearchCV run) landed close together, but that doesn't mean the leak was harmless — it means this particular leak happened not to move this particular metric, on this particular 400-row dataset. Accuracy is an estimate of how well the model generalizes, and leakage corrupts the *validity* of that estimate, not necessarily its *value*. A bigger dataset, a more leak-sensitive model, or features where the full-data and train-only statistics diverge more sharply could easily turn the same mistake into a badly inflated number. The lecture's point stands: leakage is a bug in your evaluation methodology, and the metric itself is not a reliable way to detect it.

The leak came from `imputer.fit_transform(X[NUMERIC_FEATURES])` and `scaler.fit_transform(X[NUMERIC_FEATURES])` running on the full `X` before `train_test_split` was ever called. I didn't prove this by watching accuracy — I compared the fitted `.mean_` of two `StandardScaler`s directly: one fit on the full dataset (leaky) and one fit only on `X_train` after splitting (correct). They differed — `annual_income` came out to 43761.45 in the leaky fit versus 43213.02 in the correct one — which is direct evidence the "training" transform had already learned something from rows it should never have seen.

The production scenario (serving code recomputing its own `StandardScaler` from whatever requests showed up in the last hour) describes training/serving skew, not the leak I fixed here. My leak was about *which rows* a single, one-time fit was allowed to see. This is about *when* and *on what population* the transform gets fit at all — recomputing it continuously from live, uncontrolled traffic means the same input gets transformed differently depending on what else happened to arrive that hour. It breaks the fit/predict discipline from the lecture: fit once, at training time, then reuse that exact same fitted transform unchanged at serving time.

PCA's "state" is the rotation — the principal component directions and the explained variance it learned from the training data's covariance structure — captured inside the fitted `pca` object, the same category of thing as a scaler's `mean_`/`scale_`. If serving code ran a fresh `PCA().fit_transform()` on incoming requests instead of reusing the fitted training-time object, it would compute a *different* rotation from whatever arbitrary batch of production data happened to be on hand, so the same raw input would land at different coordinates depending on what else was in that batch. The classifier was trained on coordinates from one specific, fixed rotation — feeding it coordinates from a different, unstable one would break its learned decision boundary immediately.

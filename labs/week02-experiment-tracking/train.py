"""
Week 2 Lab -- starter training script (NOT YET INSTRUMENTED)

Trains a RandomForestClassifier on the digits dataset (built into
scikit-learn -- 1,797 images of handwritten digits 0-9, no download needed).
Your job in this lab is to add MLflow experiment tracking around this
script -- logging hyperparameters, metrics, and a confusion matrix
artifact -- without changing what the script actually does.

Run it as-is first to see the baseline behavior:
    python train.py
"""

from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
from sklearn.metrics import ConfusionMatrixDisplay

# ---- config: edit these between runs to compare results ----
N_ESTIMATORS = 200
MAX_DEPTH = None
RANDOM_STATE = 42
# --------------------------------------------------------------
mlflow.set_experiment("week2-lab")

def main():
    data = load_digits()
    X, y = data.data, data.target

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )
    with mlflow.start_run():
        model = RandomForestClassifier(
            n_estimators=N_ESTIMATORS,
            max_depth=MAX_DEPTH,
            random_state=RANDOM_STATE,
        )
        mlflow.log_param("n_estimators", N_ESTIMATORS)
        mlflow.log_param("max_depth", MAX_DEPTH)
        mlflow.log_param("random_state", RANDOM_STATE)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="macro")
        recall = recall_score(y_test, y_pred, average="macro")
        f1 = f1_score(y_test, y_pred, average="macro")
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1", f1)    
        fig, ax = plt.subplots(figsize=(6, 6))
        ConfusionMatrixDisplay.from_predictions(y_test, y_pred, ax=ax)
        fig.savefig("confusion_matrix.png")
        mlflow.log_artifact("confusion_matrix.png")
        plt.close(fig)
        
        print(f"n_estimators={N_ESTIMATORS}, max_depth={MAX_DEPTH}")
        print(f"accuracy:  {accuracy:.4f}")
        print(f"precision: {precision:.4f}")
        print(f"recall:    {recall:.4f}")
        print(f"f1:        {f1:.4f}")


if __name__ == "__main__":
    main()

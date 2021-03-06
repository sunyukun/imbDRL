import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (average_precision_score, confusion_matrix,
                             f1_score, fbeta_score, precision_recall_curve)


def network_predictions(network, X: np.ndarray) -> dict:
    """Computes y_pred using a given network.
    Input is array of data entries.

    :param network: The network to use to calculate metrics
    :type  network: (Q)Network
    :param X: X data, input to network
    :type  X: np.ndarray

    :return: Numpy array of predicted targets for given X
    :rtype: np.ndarray
    """
    if not isinstance(X, np.ndarray):
        raise ValueError(f"`X` must be of type `np.ndarray` not {type(X)}")

    q, _ = network(X)
    return np.argmax(q.numpy(), axis=1)  # Max action for each x in X


def decision_function(network, X: np.ndarray) -> dict:
    """Computes the score for the predicted class of each x in X using a given network.
    Input is array of data entries.

    :param network: The network to use to calculate the score per x in X
    :type  network: (Q)Network
    :param X: X data, input to network
    :type  X: np.ndarray

    :return: Numpy array of scores for given X
    :rtype: np.ndarray
    """
    if not isinstance(X, np.ndarray):
        raise ValueError(f"`X` must be of type `np.ndarray` not {type(X)}")

    q, _ = network(X)
    return np.max(q.numpy(), axis=1)  # Max action for each x in X


def classification_metrics(y_true: list, y_pred: list) -> dict:
    """Computes metrics using y_true and y_pred.

    :param y_true: True labels
    :type  y_true: np.ndarray
    :param y_pred: Predicted labels, corresponding to y_true
    :type  y_pred: np.ndarray

    :return: Dictionairy containing Geometric Mean, F0.5, F1, F2, TP, TN, FP, FN
    :rtype: dict
    """
    if not isinstance(y_true, (list, tuple, np.ndarray)):
        raise ValueError(f"`y_true` must be of type `list` not {type(y_true)}")
    if not isinstance(y_pred, (list, tuple, np.ndarray)):
        raise ValueError(f"`y_pred` must be of type `list` not {type(y_pred)}")
    if len(y_true) != len(y_pred):
        raise ValueError("`X` and `y` must be of same length.")

    TN, FP, FN, TP = confusion_matrix(y_true, y_pred).ravel()

    recall = TP / denom if (denom := TP + FN) else 0  # Sensitivity, True Positive Rate (TPR)
    specificity = TN / denom if (denom := TN + FP) else 0  # Specificity, selectivity, True Negative Rate (TNR)

    G_mean = np.sqrt(recall * specificity)  # Geometric mean of recall and specificity
    Fdot5 = fbeta_score(y_true, y_pred, beta=0.5, zero_division=0)  # β of 0.5
    F1 = f1_score(y_true, y_pred, zero_division=0)  # Default F-measure
    F2 = fbeta_score(y_true, y_pred, beta=2, zero_division=0)  # β of 2

    return {"Gmean": G_mean, "Fdot5": Fdot5, "F1": F1, "F2": F2, "TP": TP, "TN": TN, "FP": FP, "FN": FN}


def plot_pr_curve(network, X_test: np.ndarray, y_test: np.ndarray,
                  X_val: np.ndarray = None, y_val: np.ndarray = None) -> None:   # pragma: no cover
    """Plots PR curve of X_test and y_test of given network.
    Optionally plots PR curve of X_val and y_val.
    Average precision is shown in the legend.

    :param network: The network to use to calculate the PR curve
    :type  network: (Q)Network
    :param X_test: X data, input to network
    :type  X_test: np.ndarray
    :param y_test: True labels for `X_test`
    :type  y_test: np.ndarray
    :param X_val: Optional X data to plot validation PR curve
    :type  X_val: np.ndarray
    :param y_val: True labels for `X_val`
    :type  y_val: np.ndarray

    :return: None
    :rtype: NoneType
    """
    y_test_score = decision_function(network, X_test)
    test_precision, test_recall, _ = precision_recall_curve(y_test, y_test_score)
    test_AP = average_precision_score(y_test, y_test_score)

    if X_val is not None and y_val is not None:
        y_val_score = decision_function(network, X_val)
        val_precision, val_recall, _ = precision_recall_curve(y_val, y_val_score)
        val_AP = average_precision_score(y_val, y_val_score)
        plt.plot(val_recall, val_precision, label=f"Val AP: {val_AP:.3f}")

    plt.plot(test_recall, test_precision, label=f"Test AP: {test_AP:.3f}")
    plt.xlim([0.0, 1.05])
    plt.ylim([0.0, 1.05])
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("PR Curve")
    plt.legend(loc="lower left")
    plt.grid(True)
    plt.show()

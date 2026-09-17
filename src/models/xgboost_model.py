"""XGBoost-based training scaffold for cement process prediction."""

from __future__ import annotations

from typing import Iterable, List, Sequence

try:
    import xgboost as xgb
except ImportError:  # pragma: no cover - optional dependency at stage 1
    xgb = None


class CementPredictionModel:
    """Minimal interface for a first-pass XGBoost model on a cement target."""

    def __init__(self, objective: str = "reg:squarederror"):
        self.objective = objective
        self.model = None

    def fit(self, X, y):
        if xgb is None:
            raise ImportError("xgboost is required for the prediction model.")
        self.model = xgb.XGBRegressor(objective=self.objective, n_estimators=200, max_depth=6, learning_rate=0.05)
        self.model.fit(X, y)
        return self

    def predict(self, X):
        if self.model is None:
            raise ValueError("The model has not been trained yet.")
        return self.model.predict(X)

    @staticmethod
    def feature_importance(feature_names: Sequence[str], importances: Iterable[float]):
        ranked = sorted(
            zip(feature_names, importances),
            key=lambda item: float(item[1]),
            reverse=True,
        )
        return [{"feature": name, "importance": float(value)} for name, value in ranked]

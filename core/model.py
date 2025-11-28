from typing import Dict, Tuple

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import MinMaxScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


class PriceLSTM(nn.Module):
    def __init__(self, hidden_size: int = 48):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=hidden_size, num_layers=1, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


def _prepare_sequences(prices: np.ndarray, lookback: int) -> Tuple[torch.Tensor, torch.Tensor]:
    x_list, y_list = [], []
    for i in range(len(prices) - lookback):
        x_list.append(prices[i : i + lookback])
        y_list.append(prices[i + lookback])
    x = torch.tensor(np.array(x_list), dtype=torch.float32).reshape(-1, lookback, 1)
    y = torch.tensor(np.array(y_list), dtype=torch.float32).reshape(-1, 1)
    return x, y


def predict_next_price(
    series: pd.Series,
    lookback: int = 30,
    epochs: int = 3,
    hidden_size: int = 48,
) -> Tuple[float, float, Dict]:
    """Train a lightweight LSTM on the fly and predict the next close price."""
    result_meta: Dict = {"trained_epochs": 0, "fallback": False, "loss_history": []}
    if series is None or series.empty:
        return 0.0, 0.0, {**result_meta, "fallback": True}

    closing = series.fillna(method="ffill").values.astype(float)
    if len(closing) < lookback + 2:
        last_price = float(closing[-1])
        return last_price, 0.0, {**result_meta, "fallback": True, "reason": "insufficient_data"}

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(closing.reshape(-1, 1)).flatten()
    x, y = _prepare_sequences(scaled, lookback)
    dataset = TensorDataset(x, y)
    loader = DataLoader(dataset, batch_size=min(32, len(dataset)), shuffle=True)

    device = torch.device("cpu")
    model = PriceLSTM(hidden_size=hidden_size).to(device)
    optim = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.MSELoss()

    model.train()
    for epoch in range(epochs):
        epoch_losses = []
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            optim.zero_grad()
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            optim.step()
            epoch_losses.append(loss.item())
        if epoch_losses:
            result_meta["loss_history"].append(float(np.mean(epoch_losses)))
            result_meta["trained_epochs"] = epoch + 1

    model.eval()
    with torch.no_grad():
        last_window = torch.tensor(scaled[-lookback:], dtype=torch.float32).reshape(1, lookback, 1).to(device)
        pred_scaled = model(last_window).cpu().numpy()[0][0]
        pred_price = scaler.inverse_transform([[pred_scaled]])[0][0]

    last_price = float(closing[-1])
    pct_change = (pred_price - last_price) / last_price if last_price else 0.0
    return float(pred_price), float(pct_change), result_meta

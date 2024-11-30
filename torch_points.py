import torch
import matplotlib.pyplot as plt
import os
import numpy as np
import math


def plot_points(p_x, p_y, loss=None, save=False):
    plt.figure(figsize=(8, 8))
    plt.scatter(p_x.cpu().detach(), p_y.cpu().detach(), alpha=1, s=7)
    plt.xlabel("X")
    plt.ylabel("Y")
    title = "Random Points"
    if loss is not None:
        title += f" (Loss: {loss:.6f})"
    plt.title(title)
    plt.xlim(0, w)
    plt.ylim(0, h)

    if save:
        os.makedirs("imgs", exist_ok=True)
        filename = f"optimized_points_{loss:.4f}.png"
        plt.savefig(os.path.join("imgs", filename))

    plt.show()


def get_loss(x, y, alpha, w, h):
    positions = torch.stack([x, y], dim=1)  # Shape (N, 2)
    distances = torch.pdist(positions)
    reciprocal_sum = torch.sum(1.0 / distances)
    border = torch.sum(1 / x + 1 / y + 1 / (w - x) + 1 / (h - y))
    loss = alpha * border + reciprocal_sum
    return loss


def plot_loss(losses):
    plt.figure(figsize=(10, 5))
    plt.plot(losses)
    plt.xlabel("Iteration")
    plt.ylabel("Loss")
    plt.yscale("log")
    plt.title("Loss Over Time")
    plt.ylim(
        min(losses) - 2, min(losses) + 2
    )  # Adjust y-axis to focus on the flat part
    plt.show()


def plot_lr_schedule(lrs: list[float]):
    plt.figure(figsize=(10, 5))
    plt.plot(lrs)
    plt.xlabel("Iteration")
    plt.ylabel("Learning Rate")
    plt.title("Learning Rate Schedule")
    plt.show()


def get_lrs(iterations: int, peak_lr: float, min_lr: float):
    lrs = []
    for i in range(iterations):
        progress = i / (iterations - 1)
        lr = min_lr + (peak_lr - min_lr) * math.sin(math.pi * progress)
        lrs.append(lr)

    return lrs


def optimize_points(x, y, alpha, w, h, lrs: list[float], iterations: int):
    optimizer = torch.optim.SGD([x, y])
    losses = []

    for i in range(iterations):
        for param_group in optimizer.param_groups:
            param_group["lr"] = lrs[i]

        optimizer.zero_grad()
        loss = get_loss(x, y, alpha, w, h)
        losses.append(loss.item())
        loss.backward()
        optimizer.step()

        with torch.no_grad():
            x.clamp_(1, w - 1)
            y.clamp_(1, h - 1)

    plot_loss(losses)
    return losses[-1]


def get_points(n, w, h, device):
    x = (
        1 + torch.rand(n, dtype=torch.float32, device=device) * (w - 1)
    ).requires_grad_()
    y = (
        1 + torch.rand(n, dtype=torch.float32, device=device) * (h - 1)
    ).requires_grad_()
    return x, y


def save_points(x, y, filename="optimized_points.npz"):
    # Create points directory if it doesn't exist
    os.makedirs("points", exist_ok=True)

    points = torch.stack([x.cpu().detach(), y.cpu().detach()], dim=1).numpy()
    np.savez(os.path.join("points", filename), points=points)


if __name__ == "__main__":
    w = 800
    h = 800
    n = 1000
    alpha = 250
    iterations = 100
    min_lr = 0.5
    peak_lr = 800
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    x, y = get_points(n, w, h, device)
    lrs = get_lrs(iterations, peak_lr, min_lr)
    print(lrs)
    print(len(lrs))
    plot_points(x, y, save=False)
    plot_lr_schedule(lrs)

    final_loss = optimize_points(x, y, alpha, w, h, lrs, iterations)
    save_points(x, y, f"optimized_points_{final_loss:.4f}.npz")

    plot_points(x, y, final_loss, save=True)

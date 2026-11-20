---
layout: post
title: "Fit, Fail, Fix: Linear Regression From Scratch"
description: "Part 3 of five: fitting linear regression from scratch with a bias column, the normal equations, and NumPy."
tags:
  - machine-learning
  - linear-regression
  - tutorial
date: 2026-11-20 10:00:00 +0800
---

> **Fit, Fail, Fix** · Post 3 of 5
>
> *Finding the best weights with a bias column, the normal equations and nothing but NumPy*

## A model is just a weighted sum

A linear regression model predicts an answer by multiplying each feature by a learned weight, adding them up, and adding a bias:

```text
prediction = b + w₁·x₁ + w₂·x₂ + ... + w_d·x_d
```

That is it. "Training" means finding good values for `b` and all the `w`s.

For the compact model we use only 5 features, so we need 6 numbers: `b, w₁..w₅`. For the full model we use all 40, so we need 41 numbers.

## The trick: hide the bias inside the matrix

Writing `+ b` separately is annoying in matrix math. The standard trick is to add an extra first column of **ones** to the feature matrix. Then if `θ₀` (the first parameter) plays the role of `b`, the multiplication reproduces the bias automatically:

```text
[1, x₁, x₂, ...] · [b, w₁, w₂, ...]ᵀ  =  b + w₁x₁ + w₂x₂ + ...
```

We call the ones-enhanced matrix `X̃` ("X tilde"). In code this is:

```python
def add_bias(X):
    return np.column_stack([np.ones(X.shape[0]), X])
```

## How do we find the best weights?

We choose the weights that make predictions closest to the real targets on the training set. "Closest" means minimising the sum of squared errors — the same idea behind MSE.

There are two ways to do this:

1. **Iterative (gradient descent):** start with random weights and take small steps downhill. Great for huge datasets.
2. **Direct (normal equations):** solve one linear system and get the answer in one shot. Great for small problems like this one.

This lab uses method 2. Setting the derivative of the squared error to zero gives the **normal equations**:

```text
(X̃ᵀ X̃) · θ = X̃ᵀ · y
```

Here `X̃ᵀ` means "transpose X̃" (flip rows and columns). If you have seen the geometry: we are projecting the target vector onto the space spanned by the columns of X̃, and the solution `θ` gives the coordinates of that projection.

## Solve, do not invert

You might be tempted to write `θ = inv(X̃ᵀ X̃) · X̃ᵀ · y`. Don't. Forming a matrix inverse explicitly is slower and less numerically stable. NumPy gives us `np.linalg.solve(A, b)` which solves `A·θ = b` directly:

```python
def fit_ols(X_tilde, y):
    return np.linalg.solve(X_tilde.T @ X_tilde, X_tilde.T @ y)
```

`@` is NumPy's matrix multiplication operator. The lab explicitly requires this approach.

## Task 2 in numbers

With the 5 useful features, the learned parameters came out as:

| | learned | truth |
| --- | --- | --- |
| bias | 0.989 | 1.0 |
| w₁ | 2.860 | 3.0 |
| w₂ | −2.590 | −2.0 |
| w₃ | 1.646 | 1.5 |
| w₄ | −0.014 | 0.5 |
| w₅ | −1.341 | −1.0 |

The model recovered the general shape of the true rule — four weights are in the right ballpark and have the correct sign. w₄ is off, which is a reminder that with only 56 noisy examples, individual weights can be estimated poorly even when the overall predictions are good. Training MSE was 3.55 and test MSE 4.46, close to the noise floor of ~4.

## What to take away

- A linear model is a weighted sum; learning means finding the weights.
- Adding a column of ones lets the bias be "just another weight".
- The normal equations give an exact answer for small problems.
- `solve` beats explicit inversion.
- Recovering true weights is hard with little noisy data — but good predictions can still happen.

---

*Previous: [Post 2 — Making the Data](/fit-fail-fix-making-the-data/) · Next in the series: **Post 4 — Overfitting: When More Is Worse**.*

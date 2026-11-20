---
layout: post
title: "Fit, Fail, Fix: Ridge Regularisation"
description: "Part 5 of five: using ridge regularisation to shrink weights, reduce variance, and recover generalisation."
tags:
  - machine-learning
  - linear-regression
  - tutorial
date: 2026-11-20 12:00:00 +0800
---

> **Fit, Fail, Fix** · Post 5 of 5
>
> *Putting a gentle leash on the model so it remembers the signal and forgets the noise*

## The idea in one sentence

Ridge regression keeps all 40 features but adds a **penalty for large weights**, forcing the model to explain the data with smaller, gentler coefficients.

## The objective changes

Ordinary least squares minimises only the prediction error:

```text
minimise:  prediction error on training data
```

Ridge minimises a combination:

```text
minimise:  prediction error  +  λ · (sum of squared weights)
```

The new term is the **ℓ2 penalty** (sum of squares of the parameters, i.e. ‖θ‖²). The Greek letter **λ** (lambda) controls how strong the leash is:

- **λ = 0** → no penalty → ordinary least squares (Task 3).
- **small λ** → gentle nudge towards smaller weights.
- **large λ** → strong squeeze towards zero.

The handout gives the modified normal equations (we use them exactly):

```text
(X̃ᵀ X̃ + n_train · λ · I) θ = X̃ᵀ y
```

The `+ n_train·λ·I` part is the mathematical effect of the penalty. `I` is the identity matrix; adding a multiple of it to `X̃ᵀ X̃` also helps numerically when features are correlated.

## What the results show

| λ | Training MSE | Test MSE | ‖θ‖₂ |
| --- | --- | --- | --- |
| 0.01 | 0.677 | 12.348 | 4.802 |
| 0.1 | 1.097 | **8.332** | 3.739 |
| 10 | 11.926 | 12.741 | 0.346 |

Remember the unregularised 40-feature model: test MSE 13.56, ‖θ‖₂ = 5.01.

Now trace the story as λ grows:

1. **Parameters shrink:** ‖θ‖₂ falls from 4.80 → 3.74 → 0.35. The leash works.
2. **Training error rises:** 0.68 → 1.10 → 11.93. The model is no longer free to fit every wobble. That is expected and fine.
3. **Test error improves, then worsens:** 12.35 → **8.33** → 12.74. A moderate λ = 0.1 is the sweet spot here, cutting test error substantially versus 13.56.
4. **λ = 10 is too strong:** the weights are practically zero, predictions collapse towards a constant, and the model *underfits* — it is now too simple, with high bias. Both training and test error get bad.

## Why does shrinking weights help generalisation?

Large weights usually mean the model is reacting strongly to tiny, idiosyncratic details of the training data — exactly the noise we want to ignore. By capping the weights, ridge reduces the model's **variance**: it becomes less sensitive to which particular 56 rows it happened to see. Lower variance → better test performance.

Think of it as telling a student: "Don't memorise 40 tiny rules; use a few moderate ones." The student may score slightly worse on the practice paper but better on the real exam.

## An honest nuance

Even the best ridge model (8.33) did not beat the compact 5-feature model (4.46). When you *know* which features matter, throwing away the useless ones is even more effective than shrinking them. Regularisation is most valuable when you cannot confidently pick features — which is the usual situation in practice.

## How is λ chosen in real life?

Not by guessing. The standard approach is **cross-validation**: try many λ values, split the training data into parts, and pick the λ that predicts the held-out parts best. The lab fixes three values so we can see the trend; a real project would search a wider range.

## Final mental model

```text
Too simple (few features)  ──► high bias, underfitting
Sweet spot                 ──► good generalisation
Too complex (no leash)     ──► high variance, overfitting
Ridge with moderate λ      ──► keeps features, tames variance
Ridge with huge λ          ──► back to underfitting
```

That is the entire lab in one picture. Well done — you have now seen, with real numbers, three of the central ideas of machine learning: fitting, overfitting, and regularisation.

---

*Previous: [Post 4 — Overfitting: When More Is Worse](/fit-fail-fix-overfitting-when-more-is-worse/) · Back to [Post 1 — The Big Picture](/fit-fail-fix-the-big-picture/).*

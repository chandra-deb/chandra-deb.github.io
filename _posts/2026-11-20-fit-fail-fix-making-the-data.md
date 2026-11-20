---
layout: post
title: "Fit, Fail, Fix: Making the Data"
description: "Part 2 of five: building a tiny synthetic world where we know the true rule, so we can tell signal from noise."
tags:
  - machine-learning
  - linear-regression
  - tutorial
date: 2026-11-20 09:00:00 +0800
---

> **Fit, Fail, Fix** · Post 2 of 5
>
> *Building a tiny world where we secretly know all the answers*

## Why invent fake data?

It sounds odd, but fake (we say **synthetic**) data is one of the best teaching tools in machine learning. Because *we* wrote the rule that generates it, we know the true answer. That means we can ask:

> "Did the model actually find the real rule, or did it just get lucky?"

With real-world data you rarely know the true rule, so you cannot check. Here you can.

## The recipe for our world

We create 80 observations (rows). Each row has 40 numbers describing it — we call these **features**, stored in a matrix `X` with shape 80 × 40. Each feature is a random number from a standard normal distribution (a bell curve centred at 0 with width 1).

Then we compute the target `y` for each row using this rule:

```text
y = 1 + 3·x₁ − 2·x₂ + 1.5·x₃ + 0.5·x₄ − x₅ + noise
```

Let's read that slowly:

- **1** is the *bias* (also called the intercept): the value left when all inputs are zero.
- `3·x₁` means feature 1 has a weight of +3: bigger x₁ → bigger y.
- `−2·x₂` means feature 2 pushes y *down*.
- Features 3, 4, 5 contribute 1.5, 0.5 and −1.
- **Features 6 through 40 do not appear at all.** Their true weight is zero. They are decoys.
- **noise** is a random wobble from a bell curve with standard deviation 2. Real measurements are never perfectly exact; the noise represents that.

So: **5 useful features, 35 useless ones, and a noisy target.**

## Why add noise?

Noise makes the problem realistic, and it sets a limit on how good any model can be. If the noise has variance 2² = 4, then even the *perfect* model will still miss by about that much on average. That is why our best test MSE (about 4.46) is close to 4 — we are essentially at the best achievable score. Useful thing to know when judging results!

## The seed: making randomness repeatable

Random numbers on a computer are not truly random — they follow a fixed sequence determined by a starting value called a **seed**. We set:

```python
rng = np.random.default_rng(7)
```

Seed 7 means every run produces the exact same dataset. Without it, our numbers would change each time and we could not compare models fairly. (If you use a different random generator API, the numbers shift a bit, but the *conclusions* stay the same.)

## The train/test split

After generating all 80 rows, we **shuffle** them with the same generator, then:

- first **56 rows** → **training set** (the model learns from these);
- last **24 rows** → **test set** (kept hidden, used only for the final grade).

Shuffling matters: if we took the first 56 before shuffling we might accidentally get a systematic slice of the data. Splitting after a random shuffle makes both sets representative.

## What the code checks

`lab01.py` prints and asserts the shapes:

```text
X_train (56, 40)   X_test (24, 40)
y_train (56,)      y_test (24,)
```

and checks that `mse([1,2], [1,2]) == 0` — a small sanity test that our scoring function behaves sensibly.

## Key takeaway

We deliberately built a problem where most features are worthless. This lets us test whether a model can tell signal from noise — and, as we will see, giving a model more features does not automatically help it.

---

*Previous: [Post 1 — The Big Picture](/fit-fail-fix-the-big-picture/) · Next in the series: **Post 3 — Linear Regression From Scratch**.*

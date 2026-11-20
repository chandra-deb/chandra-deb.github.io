---
layout: post
title: "Fit, Fail, Fix: The Big Picture"
description: "Part 1 of five: why a model that scores better on training data can fail on new data, and how this lab makes that visible."
tags:
  - machine-learning
  - linear-regression
  - tutorial
---

> **Fit, Fail, Fix** · Post 1 of 5
>
> *A beginner's guide to Linear Regression, Model Complexity and Ridge Regularisation*

> **The question this whole lab answers:** If a model has a lower error on the data it trained on, will it also do better on new data? (Spoiler: no.)

## Start with a story

Imagine you are studying for a big exam. You have last year's practice paper, and you take it again and again until you can answer every question perfectly. You even memorise which answer goes with which question number.

Did you learn the subject? Maybe not. You might have just **memorised the practice paper**. On the real exam, with different questions, you would do badly.

Machine learning has exactly the same trap:

- **Training data** = the practice paper the model studies.
- **Test data** = the real exam, with questions the model has never seen.
- **Training error** = score on the practice paper.
- **Test error** = score on the real exam.

The whole game is to do well on the *test*, not the *training* set. We call this ability to handle new data **generalisation**.

## Why this matters outside the classroom

- A spam filter should work on tomorrow's emails, not just yesterday's.
- A medical model should work on new patients, not just the ones it was trained on.
- A weather model should predict next week, not just re-describe last week.

In every case, a model that "memorised" its training data is useless. So we need a way to *detect* memorisation. That is what this lab does.

## What we will actually do

We are going to build a **fake world** where we know the true rule by heart (Post 2). Then we will train three models with different amounts of freedom:

1. A small, careful model that only uses the 5 features that really matter.
2. A big, flexible model that uses all 40 features, including 35 useless ones.
3. That same big model, but with a leash that stops its weights from getting too large (Post 5).

We will measure each model on both the practice paper and the real exam, and watch what happens.

## The metric: MSE

To score predictions, we use **Mean Squared Error (MSE)**: for every example, subtract the true value from the prediction, square the result, then average all those squares.

- Perfect predictions → MSE = 0.
- Bigger mistakes → bigger MSE (and squaring punishes big mistakes extra hard).
- Lower is better.

We will write this function ourselves in NumPy — it is only one line, and doing it by hand means we know exactly what it measures.

## The punchline you will see

In this lab, the flexible 40-feature model gets a *much better* training score than the careful 5-feature model (0.67 vs 3.55) — but a *much worse* test score (13.56 vs 4.46). It memorised the noise. Then a well-chosen "leash" recovers some of the lost performance. That story — complexity, overfitting, regularisation — is one of the most important ideas in all of machine learning.

---

*Next in the series: **Post 2 — Making the Data**, on building a tiny world where we secretly know all the answers.*

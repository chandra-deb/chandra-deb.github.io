---
layout: post
title: "Before Writing a Single Line of Campusly AI"
description: "The first engineering chapter of Campusly AI: smaller milestones, fewer unnecessary components, and a decision to start with Go."
tags:
  - campusly
  - building-campusly-ai
  - software-architecture
  - go
  - ai
---

*25 November 2026 · Building Campusly AI, Part 1. Architecture and engineering decisions, not a finished implementation or benchmark.*

A few days ago, I wrote about the kind of AI-powered organizer workspace I want to build inside Campusly. The idea was to reduce the time student organizers spend answering repetitive questions, coordinating activities, and chasing information across group chats.

The messaging foundation is now working in my local environment. I have tested it manually, including public discussions, private student inquiries and the ability to reopen existing discussions. There is still infrastructure work ahead, but I finally have something I can interact with.

So naturally, the next step was to build the AI assistant.

Or, apparently, to spend a considerable amount of time discussing the architecture of an AI assistant that couldn't even say hello yet.

## The assistant that had everything except an assistant

The original plan was ambitious. A personal assistant, shared group AI, asynchronous workers, memory extraction, organizational knowledge, activity retrospectives, and eventually an independently scalable infrastructure.

All of those ideas have a place in Campusly's longer-term vision. The problem was the order in which I was planning to build them.

If I implemented the backend, the agent tools, and the shared group integration before building a usable interface, I would have to wait a long time before experiencing the product myself.

And what if I didn't like the experience once I finally got there?

I decided to turn the plan around. Rather than building an entire technical layer at a time, I want to build one small user-facing capability across the necessary layers.

For the first milestone, an organization president should be able to open Campusly, enter the personal assistant, type a message, and receive a response.

That's it.

No organizational intelligence. No group memory. No vector database. The assistant is officially allowed to say hello before it learns the entire history of an organization.

## Thirty-one milestones, one small feature at a time

The revised roadmap now contains 31 product milestones across five phases:

| Phase | What I want to build |
| --- | --- |
| A | A private personal assistant, conversation history and management |
| B | Campusly-aware information retrieval, activity drafts, notices and approved actions |
| C | Personal memory and cross-conversation recall |
| D | Shared group AI, grounded answers and reliable event processing |
| E | Organization intelligence, shared knowledge and later automation |

These are not 31 mandatory steps before anyone gets a useful product. The first useful president assistant can be reviewed and released separately, long before the organization-level features exist. Actual technical prerequisites matter more than the numbering.

The rule is that every user-facing milestone should come with a usable local interface, relevant automated tests, and a manual scenario I can try myself.

For example, when the activity-drafting milestone is ready, I should be able to describe a Python workshop, inspect the generated fields and edit them. The next milestone can add confirmed creation through Campusly's existing business rules. Drafting and creating an official activity are different capabilities, and I want to test them separately.

That also means I will have screenshots, feedback, and real mistakes to document along the way. Hopefully I remember to take the screenshots this time.

## Personal memory before group memory

Another change was to move personal memory ahead of shared group intelligence.

There is a difference between remembering earlier messages in a conversation and remembering that an organizer prefers short, informal announcements across multiple conversations.

Personal memory gives me a relatively contained way to explore retrieval, context management, corrections, and deletion. It is still a privacy-sensitive feature, but I don't have to solve the additional problems of group membership, shared ownership and conflicting organizational knowledge at the same time.

I also don't know yet whether I need semantic search. Structured records may be enough for an early version. I would rather test that assumption than install a vector database because the architecture diagram looks lonely without one.

And whatever the assistant remembers, current Campusly records remain authoritative. Remembering yesterday's venue does not give an AI permission to announce it as today's venue.

## Do I actually need streaming?

AI chat interfaces often display generated text token by token. My first instinct was to plan for that too.

Then I considered what Campusly AI will actually do. A president might ask for registration statistics, request an activity draft, or prepare a notice about a change of venue. In these cases, I want a complete answer or a structured draft that can be reviewed and validated.

Watching a JSON object arrive one fragment at a time is not part of the product experience I'm trying to create.

So I decided not to stream responses. The interface will show a loading state while the assistant works and display the complete response when it is ready. Timeouts, failures and safe retries still need attention.

Most personal assistant requests should be bounded and short enough for an ordinary HTTP request-response flow. This doesn't mean every model call will be fast, or that asynchronous work is forbidden. Later, group messages will need reliable background processing so an AI outage cannot interrupt ordinary human messaging.

It just means I don't need to solve that problem before the first president can talk to the assistant.

## The inevitable Python versus Go discussion

Python was an obvious starting point. Campusly's core backend already uses Python, and the AI ecosystem has excellent libraries such as [Pydantic AI](https://ai.pydantic.dev/) and [AgentScope](https://github.com/agentscope-ai/agentscope).

Go was interesting for a different reason. I already have a Go WebSocket gateway in the messaging infrastructure, and I wanted to explore another part of the cloud-native service stack. During the discussion, I came across [Eino](https://github.com/cloudwego/eino), an open-source Go AI application framework from the CloudWeGo ecosystem, originating at ByteDance.

One thing I had to keep straight was the difference between running an agent and running a model.

The initial Campusly AI service will call hosted model APIs. It will not execute neural networks on a GPU. Its job is to manage requests, supply appropriate context, call tools when needed, validate results and enforce workflow boundaries.

A faster application runtime does not automatically make a remote language model generate a response faster. The model call may dominate end-to-end latency. Go's resource usage and concurrency behavior are interesting, but I haven't measured any advantage for this application yet.

For now, I've settled on Go as the direction for the production AI service, with Eino as the leading framework to validate. Python is still useful for future evaluation scripts, data analysis and ML experiments.

I don't need to make one language responsible for everything.

## What if my coding agent doesn't understand the framework?

Since I'm using AI coding agents extensively during development, I had another question: what happens if an agent confidently writes an API call that doesn't exist in the version of Eino I've installed?

This is not a reason to choose a framework purely because a language model has seen it more often. It is a reason to improve the development workflow.

Eino has [official examples](https://github.com/cloudwego/eino-examples), an [LLM-oriented documentation index](https://github.com/cloudwego/eino/blob/main/llms.txt), and framework guidance for coding agents in the [eino-ext repository](https://github.com/cloudwego/eino-ext/tree/main/skills).

I want agents to work from the installed version's documentation and source, not just their recollection of how a library is supposed to work. The Go compiler can catch many invalid API calls and incompatible types, while focused tests must catch incorrect behavior. Neither one automatically catches a bad architecture or a missing authorization check.

My next engineering step is a small Eino validation, not a three-framework rewrite. I want to check complete responses, synthetic testing, tool calling, structured outputs and failure handling before committing to it as the framework.

## One server is enough to start

The planned initial architecture is fairly small:

```text
Campusly UI
     |
Campusly Core (FastAPI) ---- existing messaging infrastructure
     |
Campusly AI service (Go)
     |
Hosted model API
```

Campusly Core remains the authority for official data, permissions and operational writes. The AI service helps prepare answers and proposed actions. It does not acquire administrative authority merely by generating a convincing response.

Initially, I can run the services together on one server. Their logical boundaries should still allow them to be deployed and scaled separately later. There is no reason to buy several servers just to demonstrate that the boundaries exist.

When shared group AI arrives, its background worker can be introduced and scaled according to actual demand. For now, a small, working personal assistant is more valuable than an impressive infrastructure diagram.

## Build first, document as we go

I also want this series to reflect the way I'm approaching the project itself.

I'm not building features to manufacture a research result. I want to solve actual engineering problems and keep a record of what happens: the design decisions, alternatives, failures, tests, and eventually measurements. Those records can feed technical blogs and course reports. If the findings are interesting enough to justify a research paper, that can follow too. Formal experiments will still need hypotheses and evaluation methods defined before measurement.

The [Campusly AI repository](https://github.com/chandra-deb/campusly-ai-agent) is public, including the [roadmap](https://github.com/chandra-deb/campusly-ai-agent/blob/main/docs/engineering/MILESTONES.md) and the [decision to develop in vertical slices](https://github.com/chandra-deb/campusly-ai-agent/blob/main/docs/decisions/0002-vertical-slice-delivery.md). The implementation hasn't started yet, and the framework choice is still subject to validation.

The next chapter should have something this one doesn't: executable code.

Preferably followed by a successful response from the assistant.

Preferably.

*To be continued — one small milestone at a time.*

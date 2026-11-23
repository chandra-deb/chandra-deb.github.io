---
layout: post
title: "Designing Campusly AI: From Group Chats to an Organizer Workspace"
description: "Designing Campusly AI to reduce organizer busywork and distractions, leaving more time to create better student activities."
tags:
  - campusly
  - product-design
  - ai
---

*23 November 2026 · Product discovery and UX design notes. This post describes a direction we're exploring, not a released AI feature or a completed implementation.*

I spend time on both sides of Campusly: building the software and helping organize student activities. That combination makes one problem hard to ignore.

Organizing an event rarely means managing just the event.

It means coordinating with teammates, answering student questions, checking registration, communicating changes, following up on unfinished work, and remembering everything that happened along the way.

Usually, that work is scattered across group chats and other tools. One group discusses publicity, another handles technical preparations, and students ask questions in an activity discussion. The organizer becomes the person connecting all of them.

I've been asking myself a different question lately:

**What if Campusly could reduce the time organizers spend coordinating routine work, cut down distractions, and give them more time to make their activities genuinely better?**

This post is a snapshot of our current product thinking. I'm deliberately staying at the user-experience level. The engineering design and experiments deserve their own posts later.

## The problem isn't that we need another chat app

Group chats are useful. People know how to use them, and they're good for quick conversations.

The friction appears *between* conversations.

Imagine preparing a programming competition. You need to know whether the technical team has finished setting up, whether publicity materials are ready, and whether students understand what to bring. You might have to visit several chats, scroll through replies, repeat a question, and then check activity details elsewhere.

Each individual step is small. Together, they consume attention. Constantly switching between chats, checking for updates, and repeating information also breaks concentration. The cost isn't only time; it's the attention that could have gone into improving the activity itself.

A tempting solution would be to build a more powerful group chat inside Campusly. But I don't think that's enough. Replacing one set of chat windows with another doesn't automatically make coordination easier.

The product should understand that these conversations belong to an organization, its teams, and its activities.

That's the opportunity I'm interested in.

## Less administration, more attention for the activity

I don't want to build AI features simply because they make a demo look impressive. The real goal is to **give organizers back time and focus**.

If Campusly can make the routine coordination less demanding, a competition organizer might spend more time improving problem quality and testing the event experience. A workshop team might concentrate on teaching materials and helping participants. A publicity team might have more room for creative work instead of chasing updates across groups.

This isn't about eliminating the human work that makes an activity good. It is about reducing the repetitive overhead around that work.

That's also how I want to judge whether this idea succeeds. It's not enough for an organizer to say the assistant looks useful. We should eventually test whether common coordination tasks take less time, whether people need to switch contexts less often, and whether organizers feel better able to concentrate on the quality of the experience they're creating.

Those are goals to validate, not benefits we've measured yet.

## My current hypothesis: one workspace, three ways to work

We're exploring a combined organizer home with three simple purposes:

1. **See what needs attention.** Replies to an organizer's request, direct mentions, and relevant updates appear without forcing them to inspect every group.
2. **Ask Campusly AI to help.** A personal assistant can answer questions, prepare messages, and help coordinate work across groups the organizer is authorized to access.
3. **Talk to people directly.** Real group conversations stay available. AI is an extension of the workflow, not a requirement for participating in it.

These should feel connected, not like three separate products.

I'm also trying to avoid the familiar trap of designing a home screen that shows *everything*. A large dashboard full of unread counts, AI recommendations, tasks, summaries, and reminders could easily create more noise.

For now, the home should help someone answer a simpler question: **What should I look at or do next?**

## An example: ask, send, receive, follow up

Here's a hypothetical interaction I want to test.

A CESS president opens their personal assistant and says:

> Ask the technical team whether the competition environment is ready.

Campusly AI figures out the intended group, checks whether the president has permission to post there, and prepares a message.

It does **not** send immediately.

The president sees the destination and exact message, edits it if needed, and approves. The message then appears in the actual technical team group **under the president's identity**. Internally, Campusly keeps a record that the message was prepared with AI and approved by that person.

A teammate replies that the environment is ready, but two laptops still need testing.

The president doesn't have to remember which group the assistant used. The combined home can surface the response and link to the original discussion.

From there, the president has a choice: open the group and talk normally, or ask the personal assistant:

> What did they say? Is anything still unresolved?

The assistant summarizes the permitted replies and links back to the source.

No second AI-only copy of the group conversation. No new place where teammates are expected to reply.

This **ask → approve → send → receive → follow up** loop is the first experience I'd want to validate. If it works, the president spends less attention tracking the conversation and more on preparing a successful competition.

## A personal assistant is not the same as a group assistant

Another design decision that took some discussion: who is the AI speaking for?

In the personal assistant, the AI helps *me* do my work. If I approve a message to a team group, I am the sender.

Inside a shared group, the AI is different. It is a visible participant named CampuslyAI. A team member might ask it to draft a checklist; a student might ask it about an activity's venue.

The group AI answers **as AI**, not as the president.

That distinction matters for trust and permissions. A volunteer in a technical team group shouldn't gain president-level privileges just because the president happens to be a member of the same group.

And nobody should need to open a group first just to activate a private assistant with that group's context. From the personal assistant, “What happened in our technical team today?” should be a natural request. Group and activity references can be resolved conversationally, with clarification when ambiguous.

## When should a group AI speak?

I don't want an assistant constantly interrupting human conversations.

For the first proposed version, we've chosen a deliberately small candidate rule:

- If a message explicitly mentions CampuslyAI, consider replying.
- If a message contains a question mark, consider replying.
- Otherwise, do not run the immediate AI reply decision.

Passing that first check does *not* mean the AI must answer. A message like “Haha, really?” has a question mark but probably doesn't need a bot response. The AI still needs to judge whether a reply is useful, grounded, and appropriate.

An explicit mention should usually get an answer or a clear explanation of why the assistant can't help.

This is intentionally modest. We can evaluate whether the AI answers actual student questions without becoming the most talkative member of every group.

## The longer-term idea I'm most excited about: organizational memory

In student organizations, leadership changes. Presidents graduate. Volunteers move on. A team might repeat the same mistakes because the people who learned those lessons are no longer around.

Consider a competition where students repeatedly ask whether they need to bring laptops. That might be a sign that equipment requirements were unclear.

Months later, when another organizer is planning a competition, imagine asking:

> What did we learn from our previous competitions?

Campusly could suggest checking the equipment instructions and point to a reviewed note from the previous event.

That would be more useful than a chatbot that merely remembers the last few messages.

Our current concept separates memory into scopes:

- **Personal memory** for private assistant preferences and continuity.
- **Group working memory** for useful questions, plans, commitments, and unresolved issues from permitted discussions.
- **Organization memory** for reviewed guidance and lessons that future organizers can reuse.

We're considering processing new group messages in scheduled batches, perhaps once or twice a day to start, rather than continuously asking a model to reread everything. Group replies, by contrast, would be triggered when someone mentions the AI or posts a question-mark message.

There is an essential caution here: **conversation is not automatically policy**.

“Maybe we should use Room 302” is an idea, not an official venue change. Even “Let's use Room 302” doesn't necessarily mean the venue was updated in Campusly.

Automatically extracted memories should be provisional and traceable to their sources. Organization-wide guidance should be reviewed by an authorized person. The assistant should retrieve live activity facts from Campusly rather than treating old chat summaries as authoritative.

We also need explicit boundaries for private student inquiries, consent, retention, corrections, and who can see what. Organizational memory must not become a convenient way to bypass privacy.

## Why I'm keeping the human in control

A good assistant should reduce clicks and repeated effort. It shouldn't quietly make consequential decisions for people.

If the organizer asks it to change registration capacity, publish an announcement, or send a message, the proposed action should be visible before approval. The actual system must still enforce the organizer's permissions and the activity's business rules.

And if AI is unavailable, the organizer should still be able to use Campusly normally.

This may sound less futuristic than full autonomy. For a real student organization, I think predictability and accountability are more valuable than a flashy demo.

## Where we are today

Campusly already has real activity-management workflows, and the activity-discussion messaging work provides a foundation for exploring these ideas.

**The AI organizer workspace, internal team groups, cross-group inbox, group AI, and memory system described here are product directions—not features I'm claiming are deployed.** The exact group-management rules, permission details, memory safeguards, and rollout plan still need more design work.

The next step isn't to implement every exciting possibility at once.

I want to prototype one complete organizer journey: ask the assistant, review a message, send it to a real group, receive replies, and follow up without losing context. Then I can observe whether it actually saves effort and makes sense to other organizers—not just to me.

If that journey works, we have a foundation to build on. If it feels confusing, we'll have learned something useful before scaling the idea.

## A note to my future self

I'm writing this down now because ideas become surprisingly difficult to reconstruct after a few weeks of coding.

The goal is not “add AI to Campusly.”

The goal is to **spend less time managing the process and more time improving the activity**: fewer distractions, less repetitive coordination, better continuity when people leave, and more attention for the experiences organizers are trying to create.

I don't yet know how much time this can save or how directly it will affect activity quality. That's what the prototype and real organizer feedback need to establish.

Everything else—including the assistant interface—is a means to that end.

*This is a product/UX design checkpoint. I'll document the architecture, implementation decisions, failures, and measurements separately when there's actual engineering evidence to discuss.*

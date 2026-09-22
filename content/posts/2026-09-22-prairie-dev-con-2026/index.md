---
title: "Prairie Dev Con 2026: Thank you, Winnipeg"
date: "2026-09-22"
draft: true
categories:
  - "Speaking"
tags:
  - "Prairie Dev Con"
  - "Conferences"
  - "AI"
  - "GitHub Copilot"
  - "Agent Skills"
  - "Plugins"
permalink: "/posts/prairie-dev-con-2026/"
slug: "prairie-dev-con-2026"
image: "featured.svg"
featureImage: "featured.svg"
header:
  teaser: "featured.svg"
  og_image: "featured.svg"
excerpt_separator: "<!--more-->"
description: "Thanks to the Prairie Dev Con organizers and sponsors, and a look at my new talk on agent skills, plugins, and marketplaces."
---

It's good to be back in Winnipeg for [Prairie Dev Con](https://www.prairiedevcon.com/), September 21-22, 2026. This year, I brought a new talk: **Agent Skills, Plugins & Marketplaces**. We got into a discussion about agents, reusable workflows, and how to share those workflows with a team. Thank you to everyone who asked questions and joined in.

<!--more-->

## Thank you to the organizers and sponsors

Thank you to D'Arcy Lussier and the organizing team for having me back. Putting together a conference takes a lot of work that attendees never see. I appreciate the time and care that go into making these two days happen.

Thank you as well to the [2026 sponsors](https://www.prairiedevcon.com/#sponsors-section):

- [Payworks](https://www.payworks.ca/)
- [Improving](https://www.improving.com/)
- [WorkWranglers](https://www.workwranglers.com/)
- [Laivly](https://laivly.com/)
- [Conquest Planning](https://conquestplanning.com/en-ca)
- [Pollard Banknote](https://www.pollardbanknote.com/)
- [Skip](https://www.skipthedishes.com/)
- [Richardson International](https://www.richardson.ca/)
- [Carahsoft/Google](https://www.carahsoft.com/markets/canada)

And thanks to [New Media Manitoba](https://newmediamanitoba.com/), the conference's community partner. That support helps bring developers together to learn in person.

To everyone making time for the conference: thank you. Being able to share what I'm working on with other developers is a big part of why I keep speaking.

## My new talk: Agent Skills, Plugins & Marketplaces

I want to spend less time re-explaining a workflow every time I start a conversation with an AI assistant. Once I've worked out a useful approach, I want to keep it in source control, improve it, and share it with someone else.

That's the problem behind this talk. A prompt that works once is useful. A workflow someone else can find, understand, and use is worth maintaining.

## Agents and skills have different jobs

An agent carries out the work: it reasons about the request, uses the tools available to it, and works through the task. A custom agent profile lets us specialize that behavior with a role, instructions, and a configured set of tools.

A skill describes how to do a particular job. It starts with a `SKILL.md` file and can include scripts, reference material, or templates. Loading a skill gives the agent a procedure to follow. It doesn't create another agent, launch a separate worker, or grant new permissions.

That distinction came into the discussion because there are several ways to customize an assistant. Project instructions are a place for recurring guidance, such as coding conventions. An agent profile defines a role. A skill holds a task-specific workflow. You can use a skill with a general coding agent; you don't have to build a custom agent first.

Context is part of that choice, too. An assistant has a limited amount of information it can work with at once. In the usual loading model, the host makes skill names and descriptions available first, then loads the full instructions when a skill is selected. Supporting resources can be read when needed. That gives us somewhere to put detailed procedures without loading every procedure into every conversation.[^skills]

## What makes a skill reusable?

The first example in the talk is a release-note skill. The whole thing is one `SKILL.md` file. That's enough to explain the task and the output I want, and it's small enough to read in one sitting.

For a skill to be useful to someone else, it needs to say when it applies, what information it needs, and what a good result looks like. Instructions that depend on an unexplained local path or knowledge from an earlier conversation won't travel very well.

The CSV analysis example adds supporting files because the task needs them: a Python profiler, a methodology reference, and a report template. The script handles the calculations, while the instructions explain how to use the results. That lets us check the arithmetic separately from whether the assistant produces a useful explanation.

A well-written skill still needs to be tried on real inputs. Does the agent choose it for the right task? Does it ask for missing information? Does the result match what we asked for? Those are different checks from whether a script runs successfully.

I like starting small here. Pick a task you repeat, write down how you want it done, and try it. Add supporting files when they solve a problem. The [demo repository](https://github.com/codebytes/agent-skills) includes both examples so you can compare them.

## Getting skills into other people's hands

Distribution deserves as much thought as authoring. A skill sitting on my machine only helps me.

For a workflow that belongs to one project, committing the skill alongside the code is a useful starting point. Teammates get the same files, can review changes in a pull request, and can improve the workflow together. For something I use across my own projects, a supported personal skills directory may be enough.

When several projects or people need the same capabilities, a plugin gives us an installable package. It can hold skills and, depending on the host, custom agents, hooks, and MCP server configuration. A marketplace is a catalog where people can discover and install those packages.[^plugins]

That gives us a way to maintain a shared source instead of passing around copies that gradually drift apart. It also creates some ordinary maintenance work: deciding who owns the package, versioning changes, and giving people a way to tell what changed before they update.

The Agent Skills format is an open standard, but installation still depends on the tool. Discovery paths, marketplace formats, and permissions differ between clients. A Copilot-specific agent or hook doesn't automatically become portable because it's packaged alongside a skill. The talk includes host-specific setup so we can share the reusable parts while being clear about those differences.

I also cover reviewing what you install. If a plugin includes scripts, hooks, or MCP integrations, look at what can run and what data it can access. Instructions about safe behavior aren't a substitute for permissions or for checking the output.

## The questions and discussion

I really appreciated the audience's engagement with this new talk. The questions gave us time to dig into agents, what makes a skill reusable, and how to get those skills into other people's hands.

Those topics connect quickly. Choosing what an agent should do affects which workflows are worth turning into skills. Sharing a skill means thinking about someone who wasn't there when you wrote it. Distributing it means taking responsibility for changes after that first install.

That's why I enjoy the discussion around a talk like this. Showing the files is useful, but talking through how people might use them gives us more to work with. Thank you to everyone who asked a question or contributed to the conversation.

## Slides and examples

If you'd like to try the examples or revisit the material:

- [View the slides](https://chris-ayers.com/agent-skills/)
- [Download the slides as a PDF](https://chris-ayers.com/agent-skills/Slides.pdf)
- [Get the talk source and demo plugin](https://github.com/codebytes/agent-skills)
- [Browse my reusable skills](https://chris-ayers.com/skills/)

[^skills]: GitHub Docs: [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills).
[^plugins]: GitHub Docs: [About GitHub Copilot plugins](https://docs.github.com/en/copilot/concepts/agents/about-plugins).

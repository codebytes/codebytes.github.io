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

It's good to be back in Winnipeg for [Prairie Dev Con](https://www.prairiedevcon.com/), September 21-22, 2026. This year, I'm sharing a new talk: **Agent Skills, Plugins & Marketplaces**. It's about taking the useful things we teach our AI assistants and making them easier to reuse and share.

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

That's the problem behind this talk. The pieces have different jobs:

- A skill describes how to do a particular task. It starts with a `SKILL.md` file and can include scripts, reference material, or templates.
- A plugin packages capabilities so someone else can install them. Depending on the host, that can include skills, custom agents, hooks, and MCP server configuration.
- A marketplace gives people a place to discover and install those plugins.

The talk also covers context: what an assistant needs to know now, and what it can load when a task calls for it. Keeping every instruction in every prompt gets unwieldy. Skills give us a way to make more detailed guidance available when it's relevant.[^skills]

## Start with one file

The first example in the talk is a release-note skill. The whole thing is one `SKILL.md` file. That's enough to explain the task and the output I want.

The next example adds more because the task needs it: a CSV analysis skill with a Python profiler, a methodology reference, and a report template. The script handles the calculations, while the instructions explain how to use the results.

I like that progression because it gives people somewhere small to start. Pick a task you repeat, write down how you want it done, and try the skill on a real example. Add supporting files when they solve a problem.

From there, the talk follows the examples through checking their behavior, packaging them as a plugin, and making them available through a marketplace. The [demo repository](https://github.com/codebytes/agent-skills) includes both skills and the host-specific setup.

## Sharing still takes some care

The Agent Skills format is an open standard. That doesn't mean every host discovers skills in the same place or supports the same plugin features. Install commands, marketplace formats, and permissions still depend on the client.

That distinction matters when a team uses more than one assistant. Share the skill where you can, then check the setup in the tools people actually use. A Copilot-specific agent or hook doesn't automatically become portable just because it's packaged alongside a skill.[^plugins]

I also cover reviewing what you install. If a plugin includes scripts, hooks, or MCP integrations, look at what can run and what data it can access. Instructions about safe behavior aren't a substitute for permissions or for checking the output.

## Slides and examples

If you'd like to try the examples or revisit the material:

- [View the slides](https://chris-ayers.com/agent-skills/)
- [Download the slides as a PDF](https://chris-ayers.com/agent-skills/Slides.pdf)
- [Get the talk source and demo plugin](https://github.com/codebytes/agent-skills)
- [Browse my reusable skills](https://chris-ayers.com/skills/)

[^skills]: GitHub Docs: [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills).
[^plugins]: GitHub Docs: [About GitHub Copilot plugins](https://docs.github.com/en/copilot/concepts/agents/about-plugins).

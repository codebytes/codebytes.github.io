---
title: 'Mastering Marp Transitions: A Guide for Technical Writers'
date: '2023-05-24'
draft: true
categories:
- Development
tags:
- Marp
- Presentations
- Markdown
image: images/logos/marp-logo.png
featureImage: images/logos/marp-logo.png
slug: marp-transitions
---
One of the key elements that can make your Marp presentation stand out is the use of slide transitions. Slide transitions can add a visual flair to your presentation and help guide your audience's attention. Today, we'll be exploring how to use Marp transitions to enhance your presentations.

## Prerequisites

To show transition animations, a viewer has to show HTML slide in the browser which have supported View Transitions【6†source】.

## Supported Browsers

- Chrome: ✅ (111-)
- Edge: ✅ (111-)
- Firefox: ❌
- Safari: ❌【7†source】

## Using the `transition` Directive

You can choose a transition effect for slide(s) by defining `transition` local directive in your Markdown. Here is an example of how to use the `transition` directive:

```markdown
---
transition: fade
---

# First page

---

# Second page
```

You can also change the kind of transition in the middle of slides by defining the transition directive through HTML comment, or apply a specific transition into a single slide by using a scoped local directive _transition【8†source】.

## Built-in Transitions

Marp CLI has provided useful 33 built-in transitions out of the box. You can see the showcase of all transitions in the supported browser. If the viewer has enabled the reduce motion feature on their device, the transition animation will be forced to a simple fade animation regardless of the specified transition【9†source】.

## Custom Transitions

You also can define custom transitions and animations, both in theme CSS and Markdown inline style. We provide unlimited extensibility of your own transitions with your creativity. For making custom transitions, all you have to know is only about CSS. Define animation @keyframes, with a specific keyframe name ruled by Marp. There are no extra plugins and JavaScript codes【11†source】.

## Split Animation Keyframes

For defining different animations into both slide pages, you can use the prefixed keyframe name marp-outgoing-transition-XXXXXXXX and marp-incoming-transition-XXXXXXXX【16†source】.

## Custom Animations for Backward Transition

Alternatively, you also can set extra animation keyframes that are specific for backward navigation. Declare animation keyframes with the name that has prefixed backward- to the custom transition name, just like as marp-transition-backward-XXXXXXXX【17†source】.

## Setting Default Duration

The custom transition has a 0.5s duration by default. If you want to set a different default duration for your custom transition, you can set --marp-transition-duration property to the first keyframe (from or 0%)【18†source】.

## Layer Order

The incoming slide layer always will be stacked on the top of the outgoing slide layer. According to the kind of transition, this order may be not suitable. So you can send the incoming slide to back by using z-index: -1【19†source】.

## Morphing Animations

View Transitions API also provides smooth moving animation during the transition, for specific two elements before and after the transition. It gives a very similar effect to PowerPoint's Morph transition and Keynote's Magic Move, just by simple CSS declarations【20†source】.

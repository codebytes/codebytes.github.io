---
title: Some Tools to Help Present Git
date: 2020-02-23T00:27:33+0000
categories:
- Development
tags:
- Git
- terminal
image: images/git-logo.png
featureImage: images/git-logo.png
aliases:
- /2020/02/23/some-tools-to-help-present-git/
- /development/devops/tools/some-tools-to-help-present-git/
slug: some-tools-to-help-present-git
---
{{< figure src="/images/git-logo.png" >}}

I'm presenting soon on Advanced Git. I feel a lot of Developers and DevOps engineers know enough git to the job, but sometimes that's it. I want to help people be more comfortable with the git command-line, and help alleviate some fear or hesitation in dealing with git edge cases.

While researching things, I came across a few neat tools I'm using to help describe things.

- [GitGraphJs](https://gitgraphjs.com/)
- [Windows Terminal](https://github.com/Microsoft/Terminal)
- [Oh My Posh](https://github.com/JanDeDobbeleer/oh-my-posh)/[ohmybash](https://ohmybash.github.io/)/[ohmyzsh](https://github.com/ohmyzsh/ohmyzsh)
- Git GUIs
  - [Fork](https://fork.dev/)
  - [GitKraken](https://www.gitkraken.com/)

## [GitGraphJS](https://gitgraphjs.com/)

What is great about this tool is that I can draw git commit graphs pretty easily to describe what is happening as you execute commands. It helps create great graphs like this:

{{< figure src="/images/gitgraphjs.png" >}}

I've got a project where i can have each example laid out for discussion, and because its JavaScript, I can change things and show the result easily. This tools is great for slides and lecturing, but I also like having people put hands on keyboards and _try_ things.

## [Windows Terminal](https://github.com/Microsoft/Terminal)

I do a lot of development on windows. CMD.exe isn't the best experience to use or present with. The same can be said of regular powershell. I've leveraged git bash in the past, it works pretty well. But I have completely fallen in love with the Windows Terminal. Multiple profiles (for bash, wsl, powershell, cmd), a great font, and nice scalability, I've finally found a nice shell on windows.

{{< figure src="/images/terminal-panes.gif" >}}

## Oh My \_\_\_\_\_\_\_

If you aren't familiar with [Oh My Posh (powershell)](https://github.com/JanDeDobbeleer/oh-my-posh), [Oh My Bash (bash)](https://ohmybash.github.io/), or [Oh My Zsh (zsh)](https://github.com/ohmyzsh/ohmyzsh) please pay attention. These tools add some awareness to your shell experience. If you 'cd' into git folders, it can show the branch, how far ahead or behind you are, and many other details. It gives you situational awareness about where you are and your current state. There are also many themes to tweak and customize your command-line.

{{< figure src="/images/oh-my-x.png" >}}

## Git GUIs

I don't use git GUIs in my day to day workflow. I typically interact with git via a command-line. But there are some times when a gui is very helpful. Complex merges and rebases can be made clearer via gui, as well as a clear visualization of the git history. Don't get me wrong, I can do that via command-line:

```bash
git log --pretty=oneline --graph --decorate --all
```

{{< figure src="/images/git-log.png" >}}

But these tools make it much cleaner, clearer, and prettier.

{{< figure src="/images/git-kraken.png" >}}

I'm a big fan of tools that help me share ideas more effectively and these are a few that I think will help me explain git state.

---
#layout: post
title: Presenting with VS Code - Screencast mode
date: 2019-10-06 11:58:28.000000000 +00:00
type: post
categories:
- Tools
tags:
- code
- presenting
- speaking
- vscode
permalink: "/2019/10/06/presenting-with-vs-code-screencast-mode/"
---

I have been starting to speak and present a lot more, and was looking into great tools like [Carnac](http://carnackeys.com/) and [KeyPosé](https://github.com/AxDSan/KeyPose). But I just found out today about a feature I didn't know existed inside Visual Studio Code, [Screencast mode](https://code.visualstudio.com/updates/v1_31#_screencast-mode). This was introduced in January 2019. How did I miss it?

To enable and use Screencast mode, Open the command palette, Ctrl + Shift + P.

{% include figure image_path="/assets/images/enable-screencast-mode.png" alt="Command Palette - Screencast Mode" caption="Command Palette - Screencast Mode" %}

{% include figure image_path="/assets/images/screencast-unconfigured.png" alt="Screencast Mode" caption="Screencast Mode" %}

When first enabled, Screencast Mode is not what I wanted. It shows _EVERY_ keypress. It also shows a little higher on the screen that I prefer. It also puts a little red circle everywhere I click the mouse, which is nice. Let's configure it and see if we can clean up some of that. Open the command palette again (Ctrl + Shift + P) and go to the user settings.

{% include figure image_path="/assets/images/10/open-user-settings.png" alt="Command Palette - Settings" caption="Command Palette - Settings" %}

{% include figure image_path="/assets/images/10/screencast-settings.png" alt="Settings - Screencast Mode" caption="Settings - Screencast Mode" %}

There aren't a lot of options right now, but I only want to see keyboard shortcuts.. Ctrl+C, Ctrl+V, Alt+Shift+F. So I'll check that, and I want it a little lower on the screen, so I lowered the default from 20 down to 5. Let's see the finished product:

{% include figure image_path="/assets/images/10/screencast-configured.png" alt="Screencast Mode - Configured" caption="Screencast Mode - Configured" %}

Awesome. I can now go on a mac, linux, or windows machine and have a consistent experience with sharing my keypresses and mouse clicks. If you present, live code, or give demos, this is a great feature to enable and I encourage you to do so. Seeing all the keyboard shortcuts people use is a great thing to learn.

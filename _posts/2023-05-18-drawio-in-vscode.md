---
title: Embedding Draw.io Diagrams in VS Code
type: post
categories:
- tools
tags:
- vscode
- draw.io
- markdown
- presentations
- tools
permalink: /2023/05/18/drawio-in-vscode
header:
  teaser: /assets/images/drawio-logo.png
  og_image: /assets/images/drawio-logo.png
excerpt_separator: <!--more-->
---

In the universe of software development, tools that can streamline our workflows are invaluable. Today, I'd like to shine a spotlight on an extraordinary member of this universe: Visual Studio Code (VSCode). As a big fan of VSCode, I've had the pleasure to explore a myriad of its extensions and tools designed to enhance the programming experience. VSCode isn't just a code editor; it's a versatile platform capable of accommodating a variety of tasks such as blogging, creating presentations, and crafting README files for projects.

Among the tools I've tested, one that has truly left a lasting impression is Draw.io, a free online diagram software. Draw.io isn't your average diagramming tool. It's a platform that allows users to transform their abstract ideas and complex workflows into intuitive and straightforward diagrams. For developers who frequently use VSCode for tasks like writing blog posts in markdown, designing slide decks using MARP, or detailing project README files, integrating Draw.io can be a game-changer. This integration becomes seamless with the [`hediet.vscode-drawio`](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio) extension, a powerful bridge that connects the world of diagrams to your favorite code editor.

Draw.io is known for its ease of use and broad range of features, allowing users to create flowcharts, process diagrams, org charts, UML, ER diagrams, network diagrams, and much more. The `hediet.vscode-drawio` extension brings this functionality directly to your VSCode environment. 

![draw.io demo](/assets/images/drawio-demo.gif)

The significant advantage of this integration is that you can create and edit diagrams without needing to switch between your code editor and a separate diagramming tool. This seamless integration boosts productivity and maintains the flow of work.

One of the *best* features of the `hediet.vscode-drawio` extension is its unique way of saving diagrams. You can save your diagrams as `drawio.png` or `drawio.svg` files. These file formats not only store the diagram as an image but also preserve the diagram data within the image metadata. This means you can share the diagrams as images with others, and they can view them using any standard image viewer. If they also use Draw.io or the `hediet.vscode-drawio` extension, they can even edit the diagrams, as the image file still contains the original diagram data. This is an innovative approach to sharing editable diagrams that maintains their visual accessibility.

Making the most of Draw.io within VSCode involves not only leveraging the diagramming functionality but also efficiently managing and integrating your diagrams into your projects. Here are a few tips and tricks to help you maximize the use of Draw.io within VSCode:

- **Save diagrams as `drawio.png` or `drawio.svg` files**: Regularly saving your diagrams in these formats ensures that you don't lose your work. These formats also keep the diagram data within the image metadata, allowing you (or others) to edit the diagrams later.

- **Integrate diagrams into your Git repository**: Once you've saved your diagrams as `drawio.png` or `drawio.svg` files, you can easily add them to your Git repository. This makes it easy to version control your diagrams alongside your code, and share them with others through the repository.

- **Reference diagrams directly in your markdown files**: Once your diagrams are in your Git repository, you can reference them directly in your markdown files (such as README files, blog posts, or MARP presentations). This can be done with the standard markdown image syntax, `![Alt text](url)`, where `url` is the path to your `drawio.png` or `drawio.svg` file in the repository. This allows you to seamlessly integrate visual content into your written content.

- **Explore Draw.io's shape and icon libraries**: Draw.io offers a broad library of shapes and icons. These can help make your diagrams more visually appealing and easier to understand. Different shapes can represent different elements in your diagrams, making them more intuitive to read.

- **Use color and style strategically**: Different colors and styles can help you differentiate between different elements in your diagrams. Using them wisely can increase the clarity of your diagrams and make them easier to interpret.

By implementing these tips and tricks, you can effectively manage your diagrams and integrate them into your development workflow, enhancing communication and understanding within your team.

In conclusion, the integration of Draw.io into VSCode via the `hediet.vscode-drawio` extension offers a powerful and efficient way to create diagrams. This feature-rich extension allows developers and other professionals to visualize their ideas and workflows without disrupting their coding environment. Moreover, the unique `drawio.png` and `drawio.svg` file formats ensure that your diagrams are both visually accessible and editable. This integration is a testament to how flexible and extensible the VSCode platform can be, catering to a wide range of user needs beyond just writing code.

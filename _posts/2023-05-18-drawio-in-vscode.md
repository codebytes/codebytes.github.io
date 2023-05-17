---
title: Embedding Draw.io Diagrams in VSCode
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

If you're like me and love discovering new ways to boost your productivity in VSCode, then you're in for a treat today. Let's talk about a tool that has significantly elevated my VSCode experience: [Draw.io](https://draw.io) and the [`hediet.vscode-drawio`](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio) extension.
<!--more-->

## Draw.io

Draw.io is no ordinary diagram software. It's a powerful platform that lets us turn abstract ideas and intricate workflows into clear, easy-to-understand diagrams. And the best part? We can now integrate this fantastic tool directly into our VSCode environment, thanks to the [`hediet.vscode-drawio`](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio) extension. This extension is a game-changer, enabling us to create and edit diagrams right within our favorite code editor.

![draw.io demo](/assets/images/drawio-demo.gif)

## The `hediet.vscode-drawio` Extension

Draw.io is known for its ease of use and a comprehensive range of features, enabling users to create flowcharts, process diagrams, org charts, UML, ER diagrams, network diagrams, and much more. The `hediet.vscode-drawio` extension transports this rich functionality right into your VSCode environment, allowing you to create and edit diagrams without the need to toggle between your code editor and a separate diagramming tool. This integration not only boosts productivity but also sustains the momentum of your workflow.

One of the standout features of the `hediet.vscode-drawio` extension is its unique approach to saving diagrams. Diagrams can be saved as `drawio.png` or `drawio.svg` files. These file formats store the diagram as an image and keep the diagram data intact within the image metadata. This innovative feature allows you to share diagrams as images, viewable using any standard image viewer. If the recipients also use Draw.io or the `hediet.vscode-drawio` extension, they can even edit the diagrams, thanks to the original diagram data preserved in the image file.

## Tips

To truly maximize the use of Draw.io within VSCode, you should not only leverage the diagramming functionality but also manage and integrate your diagrams effectively into your projects. Here are a few tips and tricks:

- **Save diagrams as `drawio.png` or `drawio.svg` files**: Regularly saving your diagrams in these formats ensures you don't lose your work. These formats also allow you (or others) to edit the diagrams later, courtesy of the diagram data stored within the image metadata.
 ![Sample drawio.png](/assets/diagrams/sample.drawio.png)

- **Integrate diagrams into your Git repository**: After saving your diagrams as `drawio.png` or `drawio.svg` files, you can conveniently add them to your Git repository. This integration allows you to version control your diagrams alongside your code and share them with others through the repository.

- **Reference diagrams directly in your markdown files**: Once your diagrams are stored in your Git repository, they can be directly referenced in your markdown files. This includes README files, blog posts, or MARP presentations. To do this, use the standard markdown image syntax, `![Alt text](url)`, where `url` is the path to your `drawio.png` or `drawio.svg` file in the repository. This technique enables a seamless integration of visual content into your written material.

- **Explore Draw.io's extensive shape and icon libraries**: Draw.io provides a vast library of shapes and icons that can help make your diagrams visually appealing and intuitive. Different shapes can represent various elements in your diagrams, enhancing their readability.

- **Use color and style strategically**: Utilizing different colors and styles can aid in distinguishing between different elements in your diagrams. Strategic use of these features can improve the clarity of your diagrams and make them easier to interpret.

By adopting these tips and tricks, you can effectively manage your diagrams and seamlessly integrate them into your development workflow. This not only enhances communication within your team but also promotes a better understanding of the concepts you're working with.

## Other Features

Besides the features I've covered so far, the [`hediet.vscode-drawio`](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio) extension also provides a host of other functionalities. These include:
- Offline support: By default, the extension uses an offline version of Draw.io.

- Themes: Multiple Draw.io themes are available for users to choose from.

- Collaboration: The extension supports collaborative editing of diagrams using VS Code Liveshare. Users can edit and present diagrams remotely, with participants able to see each other's cursors and selections.

- Code link feature: The extension includes a code link feature where users can enable or disable linking nodes/edges with code spans. Double-clicking on a node with a label starting with "#" performs a workspace search for a matching symbol, allowing users to jump to its source code.

## Conclusion

In conclusion, the [`hediet.vscode-drawio`](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio) extension facilitates the integration of Draw.io into VSCode, providing a powerful and efficient way to create and manipulate diagrams. This feature-rich extension enables developers and other professionals to visualize their ideas and workflows without leaving their coding environment. Furthermore, the unique `drawio.png` and `drawio.svg` file formats ensure that your diagrams remain visually accessible and editable, making sharing and collaboration easier. This integration is a shining example of the flexibility and extensibility of the VSCode platform, demonstrating its ability to cater to a wide range of user needs, well beyond just writing code.

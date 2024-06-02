---
title: Writing Regex with Copilot
type: post
categories:
- Development
tags:
- regex
- copilot
permalink: /2024/4/09/regex-with-copilot
header:
  teaser: /assets/images/github-copilot-logo.png
  og_image: /assets/images/github-copilot-logo.png
excerpt_separator: <!--more-->
---

I had a real world example today that I wanted to share about copilot helping me with a coding problem. A friend reached out asking if I knew regex. Its been a bit, but I was happy to help because I thought we could figure it out.<!--more-->

## The Problem

Her use case was that she had a string and she wanted to match a word only if another word appeared before it. She works at a University and is doing improvements to the CMS templates. They needed to do some updates to a Template only if it included certain tags. She was able to give me a sample that I could work with.

She was able to boil it down to a simple example. Given the sample, 'I think puppies are super cute, but turtles are super cute too.'  make a regex that matches turtles only if puppies appears before it.

## The Solution

Its been a while so I used GitHub Copilot Chat to help me out.

>> Given the sample, 'I think puppies are super cute, but turtles are super cute too.' Make a regex that matches turtles only if puppies appears before it.
>
> Sure, here is a regular expression that matches “turtles” only if “puppies” appears before it in the text:
>
> `puppies.*turtles`
>
> This regular expression works as follows:
>
> puppies matches the characters “puppies” literally.
> .* is a special sequence that matches any character (except for a newline) 0 or more times.
> turtles matches the characters “turtles” literally.
>
> So, this regular expression will match any string that has “turtles” somewhere after “puppies”.

We are using regexer.com to test out the regexes. The result was close but we got in a back and forth refining the regex.

![Testing regexes on regexer.com](/assets/images/regex-copilot-1.png)

>> I want to match and return only the word turtles, not additional text.
> To match and return only the word "turtles", but only if "puppies" appears before it in the text, you can use a lookahead assertion in your regular expression. Here's how you can do it:
>
> `(?<=puppies.*)(turtles)`
>
> This regular expression works as follows:
>
> `(?<=puppies.*)` is a positive lookbehind assertion that checks for the presence of "puppies" followed by any characters before the main expression.
> `(turtles)` is the main expression that matches the word "turtles".
> So, this regular expression will match the word "turtles" only if it appears somewhere after the word "puppies", but it will only return "turtles".

Awesome!
![matching turtles](/assets/images/regex-copilot-2.png)

![not matching turtles](/assets/images/regex-copilot-3.png)

## Done, Or Are We?

My friend then threw a curveball at me. She wanted to match turtles only if puppies appears even if there are line breaks or other paragraphs. Like in this sample:

'I think puppies are super cute,<br /> but turtles are super cute too.'

Let's see if we can modify the regex to match this.

>> Given the sample, 'I think  are super cute, but puppies turtles are super cute too.' and the regex `(?<=puppies.*)(turtles)` I would like this to match turtles only if puppies appears even if there are line breaks or other paragraphs.. Like in this sample:
>> 'I think puppies are super cute,
>> but turtles are super cute too.'
>
> The regular expression `(?<=puppies.*)(turtles)` you provided uses a positive lookbehind `(?<=puppies.*)` to check if “turtles” is preceded by “puppies”. However, the . character does not match line breaks in regular expressions.
>
> To match “turtles” only if “puppies” appears before it, even if there are line breaks or other paragraphs, you can use the `[\s\S]*` pattern instead of .*. The `[\s\S]` pattern matches any character including line breaks. Here’s how you can modify your regex:
>
> `(?<=puppies[\s\S]*)(turtles)`
>
> This will match “turtles” only if “puppies” appears before it, regardless of line breaks or other paragraphs. For example, it will match “turtles” in the following text:
>
> I think puppies are super cute,
> but turtles are super cute too.
>

Lets try this out.

![matching turtles same line](/assets/images/regex-copilot-4.png)

![matching turtles different lines](/assets/images/regex-copilot-5.png)

![not matching turtles](/assets/images/regex-copilot-6.png)

Everything looks like its working.

## Conclusion

At this point, my friend had told me she had spent over an hour on stack overflow and other sites trying to figure this out. She had been hesitant to use GitHub Copilot but I think this was her aha moment. We literally solved her problem in under 5 minutes.

I have been using it for a while now and I am happy with the results. I don't worry as much about syntax, I'm really more focused on **WHAT** I want to do and not **HOW** to do it. I think this is a game changer for me. I'm excited to see how this tool evolves.

If you haven't tried out GitHub Copilot, I would recommend it. [https://github.com/features/copilot](https://github.com/features/copilot)

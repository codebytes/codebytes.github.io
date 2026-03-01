---
title: Validating .NET Configuration
date: '2022-12-03'
categories:
- Development
tags:
- dotnet
- configuration
image: images/logos/dotnet-logo.png
featureImage: images/logos/dotnet-logo.png
aliases:
- /2022/12/03/validating-dotnet-configuration/
- /development/dotnet-configuration/
slug: dotnet-configuration
---
{{< figure src="/images/logos/csadvent logo.png" alt="C# Advent" class="float-left m-4" >}}

**This blog was posted as part of the [C# Advent Calendar 2022](https://www.csadvent.christmas/). I really want to thank [Matthew D. Groves](https://twitter.com/mgroves) and [Calvin Allen](https://twitter.com/_calvinallen) for helping set this up! Look for #csadvent on Twitter! Make sure to check out everyone else's work when you're done here**

One of the great things about the configuration system in .NET is the type safety, dependency injection, and model binding. Something we can take advantage of is to validate our configuration on startup and fail if it doesn't pass validation. Having that fast failure is awesome when working with containers and applications that have liveness and readiness probes.

I have some examples of the amazing configuration system in my [GitHub repository](https://github.com/Codebytes/dotnet-configuration-in-depth) I use for my [.NET Configuration in Depth](https://github.com/Codebytes/dotnet-configuration-in-depth) conference talk. Feel free to take a look at the samples found there.

But let's get to the topic at hand. How do we validate our configuration in .NET?

Let's start with some configuration we'll be wanting to validate and actually fail on startup if its not there.

```json
 "WebHook": {
    "WebhookUrl": "http://example.com/event",
    "DisplayName": "DevOps",
    "Enabled": true
  }
```

And let's have a strongly typed class to hold that configuration.

```cs
using System.ComponentModel.DataAnnotations;

public class WebHookSettings
{
    public string WebhookUrl { get; set; }
    public string DisplayName { get; set; }
    public bool Enabled { get; set; }
}
```

Now how do we _KNOW_ our URL is valid? We can add some validation to our application pretty easily leveraging Data Annotations! This lets us mark fields as required as well as doing other validation. There are a ton of build in attributes, like StringLength, Range, EmailAddress, and more. You can find some of them listed in the [documentation](https://learn.microsoft.com/en-us/dotnet/api/system.componentmodel.dataannotations?view=net-7.0) if you're curious.

Let's extend our class to add that basic validation.

```cs
using System.ComponentModel.DataAnnotations;

public class WebHookSettings
{
    [Required, Url]
    public string WebhookUrl { get; set; }
    [Required]
    public string DisplayName { get; set; }
    public bool Enabled { get; set; }
}
```

For my example, I'm using minimal APIs, and I can enable validation using just a few lines of code to invoke a few extension methods.

```cs
using System.ComponentModel.DataAnnotations;
using Microsoft.Extensions.Options;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOptions<WebHookSettings>()
    .BindConfiguration("WebHook")
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

This will not only validate the DataAnnotations on my configuration class, it will also run that validation on startup.

We can see what happens if I mangle my configuration and try to start my application. With this configuration below...

```json
"WebHook": {
    "WebhookUrl": "",
    "DisplayName": "DevOps",
    "Enabled": true
  }
```

Running the application fails with this error.

{{< alert >}}
Unhandled exception. Microsoft.Extensions.Options.OptionsValidationException: DataAnnotation validation failed for 'WebHookSettings' members: 'WebhookUrl' with the error: 'The WebhookUrl field is required.'.
{{< /alert >}}

Now its complaining about the field being blank while required. What if we populate the URL field with a bad value that isn't a Url?

```json
  "WebHook": {
    "WebhookUrl": "BADVALUE",
    "DisplayName": "DevOps",
    "Enabled": true
  }
```

We we run the app with this value, we get a different validation error.

{{< alert >}}
Unhandled exception. Microsoft.Extensions.Options.OptionsValidationException: DataAnnotation validation failed for 'WebHookSettings' members: 'WebhookUrl' with the error: 'The WebhookUrl field is not a valid fully-qualified HTTP, HTTPS, or FTP URL.'.
{{< /alert >}}

We can take this a step further, with additional custom validation if we choose. Let's reset our configuration to something reasonable, but insecure..

```json
 "WebHook": {
    "WebhookUrl": "http://example.com/event",
    "DisplayName": "DevOps",
    "Enabled": true
  }
```

How do we validate we're always using https? Let's add custom validation to our application.

```cs

builder.Services.AddOptions<WebHookSettings>()
    .BindConfiguration("WebHook")
    .ValidateDataAnnotations()
    .Validate(webHookSettings =>
        {
            return webHookSettings.WebhookUrl.StartsWith("https://");
        }, "WebHookUrl must start with https://")
    .ValidateOnStart();
```

Now we can validate the normal DataAnnotations as well as any custom validation logic we would like to include on startup!

{{< alert >}}
Unhandled exception. Microsoft.Extensions.Options.OptionsValidationException: WebHookUrl must start with https://
{{< /alert >}}

If we fix everything with our validation, like so...

```json
  "WebHook": {
    "WebhookUrl": "https://example.com/event",
    "DisplayName": "DevOps",
    "Enabled": true
  }
```

The application starts successfully!

```bash
$ dotnet run
Building...
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: https://localhost:7090
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: http://localhost:5268
info: Microsoft.Hosting.Lifetime[0]
      Application started. Press Ctrl+C to shut down.
info: Microsoft.Hosting.Lifetime[0]
      Hosting environment: Development
```

As you build your applications, think about adding validation to ensure your applications have a valid configuration at startup. Having runtime errors due to configuration is an annoying and sometimes hard problem to troubleshoot.

Please dive into the amazing documentation on the [.NET Configuration system](https://learn.microsoft.com/en-us/dotnet/core/extensions/configuration) and look into the [Options Pattern documentation](https://learn.microsoft.com/en-us/dotnet/core/extensions/options) as well!

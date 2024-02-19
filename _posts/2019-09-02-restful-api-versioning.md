---
#layout: post
title: RESTful API Versioning
date: 2019-09-02 22:26:57.000000000 +00:00
type: post
categories:
- Development
tags:
- api
- rest
- restful
permalink: "/2019/09/02/restful-api-versioning/"
header:
  teaser: /assets/images/rest-logo.png
  og_image: /assets/images/rest-logo.png
---
I've been a developer for a long time, writing APIs and clients to consume them. When an API is around long enough, it needs to change. I've versioned APIs in the past using a number of different techniques. Some successful, some painful. Now I realize this discussion is like the VI/Emacs conflict, the Tab/Space wars, and the Spanish Inquisition, but it is a good topic to look at. There are a few main styles when it comes to API versioning:

- URL
- Query Parameter
- Accept header
- Custom request header

## URL

This is where a lot of people start, you might have seen it out there. You can easily see the version of the API you are calling. And a lot of times behind the scenes, the base API points to the latest version. The issue a number of people have with this, myself included, is that a URL in RESTful APIs should represent an entity, not a version of an entity. For example, /api/v1/users/27 and /api/v2/users/27 are not two different users. As you add new versions, you break permalinks to resources. And you're tying the URL of a resource, not to a version of it.

    /api/users  -> /api/v2/users
    /api/v1/users
    /api/v2/users

## Query Parameter

Another way people can version APIs is by Query Parameter. This keeps the URL consistent, but adds an extra parameter. This is fine by my book, you're adding extra info to the _request_, not the **resource**. It can change per request, and doesn't change the permalink or URL of the resource.

    /api/users -> /api/users?api-version=1.0
    /api/users?api-version=1.0
    /api/users?api-version=2.0

## Accept Header

The third way I've seen API versioning is an accept header on the http(s) request. Accept headers describe how you'ld like to receive the data. Being part of the http headers, this can be taken into effect during caching, and if not specified explicitly can return the latest version. I like this method quite a bit, the client is telling the server how it wants to receive the data, the format _and_ the version.

    GET api/users HTTP/1.1
    host: localhost
    accept: application/json;v=2.0

## Custom Header

The last way I've seen is to define a custom http header. Just adding the requested version as a header to the request. This isn't as easily compatible with clients as the other methods.

    api-version: 1.0

## Implementation

In the past, I've had to roll my own. I started with URL versioning. As I worked with RESTful APIs, I realized there was a better way and started moving towards either the Query parameter or an Accept Header. There are some pretty good libraries that will handle a lot of this for you today.

Microsoft has a library that works with .Net Framework 4.5 and .Net Core. It's called ASPNet API Versioning, [https://github.com/microsoft/aspnet-api-versioning](https://github.com/microsoft/aspnet-api-versioning) . They also released libraries to work with [Swagger](https://docs.microsoft.com/en-us/aspnet/core/tutorials/web-api-help-pages-using-swagger?view=aspnetcore-2.2) for API documentation. Honestly, its pretty nice and supports a number of methods for versioning that you can customize pretty well. This follows the [Microsoft REST API Guidelines](https://github.com/Microsoft/api-guidelines/blob/master/Guidelines.md#12-versioning).

There are some more references to check out at [http://apistylebook.com/design/topics/versioning](http://apistylebook.com/design/topics/versioning)

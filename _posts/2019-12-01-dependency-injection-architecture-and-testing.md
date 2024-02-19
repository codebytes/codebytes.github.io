---
#layout: post
title: Dependency Injection, Architecture, and Testing
date: 2019-12-01 23:27:53.000000000 +00:00
type: post
categories:
- Development
tags:
- c#
- dependency injection
- di
- ioc
- solid
- testing
permalink: "/2019/12/01/dependency-injection-architecture-and-testing/"
header:
  teaser: /assets/images/dotnet-logo.png
  og_image: /assets/images/dotnet-logo.png
---

**This blog was posted as part of the [Third Annual C# Advent](https://crosscuttingconcerns.com/The-Third-Annual-csharp-Advent). Make sure to check out everyone else's work when you're done here**

Dependency Injection, or DI, is a Software Architecture Design Pattern. DI is something that comes up during discussions on SOLID, IoC (Inversion of Control), testing, and refactoring. I want to speak on each of these briefly because DI touches all of these. But before I really dive into things, I want to define what a dependency is. A _dependency_ is any object that another object requires. So all of those classes, services, and libraries that we use to build our applications are dependencies.

## Dependency Injection - What is it?

At its heart, Dependency Injection is right there in the name, you inject your dependencies. I want all the dependencies for my class called out in the constructor, parameter list, or somewhere I can easily see them. Without Dependency Injection, any time I need a class, service, database connection, I just new it up. This can make code untestable, hard to use safely, and very brittle. Lets see what this looks like in a small example. Imagine the hidden dependencies and hard to test logic in a bigger class.

```cs
    public class ClientService
    {
        private ClientRepository _clientRepository;
        
        public ClientService()
        {
            //allocated in constructor but can't test or use a different repository without a code change
            _clientRepository = new ClientRepository();
        }
    
        public void Delete(int id)
        {
            //hidden dependency to the delete method, newed up here
            var audit = new AuditService();
            audit.LogDelete(id);
            
            _clientRepository.Delete(id);
    
            //a hidden static dependency, very hard to test with
            EmailProvider.SendDeleteConfirmation(id);
        }
    }
```

### Untestable

I said not using DI would make the code untestable. Why? There are a lot of reasons in this example. I'll go through them one at a time.

#### Isolation / Coupling

When you are writing unit tests, you want to isolate a class for testing. Some people call it the "System Under Test" (SUT) or "Class Under Test" (CUT). How can we isolate just the logic in ClientService from the logic in its dependencies? Our service is tightly coupled to the repository, the audit service and the email provider. I can't easily put in a fake/mocked email provider or audit service to test what my class is doing. This type of code pushes a lot of developers to skip unit tests and just rely on integration tests.

#### Database

Another issue is I/O, like files, databases, network connections. In this example, I'm using the Repository pattern to wrap/abstract my database. This could be a file, mysql, or Azure CosmosDB, I don't care. But, in this case, it's getting created in the constructor of my service. When I want to unit test my business logic, it will be touching the database. More of an integration test than a unit test. Unit tests should be _fast_. **Ludicrous** speed _fast_. Sure I could create a local or testing database, but again, that is integration, not unit testing.

#### Statics

Statics are always a problem because statics can't be mocked or faked. Another issue is that its hard to tell side effects of those classes and methods. When I'm reviewing a class or method, I usually check the constructor, parameters, or variables at the top to see what a piece of code depends on. Static methods can be buried inside a block of code and be missed. It means that it can be a hidden dependency.

## Interfaces

I feel it is very important to have interfaces define the contracts between layers and systems. Having _FOO_ depend on _BAR_ means that _FOO_ might change every time we modify the implementation of _BAR_. If _FOO_ depends on _IBAR_, the API contract of _BAR_, we can have multiple implementations, change the implementation or mock it. The interface insulates _FOO_ from the changes in _BAR_. In addition to reducing coupling between modules, it will help with testability and refactoring down the road.

## Types of Dependency Injection

Let's look at a few types of dependency injection. The type I usually prefer, and my default, is Constructor Injection. This lists all the dependencies for a class in its constructor. There are times where this isn't a good idea, when you have the expensive creation of dependencies that are only used in infrequent edge cases in the class. In those instances, Parameter Injection works well, injecting the dependency as a parameter into the methods that need it. Finally there is property injection which I dislike. I've seen people use it because of tutorials online, but I _**HIGHLY**_ recommend avoiding this if possible.

### Constructor Injection

This involves moving dependencies to the constructor where possible. This is a lot of times the place where people end up, but if you're refactoring older code, you won't get here right away. Notice I moved from having private variables of the concrete classes to the interfaces. Also notice, looking at the class constructor, you know exactly what this class depends on.

```cs
    public class ClientService : IClientService
    {
        private readonly IClientRepository _clientRepository;
        private readonly IAuditService _auditService;
        private readonly IEmailProvider _emailProvider;
    
        public ClientService(IClientRepository clientRepository, IAuditService auditService, IEmailProvider emailProvider)
        {
            _clientRepository = clientRepository;
            _auditService = auditService;
            _emailProvider = emailProvider;
        }
    
        public void Delete(int id)
        {
            _auditService.LogDelete(id);
            _clientRepository.Delete(id);
            _emailProvider.SendDeleteConfirmation(id);
        }
    }
```

### Parameter Injection

This involves moving dependencies to where they are used. Looking at the interface to the service or the methods, you can see what dependencies are needed for some of the methods. Like I mentioned before, if there are some dependencies that are really expensive to create or maybe incur some type of cost, you can limit their creation to only when they are used.

```cs
    public class ClientService : IClientService
    {
        private readonly IClientRepository _clientRepository;
    
        public ClientService(IClientRepository clientRepository)
        {
            _clientRepository = clientRepository;
        }
    
        public void Delete(int id, IAuditService auditService, IEmailProvider emailProvider)
        {
            auditService.LogDelete(id);
            _clientRepository.Delete(id);
            emailProvider.SendDeleteConfirmation(id);
        }
    }
```

### Property Injection

Use property injection only for optional dependencies. That means your service should be able to properly work without these dependencies provided. After you instantiate the class, you need to assign the properties with objects. This can cause confusion because you can't always tell what a classes true dependencies are just looking at the constructor. It can also cause confusion during testing.

```cs
    public class ClientService : IClientService
    {
        public IEmailProvider EmailProvider { get; set; }
    
        private readonly IClientRepository _clientRepository;
        private readonly IAuditService _auditService;
    
        public ClientService(IClientRepository clientRepository, IAuditService auditService)
        {
            _clientRepository = clientRepository;
            _auditService = auditService;
        }
    
        public void Delete(int id)
        {
            _auditService.LogDelete(id);
            _clientRepository.Delete(id);
            EmailProvider?.SendDeleteConfirmation(id);
        }
    }
```

## DI Containers

Having all our dependencies in the constructor is nice, but _who_ is going to new up our services? With most DI frameworks, you register your interfaces and services at program startup with a DI container, and everything is wired up for you. You can control the wiring process. Should service A be a singleton? Should service B be instantiated on every call? Dotnet core has built-in support for DI containers. And before dotnet core, the .Net Framework had a lot of different libraries and frameworks to help with dependency injection. You might have heard of Ninject, Autofac, Castle, or Unity. Dotnet core has some [good documentation](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-3.0) around their implementation, but if you want to you something else you can.

```cs
    services.AddScoped<IMyDependency, MyDependency>();
    services.AddTransient<IOperationTransient, Operation>();
    services.AddScoped<IOperationScoped, Operation>();
    services.AddSingleton<IOperationSingleton, Operation>();
```

## Testing

I just briefly wanted to discuss testing. Using some of the techniques I've discussed, testing services and classes is much easier. By having interfaces for all my major services, constructor injection in place, and a mocking framework, I can isolate classes for testing.

```cs
        private BookService _bookService;
        private Mock<IBookRepository> _mockBookRepository;
        private Mock<IBookEntityDomainAdapter> _mockBookEntityDomainAdapter;
    
        [TestInitialize]
        public void TestInitialize()
        {
            _mockBookRepository = new Mock<IBookRepository>();
            _mockBookEntityDomainAdapter = new Mock<IBookEntityDomainAdapter>();
    
            _bookService = new BookService(_mockBookRepository.Object, _mockBookEntityDomainAdapter.Object);
        }
    
        [TestMethod]
        public void GetAll_ItemsInRepository_ReturnsSameNumberOfItems()
        {
            //arrange
            var sampleData = Enumerable
                .Repeat(new BookEntity(), 5)
                .ToList();
            _mockBookRepository.Setup(x => x.GetAll())
                .Returns(sampleData);
    
            //act
            var result = _bookService.GetAll();
    
            //assert
            Assert.AreEqual(sampleData.Count(), result.Count());
        }
```

## Where to Go from here - Refactoring

Taking legacy code, code without tests (essentially the same thing), or code written without dependency injection and refactoring it into testable, decoupled code is not as easy as installing a nuget package. If you are just getting started and you have a ton of new ServiceX() and ServiceY.action() sprinkled throughout your code, code review the docs at: [https://docs.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-3.0](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-3.0). Have interfaces for your classes. When you have dependencies, instantiate them in your constructor if you can't setup DI, it will help with readability and maintainability.

## Conclusion

Dependency Injection is a pattern that everyone should be using. It makes the code more readable, maintainable, and testable. I know a lot of people think that this is something we've solved and everyone uses, but we're not. Too many people aren't setting up DI, they aren't using interfaces, they aren't registering dependencies. We need to keep discussing this because people are constantly starting out, learning, and growing in this field.

There is some sample code at: [https://github.com/Codebytes/DependencyInjectionDemo](https://github.com/Codebytes/DependencyInjectionDemo)

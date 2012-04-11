Defining Content
================

"Resource" is the term that Substance D uses to describe an object placed in
the *resource tree*.  The SDI management interface is a set of views imposed
upon the resource tree that allow you to add, delete, and otherwise manage
resources.

Ideally, all resources in your resource tree will be "content". "Content" is
the term that Substance D uses to describe resource objects that are
particularly well-behaved when they appear in the SDI management interface.

You can convince the management interface that your particular resources are
content.  To define a resource as content, you need to associate a resource
with a *content type*.

Registering Content
-------------------

In order to add new content to the system, you need to associate a resource
constructor with a content *type*.  A resource constructor that generates
content must have these properties:

- It must be a class, or a factory function that returns an instance of a
  resource class.

- Instances of the resource class must be *persistent* (it must derive from
  the ``persistent.Persistent`` class or a class that derives from Persistent
  such as :class:`substanced.folder.Folder`).

- The resource class or factory must be decorated with the ``@content``
  decorator, or must be added at configuration time via
  ``config.add_content_type``.

- It must have a *type*.  A type acts as a globally unique categorization
  marker, and allows the content to be constructed, enumerated, and
  introspected by various Substance D UI elements such as "add forms", and
  queries by the management interface for the icon name of a resource.  The
  type is defined as a class that inherits from the
  :class:`substanced.content.Type` class.

.. note::

   If a resource constructor is not a class, you might need to do add an
   interface declaration on the actual class or the instance that is
   returned. XXX, bleh, TMI?

Here's an example which defines a content resource constructor as a class:

.. code-block:: python

   # in a module named blog.resources

   from persistent import Persistent
   from substanced.content import (
       Type,
       content,
       )     

   class BlogEntryType(Type):
       pass

   @content(BlogEntryType)
   class BlogEntry(Persistent):
       def __init__(self, title, body):
           self.title = title
           self.body = body

Here's an example of defining a content resource factory using a function
instead:

.. code-block:: python

   # in a module named blog.resources

   from persistent import Persistent
   from substanced.content import (
       Type,
       content,
       )     

   class BlogEntryType(Type):
       pass

   class BlogEntry(Persistent):
       def __init__(self, title, body):
           self.title = title
           self.body = body

   @content(BlogEntryType)
   def make_blog_entry(title, body):
       return BlogEntry(title, body)

In order to activate a ``@content`` decorator, it must be *scanned* using the
Pyramid ``config.scan()`` machinery:

.. code-block:: python

   # in a module named blog.__init__

   from pyramid.config import Configurator

   def main(global_config, **settings):
       config = Configurator()
       config.include('substanced')
       config.scan('blog.resources')
       # .. and so on ...

Instead of using the ``@content`` decorator, you can alternately add a
content resource imperatively at configuration time using the
``add_content_type`` method of the Configurator:

.. code-block:: python

   # in a module named blog.__init__

   from pyramid.config import Configurator
   from .resources import BlogEntryType, BlogEntry

   def main(global_config, **settings):
       config = Configurator()
       config.include('substanced')
       config.add_content_type(BlogEntryType, BlogEntry)

This does the same thing as using the ``@content`` decorator, but you don't
need to ``scan()`` your resources if you use ``add_content_type`` instead of
the ``@content`` decorator.

Once a content type has been defined (and scanned, if it's been defined using
a decorator), an instance of the resource can be constructed from within a
view that lives in your application:

.. code-block:: python

   # in a module named blog.views

   from pyramid.httpexceptions import HTTPFound
   from .resources import BlogEntryType

   @view_config(name='add_blog_entry', request_method='POST')
   def add_blogentry(request):
       title = request.POST['title']
       body = request.POST['body']
       entry = request.registry.content.create(BlogEntryType, title, body)
       context['title] = entry
       return HTTPFound(request.resource_url(entry))

The arguments passed to ``request.registry.content.create`` must start with
the content type, and must be followed with whatever arguments are required
by the resource constructor.

Creating an instance of content this way isn't particularly more useful than
creating an instance of the resource object directly by calling its class
``__init__`` unless you're building a highly abstract system.  But even if
you're not building a very abstract system, types can be very useful.  For
instance, types can be enumerated:

.. code-block:: python

   # in a module named blog.views

   @view_config(name='show_types', renderer='show_types.pt')
   def show_types(request):
       all_types = request.registry.content.all()
       return {'all_types':all_types}

``request.registry.content.all()`` will return all type objects you've
defined and scanned.

.. Introspecting Content
.. ---------------------

.. You can check if a resource is of a particular type by using
.. ``request.registry.content.is_type``:

.. .. code-block:: python

..    # in a module named blog.views

..    from .resources import BlogEntryType

..    @view_config(name='is_blog_entry', renderer='string')
..    def check(request):
..        if request.registry.content.is_type(request.context, BlogEntryType):
..            return "It's a blog entry type"
..        return "It's not a blog entry type"

.. A resource object might be associated with more than one type.  You can get a
.. sequence of content types that are provided by a resource by calling
.. ``request.registry.content.provides``:

.. .. code-block:: python

..    # in a module named blog.views

..    from .resources import BlogEntryType

..    @view_config(name='is_blog_entry', renderer='string')
..    def check(request):
..        types = request.registry.content.provides(request.context)
..        if BlogEntryType in types:
..            return "It's a blog entry type"
..        return "It's not a blog entry type"

Icons
-----

You can associate a content type registration with a management view icon by
passing an ``icon`` keyword argument to ``@content`` or ``add_content_type``.

.. code-block:: python

   # in a module named blog.resources

   from persistent import Persistent
   from substanced.content import (
       Type,
       content,
       )     

   class BlogEntryType(Type):
       pass

   class BlogEntry(Persistent):
       def __init__(self, title, body):
           self.title = title
           self.body = body

   @content(BlogEntryType, icon='icon-file')
   def make_blog_entry(title, body):
       return BlogEntry(title, body)

Once you've done this, content you add to a folder in the sytem will display
the icon next to it in the contents view of the management interface and in
the breadcrumb list.  The available icon names are listed at
http://twitter.github.com/bootstrap/base-css.html#icons .

Categories
----------

Using categories is a nice way to let you populate the management UI with
choices.  For example, if you register several types in a given category, you
can easily get a listing of them to put into a dropdown of constructable
items on an "add form".  They won't be listed in highly generic SDI add
menus, but they'll be available for your own use as necessary.

You can categorize types into particular "buckets" by passing a ``category``
argument to the ``@content`` decorator:

.. code-block:: python

   # in a module named blog.resources

   from persistent import Persistent
   from substanced.content import (
       Type,
       content,
       )     

   class BlogTypes(Type):
       pass

   class BlogEntryType(Type):
       pass

   class BlogPictureType(Type):
       pass

   @content(BlogEntryType, category=BlogTypes)
   class BlogEntry(Persistent):
       def __init__(self, title, body):
           self.title = title
           self.body = body

   @content(BlogPictureType, category=BlogTypes)
   class BlogPicture(Persistent):
       def __init__(self, title, data):
           self.title = title
           self.data = data

In the above example, ``BlogPictureType`` is the content type, and
``BlogTypes`` is the categorization type.

Once you've categorized content like this, you can make use of the categories
in the ``create`` and ``all`` APIs:

.. code-block:: python

   # in a module named blog.views

   from pyramid.httpexceptions import HTTPFound
   from .resources import BlogType, BlogEntryType

   @view_config(name='add_blog_entry', request_method='POST')
   def add_blogentry(request):
       title = request.POST['title']
       body = request.POST['body']
       entry = request.registry.content[BlogType].create(
                                 BlogEntryType, title, body)
       context['title] = entry
       return HTTPFound(request.resource_url(entry))

.. code-block:: python

   # in a module named blog.views

   from .resources import BlogType

   @view_config(name='show_blog_types', renderer='show_types.pt')
   def show_types(request):
       blog_types = request.registry.content[BlogTypes].all()
       return {'blog_types':blog_types}

Content types defined with a ``category`` will not show up in "bare" calls to
``all()``:

.. code-block:: python

   # in a module named blog.views

   @view_config(name='show_blog_types', renderer='show_types.pt')
   def show_types(request):
       all_types = request.registry.content.all() # won't return BlogTypes
       return {'all_types':all_types}
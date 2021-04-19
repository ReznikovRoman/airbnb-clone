# hosts package

## Subpackages


* hosts.tests package


    * Submodules


    * hosts.tests.test_views module


    * Module contents


## Submodules

## hosts.admin module


### class hosts.admin.RealtyHostAdmin(model, admin_site)
Bases: `django.contrib.admin.options.ModelAdmin`


#### list_display( = ('__str__', 'host_rating'))

#### property media()
## hosts.apps module


### class hosts.apps.HostsConfig(app_name, app_module)
Bases: `django.apps.config.AppConfig`


#### name( = 'hosts')
## hosts.models module


### class hosts.models.RealtyHost(\*args, \*\*kwargs)
Bases: `django.db.models.base.Model`

Realty host.


#### exception DoesNotExist()
Bases: `django.core.exceptions.ObjectDoesNotExist`


#### exception MultipleObjectsReturned()
Bases: `django.core.exceptions.MultipleObjectsReturned`


#### host_rating()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### id()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### objects( = <django.db.models.manager.Manager object>)

#### realty()
Accessor to the related objects manager on the reverse side of a
many-to-one relation.

In the example:

```
class Child(Model):
    parent = ForeignKey(Parent, related_name='children')
```

`Parent.children` is a `ReverseManyToOneDescriptor` instance.

Most of the implementation is delegated to a dynamically defined manager
class built by `create_forward_many_to_many_manager()` defined below.


#### save(\*args, \*\*kwargs)
Save the current instance. Override this in a subclass if you want to
control the saving process.

The ‘force_insert’ and ‘force_update’ parameters can be used to insist
that the “save” must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.


#### user()
Accessor to the related object on the forward side of a one-to-one relation.

In the example:

```
class Restaurant(Model):
    place = OneToOneField(Place, related_name='restaurant')
```

`Restaurant.place` is a `ForwardOneToOneDescriptor` instance.


#### user_id()
## hosts.services module


### hosts.services.has_user_required_data_to_become_host(user: accounts.CustomUser)
Check if user that wants to become a host has a profile image and a confirmed email address.

## hosts.urls module

## hosts.views module


### class hosts.views.BecomeHostView(\*\*kwargs)
Bases: `django.contrib.auth.mixins.LoginRequiredMixin`, `accounts.mixins.ActivatedAccountRequiredMixin`, `django.views.generic.base.View`

View for handling new hosts.


#### get(request: common.types.AuthenticatedHttpRequest, \*args, \*\*kwargs)

### class hosts.views.HostMissingImageView(\*\*kwargs)
Bases: `django.contrib.auth.mixins.LoginRequiredMixin`, `accounts.mixins.ActivatedAccountRequiredMixin`, `django.views.generic.base.TemplateView`

View for showing a ‘missing profile image’ error page.


#### template_name( = 'hosts/host/missing_image.html')
## Module contents

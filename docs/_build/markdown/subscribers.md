# subscribers package

## Subpackages

## Submodules

## subscribers.admin module


### class subscribers.admin.SubscriberAdmin(model, admin_site)
Bases: `django.contrib.admin.options.ModelAdmin`


#### get_user_link(obj: subscribers.models.Subscriber)

#### list_display( = ('__str__', 'get_user_link'))

#### property media()
## subscribers.apps module


### class subscribers.apps.SubscribersConfig(app_name, app_module)
Bases: `django.apps.config.AppConfig`


#### name( = 'subscribers')
## subscribers.forms module


### class subscribers.forms.SubscriberEmailForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=<class 'django.forms.utils.ErrorList'>, label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None)
Bases: `django.forms.models.ModelForm`

Form for creating new Subscriber with the given email.


#### class Meta()
Bases: `object`


#### fields( = ('email',))

#### model()
alias of `subscribers.models.Subscriber`


#### base_fields( = {'email': <django.forms.fields.EmailField object>})

#### declared_fields( = {})

#### property media()
Return all media required to render the widgets on this form.

## subscribers.models module


### class subscribers.models.Subscriber(\*args, \*\*kwargs)
Bases: `django.db.models.base.Model`

Subscriber that receives email notifications about new realty.


#### exception DoesNotExist()
Bases: `django.core.exceptions.ObjectDoesNotExist`


#### exception MultipleObjectsReturned()
Bases: `django.core.exceptions.MultipleObjectsReturned`


#### email()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### id()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### objects( = <django.db.models.manager.Manager object>)

#### user()
Accessor to the related object on the forward side of a one-to-one relation.

In the example:

```
class Restaurant(Model):
    place = OneToOneField(Place, related_name='restaurant')
```

`Restaurant.place` is a `ForwardOneToOneDescriptor` instance.


#### user_id()
## subscribers.services module


### subscribers.services.get_subscriber_by_email(email: str)

### subscribers.services.get_subscriber_by_user(user: accounts.CustomUser)

### subscribers.services.set_user_for_subscriber(user: accounts.models.CustomUser)
Update user field in the Subscriber object if there is subscriber with <user.email> email.


### subscribers.services.update_email_for_subscriber_by_user(user: accounts.models.CustomUser)
Update subscriber’s email if User has changed an email, but there was subscriber with ‘previous’ email.

E.g. user has subscribed to the newsletter with email <[first@email.com](mailto:first@email.com)>,
then he has changed his email to <[second@email.com](mailto:second@email.com)>, now Subscriber’s email is <[second@gmail.com](mailto:second@gmail.com)>

## subscribers.tasks module

## subscribers.tests module

## subscribers.urls module

## subscribers.views module


### class subscribers.views.SubscribeView(\*\*kwargs)
Bases: `django.views.generic.base.View`

View for handling new subscriptions.


#### post(request: django.http.request.HttpRequest, \*args, \*\*kwargs)
## Module contents

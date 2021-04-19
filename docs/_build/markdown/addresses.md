# addresses package

## Subpackages

## Submodules

## addresses.admin module


### class addresses.admin.AddressAdmin(model, admin_site)
Bases: `django.contrib.admin.options.ModelAdmin`


#### address_link(obj: addresses.models.Address)

#### exclude( = ('city_slug', 'country_slug'))

#### list_display( = ('address_link', 'country', 'city', 'street'))

#### list_filter( = ('country',))

#### property media()
## addresses.apps module


### class addresses.apps.AddressesConfig(app_name, app_module)
Bases: `django.apps.config.AppConfig`


#### name( = 'addresses')
## addresses.forms module


### class addresses.forms.AddressForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=<class 'django.forms.utils.ErrorList'>, label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None)
Bases: `django.forms.models.ModelForm`

Form for editing (creating or updating) an Address object.


#### class Meta()
Bases: `object`


#### fields( = ('country', 'city', 'street'))

#### model()
alias of `addresses.models.Address`


#### base_fields( = {'city': <django.forms.fields.CharField object>, 'country': <django.forms.fields.CharField object>, 'street': <django.forms.fields.CharField object>})

#### declared_fields( = {})

#### property media()
Return all media required to render the widgets on this form.

## addresses.models module


### class addresses.models.Address(\*args, \*\*kwargs)
Bases: `django.db.models.base.Model`

Address.


#### exception DoesNotExist()
Bases: `django.core.exceptions.ObjectDoesNotExist`


#### exception MultipleObjectsReturned()
Bases: `django.core.exceptions.MultipleObjectsReturned`


#### city()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### city_slug()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### country()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### country_slug()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### get_full_address()

#### id()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### objects( = <django.db.models.manager.Manager object>)

#### realty()
Accessor to the related object on the reverse side of a one-to-one
relation.

In the example:

```
class Restaurant(Model):
    place = OneToOneField(Place, related_name='restaurant')
```

`Place.restaurant` is a `ReverseOneToOneDescriptor` instance.


#### save(\*args, \*\*kwargs)
Save the current instance. Override this in a subclass if you want to
control the saving process.

The ‘force_insert’ and ‘force_update’ parameters can be used to insist
that the “save” must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.


#### street()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.

## addresses.tests module

## addresses.views module

## Module contents

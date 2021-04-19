# realty package

## Subpackages


* realty.services package


    * Submodules


    * realty.services.images module


    * realty.services.ordering module


    * realty.services.realty module


    * Module contents


## Submodules

## realty.admin module


### class realty.admin.AmenityAdmin(model, admin_site)
Bases: `django.contrib.admin.options.ModelAdmin`


#### list_display( = ('__str__',))

#### property media()

### class realty.admin.AmenityInline(parent_model, admin_site)
Bases: `django.contrib.admin.options.TabularInline`


#### property media()

#### model()
alias of `realty.models.Realty_amenities`


### class realty.admin.RealtyAdmin(model, admin_site)
Bases: `django.contrib.admin.options.ModelAdmin`


#### inlines( = [<class 'realty.admin.AmenityInline'>])

#### list_display( = ('__str__', 'name', 'realty_type', 'is_available', 'created', 'host'))

#### property media()

#### prepopulated_fields( = {'slug': ('name',)})

#### search_fields( = ('name',))

### class realty.admin.RealtyImageAdmin(model, admin_site)
Bases: `django.contrib.admin.options.ModelAdmin`


#### list_display( = ('__str__', 'realty'))

#### list_filter( = ('realty',))

#### property media()

#### search_fields( = ('realty__name',))
## realty.apps module


### class realty.apps.RealtyConfig(app_name, app_module)
Bases: `django.apps.config.AppConfig`


#### name( = 'realty')
## realty.constants module

## realty.fields module


### class realty.fields.OrderField(related_fields: Optional[List[str]] = None, \*args, \*\*kwargs)
Bases: `django.db.models.fields.PositiveSmallIntegerField`

Order field.


#### related_fields()
fields, with the respect to which the order is calculated


* **Type**

    Optional[List[str]]



### (e.g. for each Realty object we start image ordering from 0 and each next image has a larger order)()

#### pre_save(model_instance, add)
Return field’s value (order) just before saving.

## realty.forms module


### class realty.forms.RealtyDescriptionForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=<class 'django.forms.utils.ErrorList'>, label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None, renderer=None)
Bases: `django.forms.forms.Form`

Form for editing Realty’s description.

Step-3


#### base_fields( = {'description': <django.forms.fields.CharField object>})

#### declared_fields( = {'description': <django.forms.fields.CharField object>})

#### property media()
Return all media required to render the widgets on this form.


### class realty.forms.RealtyForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=<class 'django.forms.utils.ErrorList'>, label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None)
Bases: `django.forms.models.ModelForm`

Form for editing (creating or updating) a Realty object.


#### class Meta()
Bases: `object`


#### fields( = ('name', 'realty_type', 'beds_count', 'max_guests_count', 'price_per_night', 'amenities', 'description'))

#### model()
alias of `realty.models.Realty`


#### widgets( = {'amenities': <django.forms.widgets.CheckboxSelectMultiple object>, 'beds_count': <django.forms.widgets.TextInput object>, 'max_guests_count': <django.forms.widgets.TextInput object>, 'price_per_night': <django.forms.widgets.TextInput object>})

#### base_fields( = {'amenities': <django.forms.models.ModelMultipleChoiceField object>, 'beds_count': <django.forms.fields.IntegerField object>, 'description': <django.forms.fields.CharField object>, 'max_guests_count': <django.forms.fields.IntegerField object>, 'name': <django.forms.fields.CharField object>, 'price_per_night': <django.forms.fields.IntegerField object>, 'realty_type': <django.forms.fields.TypedChoiceField object>})

#### declared_fields( = {})

#### property media()
Return all media required to render the widgets on this form.


### class realty.forms.RealtyGeneralInfoForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=<class 'django.forms.utils.ErrorList'>, label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None)
Bases: `django.forms.models.ModelForm`

Form for editing Realty’s general info.

Step-1


#### class Meta()
Bases: `object`


#### fields( = ('name', 'realty_type', 'beds_count', 'max_guests_count', 'price_per_night', 'amenities'))

#### model()
alias of `realty.models.Realty`


#### widgets( = {'amenities': <django.forms.widgets.CheckboxSelectMultiple object>, 'beds_count': <django.forms.widgets.TextInput object>, 'max_guests_count': <django.forms.widgets.TextInput object>, 'price_per_night': <django.forms.widgets.TextInput object>})

#### base_fields( = {'amenities': <django.forms.models.ModelMultipleChoiceField object>, 'beds_count': <django.forms.fields.IntegerField object>, 'max_guests_count': <django.forms.fields.IntegerField object>, 'name': <django.forms.fields.CharField object>, 'price_per_night': <django.forms.fields.IntegerField object>, 'realty_type': <django.forms.fields.TypedChoiceField object>})

#### declared_fields( = {})

#### property media()
Return all media required to render the widgets on this form.


### class realty.forms.RealtyImageForm(\*args, \*\*kwargs)
Bases: `django.forms.models.ModelForm`

Form for creating RealtyImages.


#### class Meta()
Bases: `object`


#### fields( = ('image',))

#### model()
alias of `realty.models.RealtyImage`


#### widgets( = {'image': <django.forms.widgets.FileInput object>})

#### base_fields( = {'image': <django.forms.fields.ImageField object>})

#### declared_fields( = {})

#### property media()
Return all media required to render the widgets on this form.


### class realty.forms.RealtyTypeForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=<class 'django.forms.utils.ErrorList'>, label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None, renderer=None)
Bases: `django.forms.forms.Form`

Form for selecting realty types.


#### base_fields( = {'realty_type': <django.forms.fields.MultipleChoiceField object>})

#### declared_fields( = {'realty_type': <django.forms.fields.MultipleChoiceField object>})

#### property media()
Return all media required to render the widgets on this form.

## realty.mixins module


### class realty.mixins.RealtySessionDataRequiredMixin()
Bases: `common.mixins.SessionDataRequiredMixin`

Verify that user has entered all the required data to create new Realty.


#### redirect_url(: str)
## realty.models module


### class realty.models.Amenity(\*args, \*\*kwargs)
Bases: `django.db.models.base.Model`

Realty amenity.


#### exception DoesNotExist()
Bases: `django.core.exceptions.ObjectDoesNotExist`


#### exception MultipleObjectsReturned()
Bases: `django.core.exceptions.MultipleObjectsReturned`


#### id()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### name()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### objects( = <django.db.models.manager.Manager object>)

#### realty()
Accessor to the related objects manager on the forward and reverse sides of
a many-to-many relation.

In the example:

```
class Pizza(Model):
    toppings = ManyToManyField(Topping, related_name='pizzas')
```

`Pizza.toppings` and `Topping.pizzas` are `ManyToManyDescriptor`
instances.

Most of the implementation is delegated to a dynamically defined manager
class built by `create_forward_many_to_many_manager()` defined below.


### class realty.models.AvailableRealtyManager(\*args, \*\*kwargs)
Bases: `django.db.models.manager.Manager`

Manager for all realty that is available.


#### get_queryset()
Return a new QuerySet object. Subclasses can override this method to
customize the behavior of the Manager.


### class realty.models.CustomDeleteQueryset(model=None, query=None, using=None, hints=None)
Bases: `django.db.models.query.QuerySet`


#### delete()
Delete the records in the current QuerySet.


### class realty.models.Realty(\*args, \*\*kwargs)
Bases: `django.db.models.base.Model`

Realty in an online marketplace (airbnb).


#### exception DoesNotExist()
Bases: `django.core.exceptions.ObjectDoesNotExist`


#### exception MultipleObjectsReturned()
Bases: `django.core.exceptions.MultipleObjectsReturned`


#### amenities()
Accessor to the related objects manager on the forward and reverse sides of
a many-to-many relation.

In the example:

```
class Pizza(Model):
    toppings = ManyToManyField(Topping, related_name='pizzas')
```

`Pizza.toppings` and `Topping.pizzas` are `ManyToManyDescriptor`
instances.

Most of the implementation is delegated to a dynamically defined manager
class built by `create_forward_many_to_many_manager()` defined below.


#### available( = <realty.models.AvailableRealtyManager object>)

#### beds_count()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### created()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### delete(using=None, keep_parents=False)

#### description()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### get_next_by_created(\*, field=<django.db.models.fields.DateTimeField: created>, is_next=True, \*\*kwargs)

#### get_next_by_updated(\*, field=<django.db.models.fields.DateTimeField: updated>, is_next=True, \*\*kwargs)

#### get_previous_by_created(\*, field=<django.db.models.fields.DateTimeField: created>, is_next=False, \*\*kwargs)

#### get_previous_by_updated(\*, field=<django.db.models.fields.DateTimeField: updated>, is_next=False, \*\*kwargs)

#### get_realty_type_display(\*, field=<django.db.models.fields.CharField: realty_type>)

#### host()
Accessor to the related object on the forward side of a many-to-one or
one-to-one (via ForwardOneToOneDescriptor subclass) relation.

In the example:

```
class Child(Model):
    parent = ForeignKey(Parent, related_name='children')
```

`Child.parent` is a `ForwardManyToOneDescriptor` instance.


#### host_id()

#### id()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### images()
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


#### is_available()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### location()
Accessor to the related object on the forward side of a one-to-one relation.

In the example:

```
class Restaurant(Model):
    place = OneToOneField(Place, related_name='restaurant')
```

`Restaurant.place` is a `ForwardOneToOneDescriptor` instance.


#### location_id()

#### max_guests_count()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### name()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### objects( = <realty.models.RealtyManager object>)

#### price_per_night()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### realty_type()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### save(\*args, \*\*kwargs)
Save the current instance. Override this in a subclass if you want to
control the saving process.

The ‘force_insert’ and ‘force_update’ parameters can be used to insist
that the “save” must be an SQL insert or update (or equivalent for
non-SQL backends), respectively. Normally, they should not be set.


#### slug()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### updated()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


### class realty.models.RealtyImage(\*args, \*\*kwargs)
Bases: `django.db.models.base.Model`

Image of a realty.


#### exception DoesNotExist()
Bases: `django.core.exceptions.ObjectDoesNotExist`


#### exception MultipleObjectsReturned()
Bases: `django.core.exceptions.MultipleObjectsReturned`


#### delete(using=None, keep_parents=False)

#### id()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### image()
Just like the FileDescriptor, but for ImageFields. The only difference is
assigning the width/height to the width_field/height_field, if appropriate.


#### objects( = <django.db.models.manager.ManagerFromCustomDeleteQueryset object>)

#### order()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### realty()
Accessor to the related object on the forward side of a many-to-one or
one-to-one (via ForwardOneToOneDescriptor subclass) relation.

In the example:

```
class Child(Model):
    parent = ForeignKey(Parent, related_name='children')
```

`Child.parent` is a `ForwardManyToOneDescriptor` instance.


#### realty_id()

### class realty.models.RealtyManager(\*args, \*\*kwargs)
Bases: `django.db.models.manager.Manager`


#### get_queryset()
Return a new QuerySet object. Subclasses can override this method to
customize the behavior of the Manager.


### class realty.models.RealtyTypeChoices(value)
Bases: `django.db.models.enums.TextChoices`

An enumeration.


#### APARTMENTS( = 'Apartments')

#### HOTEL( = 'Hotel')

#### HOUSE( = 'House')

### realty.models.get_realty_image_upload_path(instance: realty.models.RealtyImage, filename: str)
## realty.tests module

## realty.urls module

## realty.views module

## Module contents

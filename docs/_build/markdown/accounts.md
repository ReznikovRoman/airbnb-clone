# accounts package

## Subpackages

## Submodules

## accounts.admin module


### class accounts.admin.CustomUserAdmin(model, admin_site)
Bases: `django.contrib.auth.admin.UserAdmin`


#### add_fieldsets( = ((None, {'classes': ('wide',), 'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')}),))

#### add_form()
alias of `accounts.forms.SignUpForm`


#### fieldsets( = ((None, {'fields': ('email',)}), ('Personal info', {'fields': ('first_name', 'last_name')}), ('Permissions', {'fields': ('is_active', 'is_email_confirmed', 'is_staff', 'is_admin', 'groups', 'user_permissions')}), ('Important dates', {'fields': ('last_login', 'date_joined')})))

#### form()
alias of `accounts.forms.AdminCustomUserChangeForm`


#### get_profile_link(obj: accounts.models.CustomUser)

#### list_display( = ('email', 'first_name', 'last_name', 'get_profile_link', 'is_email_confirmed'))

#### list_filter( = ('is_active', 'is_staff', 'is_admin'))

#### property media()

#### ordering( = ('email',))

#### readonly_fields( = ('id', 'date_joined', 'last_login'))

#### search_fields( = ('email', 'first_name', 'last_name'))

### class accounts.admin.ProfileAdmin(model, admin_site)
Bases: `django.contrib.admin.options.ModelAdmin`


#### list_display( = ('__str__', 'date_of_birth', 'gender', 'phone_number'))

#### property media()

#### search_fields( = ('user__email',))

### class accounts.admin.SMSLogAdmin(model, admin_site)
Bases: `django.contrib.admin.options.ModelAdmin`


#### get_profile_link(obj: accounts.models.CustomUser)

#### list_display( = ('__str__', 'get_profile_link'))

#### property media()
## accounts.apps module


### class accounts.apps.AccountsConfig(app_name, app_module)
Bases: `django.apps.config.AppConfig`


#### name( = 'accounts')

#### ready()
Override this method in subclasses to run code when Django starts.

## accounts.forms module


### class accounts.forms.AdminCustomUserChangeForm(\*args, \*\*kwargs)
Bases: `django.contrib.auth.forms.UserChangeForm`

Form for editing CustomUser (used on the admin panel).


#### class Meta()
Bases: `object`


#### fields( = ('email', 'first_name', 'last_name', 'is_email_confirmed'))

#### model()
alias of `accounts.models.CustomUser`


#### base_fields( = {'email': <django.forms.fields.EmailField object>, 'first_name': <django.forms.fields.CharField object>, 'is_email_confirmed': <django.forms.fields.BooleanField object>, 'last_name': <django.forms.fields.CharField object>, 'password': <django.contrib.auth.forms.ReadOnlyPasswordHashField object>})

#### declared_fields( = {'password': <django.contrib.auth.forms.ReadOnlyPasswordHashField object>})

#### property media()
Return all media required to render the widgets on this form.


### class accounts.forms.CustomPasswordResetForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=<class 'django.forms.utils.ErrorList'>, label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None, renderer=None)
Bases: `django.contrib.auth.forms.PasswordResetForm`

Custom password reset form.

Sends emails using Celery.


#### base_fields( = {'email': <django.forms.fields.EmailField object>})

#### declared_fields( = {'email': <django.forms.fields.EmailField object>})

#### property media()
Return all media required to render the widgets on this form.


#### send_mail(subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None)
Send a django.core.mail.EmailMultiAlternatives to to_email.


### class accounts.forms.ProfileDescriptionForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=<class 'django.forms.utils.ErrorList'>, label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None)
Bases: `django.forms.models.ModelForm`

Form for editing user description (‘about me’ section).


#### class Meta()
Bases: `object`


#### fields( = ('description',))

#### model()
alias of `accounts.models.Profile`


#### base_fields( = {'description': <django.forms.fields.CharField object>})

#### declared_fields( = {})

#### property media()
Return all media required to render the widgets on this form.


### class accounts.forms.ProfileForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=<class 'django.forms.utils.ErrorList'>, label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None)
Bases: `django.forms.models.ModelForm`

Form for editing user profile.


#### class Meta()
Bases: `object`


#### fields( = ('gender', 'date_of_birth', 'phone_number'))

#### model()
alias of `accounts.models.Profile`


#### widgets( = {'date_of_birth': <django.forms.widgets.DateInput object>})

#### base_fields( = {'date_of_birth': <django.forms.fields.DateField object>, 'gender': <django.forms.fields.TypedChoiceField object>, 'phone_number': <phonenumber_field.formfields.PhoneNumberField object>})

#### clean_date_of_birth()
Handles input of date_of_birth field.

date of birth can’t be in the future, Host must be at least 18 years old


#### declared_fields( = {})

#### property media()
Return all media required to render the widgets on this form.


### class accounts.forms.ProfileImageForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=<class 'django.forms.utils.ErrorList'>, label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None)
Bases: `django.forms.models.ModelForm`

Form for uploading profile image.


#### class Meta()
Bases: `object`


#### fields( = ('profile_image',))

#### model()
alias of `accounts.models.Profile`


#### widgets( = {'profile_image': <django.forms.widgets.FileInput object>})

#### base_fields( = {'profile_image': <django.forms.fields.ImageField object>})

#### declared_fields( = {})

#### property media()
Return all media required to render the widgets on this form.


### class accounts.forms.SignUpForm(\*args, \*\*kwargs)
Bases: `django.contrib.auth.forms.UserCreationForm`

Form for signing up/creating new account.


#### class Meta()
Bases: `object`


#### fields( = ('email', 'first_name', 'last_name', 'password1', 'password2'))

#### model()
alias of `accounts.models.CustomUser`


#### base_fields( = {'email': <django.forms.fields.EmailField object>, 'first_name': <django.forms.fields.CharField object>, 'last_name': <django.forms.fields.CharField object>, 'password1': <django.forms.fields.CharField object>, 'password2': <django.forms.fields.CharField object>})

#### declared_fields( = {'password1': <django.forms.fields.CharField object>, 'password2': <django.forms.fields.CharField object>})

#### property media()
Return all media required to render the widgets on this form.


### class accounts.forms.UserInfoForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=<class 'django.forms.utils.ErrorList'>, label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None)
Bases: `django.forms.models.ModelForm`

Form for editing user info.


#### class Meta()
Bases: `object`


#### fields( = ('first_name', 'last_name', 'email'))

#### model()
alias of `accounts.models.CustomUser`


#### base_fields( = {'email': <django.forms.fields.EmailField object>, 'first_name': <django.forms.fields.CharField object>, 'last_name': <django.forms.fields.CharField object>})

#### declared_fields( = {})

#### property media()
Return all media required to render the widgets on this form.


### class accounts.forms.VerificationCodeForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=<class 'django.forms.utils.ErrorList'>, label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None, renderer=None)
Bases: `django.forms.forms.Form`

Form for entering a SMS verification code.


#### base_fields( = {'digit_1': <django.forms.fields.CharField object>, 'digit_2': <django.forms.fields.CharField object>, 'digit_3': <django.forms.fields.CharField object>, 'digit_4': <django.forms.fields.CharField object>})

#### clean_digit_1()

#### clean_digit_2()

#### clean_digit_3()

#### clean_digit_4()

#### declared_fields( = {'digit_1': <django.forms.fields.CharField object>, 'digit_2': <django.forms.fields.CharField object>, 'digit_3': <django.forms.fields.CharField object>, 'digit_4': <django.forms.fields.CharField object>})

#### property media()
Return all media required to render the widgets on this form.

## accounts.mixins module


### class accounts.mixins.ActivatedAccountRequiredMixin()
Bases: `object`

Verify that current user has confirmed an email.


#### dispatch(request: django.http.request.HttpRequest, \*args, \*\*kwargs)

### class accounts.mixins.AnonymousUserRequiredMixin()
Bases: `object`

Verify that current user is not logged in.


#### dispatch(request: django.http.request.HttpRequest, \*args, \*\*kwargs)

### class accounts.mixins.UnconfirmedEmailRequiredMixin()
Bases: `object`

Verify that current user has not confirmed an email address yet.


#### dispatch(request: django.http.request.HttpRequest, \*args, \*\*kwargs)

### class accounts.mixins.UnconfirmedPhoneNumberRequiredMixin()
Bases: `object`

Verify that current user has not confirmed his phone number yet.


#### dispatch(request: django.http.request.HttpRequest, \*args, \*\*kwargs)
## accounts.models module


### class accounts.models.ActivatedAccountsManager(\*args, \*\*kwargs)
Bases: `accounts.models.CustomUserManager`

Manager for all users that have confirmed their email.


#### get_queryset()
Return a new QuerySet object. Subclasses can override this method to
customize the behavior of the Manager.


### class accounts.models.CustomUser(\*args, \*\*kwargs)
Bases: `django.contrib.auth.models.AbstractUser`, `django.contrib.auth.models.PermissionsMixin`

Custom user model.


#### exception DoesNotExist()
Bases: `django.core.exceptions.ObjectDoesNotExist`


#### exception MultipleObjectsReturned()
Bases: `django.core.exceptions.MultipleObjectsReturned`


#### REQUIRED_FIELDS( = ['first_name', 'last_name'])

#### USERNAME_FIELD( = 'email')

#### activated( = <accounts.models.ActivatedAccountsManager object>)

#### email()

#### email_tracker()

#### property full_name()

#### get_all_permissions(obj=None)

#### get_next_by_date_joined(\*, field=<django.db.models.fields.DateTimeField: date_joined>, is_next=True, \*\*kwargs)

#### get_next_by_last_login(\*, field=<django.db.models.fields.DateTimeField: last_login>, is_next=True, \*\*kwargs)

#### get_previous_by_date_joined(\*, field=<django.db.models.fields.DateTimeField: date_joined>, is_next=False, \*\*kwargs)

#### get_previous_by_last_login(\*, field=<django.db.models.fields.DateTimeField: last_login>, is_next=False, \*\*kwargs)

#### groups()
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


#### has_perm(perm, obj=None)
Return True if the user has the specified permission. Query all
available auth backends, but return immediately if any backend returns
True. Thus, a user who has permission from a single auth backend is
assumed to have permission in general. If an object is provided, check
permissions for that object.


#### host()
Accessor to the related object on the reverse side of a one-to-one
relation.

In the example:

```
class Restaurant(Model):
    place = OneToOneField(Place, related_name='restaurant')
```

`Place.restaurant` is a `ReverseOneToOneDescriptor` instance.


#### id()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### is_admin()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### is_email_confirmed()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### logentry_set()
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


#### objects( = <accounts.models.CustomUserManager object>)

#### profile(: accounts.models.Profile)
Accessor to the related object on the reverse side of a one-to-one
relation.

In the example:

```
class Restaurant(Model):
    place = OneToOneField(Place, related_name='restaurant')
```

`Place.restaurant` is a `ReverseOneToOneDescriptor` instance.


#### refresh_from_db(using=None, fields=None)
Reload field values from the database.

By default, the reloading happens from the database this instance was
loaded from, or by the read router if this instance wasn’t loaded from
any database. The using parameter will override the default.

Fields can be used to specify which fields to reload. The fields
should be an iterable of field attnames. If fields is None, then
all non-deferred fields are reloaded.

When accessing deferred fields of an instance, the deferred loading
of the field will call this method.


#### save_base(raw=False, force_insert=False, force_update=False, using=None, update_fields=None)
Handle the parts of saving which should be done only once per save,
yet need to be done in raw saves, too. This includes some sanity
checks and signal sending.

The ‘raw’ argument is telling save_base not to save any parent
models and not to do any changes to the values before save. This
is used by fixture loading.


#### subscriber()
Accessor to the related object on the reverse side of a one-to-one
relation.

In the example:

```
class Restaurant(Model):
    place = OneToOneField(Place, related_name='restaurant')
```

`Place.restaurant` is a `ReverseOneToOneDescriptor` instance.


#### user_permissions()
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


#### username( = None)

### class accounts.models.CustomUserManager(\*args, \*\*kwargs)
Bases: `django.contrib.auth.base_user.BaseUserManager`

Manager for CustomUser model.


#### create_staffuser(email: str, first_name: str, last_name: str, password: str)

#### create_superuser(email: str, first_name: str, last_name: str, password: str)

#### create_user(email: str, first_name: str, last_name: str, password: Optional[str] = None)

#### get_or_create(email: str, first_name: Optional[str] = None, last_name: Optional[str] = None, password: Optional[str] = None)
Look up an object with the given kwargs, creating one if necessary.
Return a tuple of (object, created), where created is a boolean
specifying whether an object was created.


### class accounts.models.Profile(\*args, \*\*kwargs)
Bases: `django.db.models.base.Model`

Profile for CustomUser.


#### exception DoesNotExist()
Bases: `django.core.exceptions.ObjectDoesNotExist`


#### exception MultipleObjectsReturned()
Bases: `django.core.exceptions.MultipleObjectsReturned`


#### date_of_birth()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### description()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### gender()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### get_gender_display(\*, field=<django.db.models.fields.CharField: gender>)

#### id()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### is_phone_number_confirmed()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### objects( = <django.db.models.manager.Manager object>)

#### phone_number()
The descriptor for the phone number attribute on the model instance.
Returns a PhoneNumber when accessed so you can do stuff like:

```
>>> instance.phone_number.as_international
```

Assigns a phone number object on assignment so you can do:

```
>>> instance.phone_number = PhoneNumber(...)
```

or,

```python
>>> instance.phone_number = '+414204242'
```


#### profile_image()
Just like the FileDescriptor, but for ImageFields. The only difference is
assigning the width/height to the width_field/height_field, if appropriate.


#### sms_log()
Accessor to the related object on the reverse side of a one-to-one
relation.

In the example:

```
class Restaurant(Model):
    place = OneToOneField(Place, related_name='restaurant')
```

`Place.restaurant` is a `ReverseOneToOneDescriptor` instance.


#### user()
Accessor to the related object on the forward side of a one-to-one relation.

In the example:

```
class Restaurant(Model):
    place = OneToOneField(Place, related_name='restaurant')
```

`Restaurant.place` is a `ForwardOneToOneDescriptor` instance.


#### user_id()

### class accounts.models.ProfileGenderChoices(value)
Bases: `django.db.models.enums.TextChoices`

An enumeration.


#### APARTMENTS( = 'O')

#### HOTEL( = 'F')

#### MALE( = 'M')

### class accounts.models.SMSLog(\*args, \*\*kwargs)
Bases: `django.db.models.base.Model`

Log of sms message that is sent to User to verify his phone number.


#### exception DoesNotExist()
Bases: `django.core.exceptions.ObjectDoesNotExist`


#### exception MultipleObjectsReturned()
Bases: `django.core.exceptions.MultipleObjectsReturned`


#### id()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


#### objects( = <django.db.models.manager.Manager object>)

#### profile()
Accessor to the related object on the forward side of a one-to-one relation.

In the example:

```
class Restaurant(Model):
    place = OneToOneField(Place, related_name='restaurant')
```

`Restaurant.place` is a `ForwardOneToOneDescriptor` instance.


#### profile_id()

#### sms_code()
A wrapper for a deferred-loading field. When the value is read from this
object the first time, the query is executed.


### accounts.models.get_default_profile_image()

### accounts.models.get_default_profile_image_full_url()

### accounts.models.get_profile_image_upload_path(instance: accounts.models.Profile, filename: str)
## accounts.services module


### accounts.services.add_user_to_group(user: accounts.models.CustomUser, group_name: str)

### accounts.services.generate_random_sms_code()
Generates random 4 digits code (0000-9999).


### accounts.services.get_user_from_uid(uid)

### accounts.services.get_verification_code_from_digits_dict(digits_dict: Dict[str, str])
Converts dict of digits ({‘key’: ‘digit’, …}) to a verification code.


### accounts.services.handle_phone_number_change(user_profile: accounts.models.Profile, site_domain: str, new_phone_number: str)
Handles phone number change.
- Gets or creates a SMSLog object for the given user_profile
- Generates random verification code and saves it to the SMSLog object
- Sets profile.is_phone_number_confirmed to False
- Sends verification code to the user’s new phone number (celery task)


* **Parameters**

    
    * **user_profile** (*Profile*) – Profile of current user


    * **site_domain** (*str*) – Current site domain (e.g., airbnb, localhost, etc.)


    * **new_phone_number** (*str*) – User’s new phone number



* **Returns**

    None



### accounts.services.is_verification_code_for_profile_valid(user_profile: accounts.models.Profile, verification_code: str)

### accounts.services.send_greeting_email(request: django.http.request.HttpRequest, user: accounts.models.CustomUser)
Send greeting email to the given user.


### accounts.services.send_verification_link(request: django.http.request.HttpRequest, user: accounts.CustomUser)
Send email verification link.


### accounts.services.set_profile_phone_number_confirmed(user_profile: accounts.models.Profile, is_phone_number_confirmed: bool = True)
## accounts.signals module


### accounts.signals.handle_user_sign_up(sender, instance: accounts.CustomUser, created, \*\*kwargs)

### accounts.signals.update_profile(sender, instance: accounts.CustomUser, created, \*\*kwargs)
## accounts.tests module

## accounts.tokens module


### class accounts.tokens.AccountActivationTokenGenerator()
Bases: `django.contrib.auth.tokens.PasswordResetTokenGenerator`

## accounts.urls module

## accounts.views module

## Module contents

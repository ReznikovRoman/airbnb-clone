# common package

## Submodules

## common.collections module


### class common.collections.FormWithModel(form, model)
Bases: `tuple`


#### form(: AbstractForm)
Alias for field number 0


#### model(: AbstractModel)
Alias for field number 1

## common.mixins module


### class common.mixins.SessionDataRequiredMixin()
Bases: `object`

Verify that there is all ‘required_data’ in the session, otherwise redirect to the ‘redirect_url’.


#### dispatch(request: django.http.request.HttpRequest, \*args, \*\*kwargs)

#### redirect_url(: str = None)

#### required_session_data(: Union[List[str], Tuple[str, …]] = None)
## common.services module


### common.services.create_name_with_prefix(name: str, prefix: str)

### common.services.get_field_names_from_form(form: AbstractForm)

### common.services.get_required_fields_from_form_with_model(forms_with_models: List[common.collections.FormWithModel])
Return all required fields from form and linked model.


### common.services.set_prefixes_for_names(names: List[str], prefix: str = '')
## common.session_handler module


### class common.session_handler.SessionHandler(session: django.contrib.sessions.backends.base.SessionBase, keys_collector_name: str, session_prefix: Optional[str] = None)
Bases: `object`

Basic session handler.


#### session()
current session


* **Type**

    SessionBase



#### keys_collector_name()
name of the session variable that stores all app-specific keys


* **Type**

    str



#### session_prefix()
optional prefix that all keys will start with (<prefix>_<key>)


* **Type**

    Optional[str]



#### add_new_item(new_key: str, new_value)

#### add_new_key_to_collector(new_session_key: str)

#### create_initial_dict_with_session_data(initial_keys: Union[List[str], Tuple[str]])

#### delete_given_keys(keys_to_delete: List[str])

#### flush_keys_collector()

#### get_session()

#### update_values_with_given_data(data: dict)
## common.tasks module


### (task)common.tasks.send_sms_by_twilio(body: str, sms_from: str, sms_to: str)
Sends SMS message using Twilio provider


* **Parameters**

    
    * **body** (*str*) – SMS message text


    * **sms_from** (*str*) – Twilio phone number


    * **sms_to** (*str*) – Recipient’s phone number



* **Returns**

    Twilio message SID



* **Return type**

    dict


## common.types module


### class common.types.AuthenticatedHttpRequest()
Bases: `django.http.request.HttpRequest`


#### user(: accounts.models.CustomUser)
## Module contents

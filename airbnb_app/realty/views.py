from typing import List, Optional

from braces.views import JsonRequestResponseMixin

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, reverse
from django.views import generic

from addresses.forms import AddressForm
from addresses.models import Address
from common.collections import FormWithModel
from common.services import get_field_names_from_form, get_keys_with_prefixes, get_required_fields_from_form_with_model
from common.session_handler import SessionHandler
from hosts.models import RealtyHost

from .constants import MAX_REALTY_IMAGES_COUNT, REALTY_FORM_KEYS_COLLECTOR_NAME, REALTY_FORM_SESSION_PREFIX
from .filters import RealtyShortFilter
from .forms import (
    RealtyDescriptionForm, RealtyFiltersForm, RealtyForm, RealtyGeneralInfoForm, RealtyImageFormSet, RealtyTypeForm,
)
from .mixins import RealtySessionDataRequiredMixin
from .models import CustomDeleteQueryset, Realty, RealtyImage
from .services.images import get_images_by_realty_id, update_images_order
from .services.order import convert_response_to_orders
from .services.realty import (
    get_all_available_realty, get_amenity_ids_from_session, get_available_realty_by_city_slug,
    get_available_realty_filtered_by_type, get_available_realty_search_results,
    get_cached_realty_visits_count_by_realty_id, get_or_create_realty_host_by_user, update_realty_visits_count,
)


class RealtySearchResultsView(generic.ListView):
    model = Realty
    template_name = 'realty/realty/search_results.html'
    realty_type_form: RealtyTypeForm = None
    realty_filters_form: RealtyFiltersForm = None

    def dispatch(self, request, *args, **kwargs):
        self.realty_type_form = RealtyTypeForm()
        self.realty_filters_form = RealtyFiltersForm()
        return super(RealtySearchResultsView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        realty_search_results = get_available_realty_search_results(self.request.GET.get('q', None))

        realty_types: List[str] = self.request.GET.getlist('realty_type', None)
        if realty_types:
            realty_search_results = get_available_realty_filtered_by_type(
                realty_types=realty_types,
                realty_qs=realty_search_results,
            )

        realty_search_results = RealtyShortFilter(self.request.GET, realty_search_results).qs

        return realty_search_results

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RealtySearchResultsView, self).get_context_data(**kwargs)
        search_query: str = self.request.GET.get('q')

        context['search_query'] = search_query
        context['realty_count'] = self.get_queryset().count()
        context['realty_type_form'] = self.realty_type_form
        context['realty_filters_form'] = self.realty_filters_form
        context['meta_description'] = f"Search results for `{search_query}`"

        return context


class RealtyListView(generic.ListView):
    """Display all available realty objects."""

    model = Realty
    template_name = 'realty/realty/list.html'
    paginate_by = 3
    realty_type_form: RealtyTypeForm = None
    realty_filters_form: RealtyFiltersForm = None

    def dispatch(self, request, *args, **kwargs):
        self.realty_type_form = RealtyTypeForm()
        self.realty_filters_form = RealtyFiltersForm()
        return super(RealtyListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        available_realty = get_all_available_realty()

        city_slug: str = self.kwargs.get('city_slug', None)
        if city_slug:
            available_realty = get_available_realty_by_city_slug(city_slug=city_slug)

        realty_types: List[str] = self.request.GET.getlist('realty_type', None)
        if realty_types:
            available_realty = get_available_realty_filtered_by_type(
                realty_types=realty_types,
                realty_qs=available_realty,
            )

        available_realty = RealtyShortFilter(data=self.request.GET, queryset=available_realty).qs

        return available_realty

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RealtyListView, self).get_context_data(**kwargs)
        city_slug = self.kwargs.get('city_slug', 'All cities')
        city: str = city_slug.capitalize()

        context['realty_count'] = self.get_queryset().count()
        context['city'] = city
        context['meta_description'] = f"List of places in {city}"
        context['realty_type_form'] = self.realty_type_form
        context['realty_filters_form'] = self.realty_filters_form

        return context


class RealtyDetailView(generic.DetailView):
    """Display a single available Realty."""

    model = Realty
    template_name = 'realty/realty/detail.html'
    queryset = get_all_available_realty()

    def get(self, request: HttpRequest, *args, **kwargs):
        update_realty_visits_count(self.get_object().id)
        return super(RealtyDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RealtyDetailView, self).get_context_data(**kwargs)
        realty_object: Realty = self.get_object()

        context['realty_views_count'] = (
                realty_object.visits_count +
                get_cached_realty_visits_count_by_realty_id(realty_id=realty_object.id)
        )

        return context


class RealtyEditView(
    LoginRequiredMixin,
    RealtySessionDataRequiredMixin,
    generic.base.TemplateResponseMixin,
    generic.View,
):
    """View for creating or updating a single Realty."""

    template_name = 'realty/realty/form.html'

    realty: Realty = None
    address: Address = None
    realty_images: 'CustomDeleteQueryset[RealtyImage]' = None

    is_creating_new_realty: bool = True  # True if we are creating new Realty, False otherwise
    realty_form: RealtyForm = None
    address_form: AddressForm = None
    realty_address_initial: dict = None
    realty_info_initial: dict = None

    session_handler: SessionHandler = None

    def dispatch(self, request: HttpRequest, realty_id: Optional[int] = None, *args, **kwargs):
        self.session_handler = SessionHandler(
            session=request.session,
            keys_collector_name=REALTY_FORM_KEYS_COLLECTOR_NAME,
            session_prefix=REALTY_FORM_SESSION_PREFIX,
        )

        if realty_id is not None:  # if we are editing an existing Realty object
            self.realty = get_object_or_404(Realty, id=realty_id)

            # if a current user is not the host of the Realty
            if (not hasattr(request.user, 'host')) or (self.realty.host != request.user.host):
                return redirect(reverse('realty:all'))

            self.address = self.realty.location
            self.is_creating_new_realty = False
            self.realty_images = self.realty.images.all()
            self.required_session_data = []
        else:
            self.required_session_data = get_keys_with_prefixes(
                names=get_required_fields_from_form_with_model(
                    forms_with_models=[
                        FormWithModel(RealtyGeneralInfoForm, Realty),
                        FormWithModel(AddressForm, Address),
                        FormWithModel(RealtyDescriptionForm, Realty),
                    ],
                ),
                prefix=REALTY_FORM_SESSION_PREFIX,
            )

            self.realty_info_initial = self.session_handler.get_items_by_keys(
                keys=get_field_names_from_form(RealtyForm),
            )
            # handle m2m field
            self.realty_info_initial['amenities'] = get_amenity_ids_from_session(self.session_handler)

            self.realty_address_initial = self.session_handler.get_items_by_keys(
                keys=get_field_names_from_form(AddressForm),
            )

        self.realty_form = RealtyForm(
            data=request.POST or None,
            instance=self.realty,
            initial=self.realty_info_initial,
        )
        self.address_form = AddressForm(
            data=request.POST or None,
            instance=self.address,
            initial=self.realty_address_initial,
        )
        return super(RealtyEditView, self).dispatch(request, realty_id, *args, **kwargs)

    def get(self, request: HttpRequest, realty_id: Optional[int] = None, *args, **kwargs):
        realty_image_formset = RealtyImageFormSet(queryset=get_images_by_realty_id(realty_id))

        return self.render_to_response(
            context={
                'realty_form': self.realty_form,
                'address_form': self.address_form,
                'realty_image_formset': realty_image_formset,
                'is_creating_new_realty': self.is_creating_new_realty,
                'realty_images': self.realty_images,
                'max_realty_images_count': MAX_REALTY_IMAGES_COUNT,
            },
        )

    def post(self, request: HttpRequest, realty_id: Optional[int] = None, *args, **kwargs):
        realty_image_formset = RealtyImageFormSet(
            data=request.POST,
            files=request.FILES,
            queryset=get_images_by_realty_id(realty_id),
        )

        if self.realty_form.is_valid():
            new_realty: Realty = self.realty_form.save(commit=False)
            realty_host: RealtyHost = get_or_create_realty_host_by_user(user=request.user)[0]
            new_realty.host = realty_host

            if self.address_form.is_valid():
                new_address: Address = self.address_form.save()
                new_realty.location = new_address

                if realty_id is None:  # if it is a new Realty
                    self.session_handler.flush_keys_collector()

                new_realty.save()
                self.realty_form.save_m2m()

                if realty_image_formset.is_valid():
                    valid_image_formsets = [
                        image_formset
                        for image_formset in realty_image_formset
                        if image_formset.cleaned_data
                    ]
                    for image_form in valid_image_formsets:
                        new_image: RealtyImage = image_form.save(commit=False)
                        new_image.realty = new_realty
                        new_image.save()

            # TODO: Redirect to Host's listings dashboard
            return redirect(reverse('realty:all'))

        return self.render_to_response(
            context={
                'realty_form': self.realty_form,
                'address_form': self.address_form,
                'realty_image_formset': realty_image_formset,
                'is_creating_new_realty': self.is_creating_new_realty,
                'realty_images': self.realty_images,
                'max_realty_images_count': MAX_REALTY_IMAGES_COUNT,
            },
        )


class RealtyGeneralInfoEditView(
    LoginRequiredMixin,
    generic.base.TemplateResponseMixin,
    generic.View,
):
    """View for editing Realty general info (part of the multi-step form).

    Step-1
    """

    template_name = 'realty/realty/creation_steps/step_1_general_info.html'

    realty_form: Optional[RealtyGeneralInfoForm] = None
    session_handler: SessionHandler = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.session_handler = SessionHandler(
            session=request.session,
            keys_collector_name=REALTY_FORM_KEYS_COLLECTOR_NAME,
            session_prefix=REALTY_FORM_SESSION_PREFIX,
        )
        initial = self.session_handler.get_items_by_keys(
            keys=get_field_names_from_form(RealtyGeneralInfoForm),
        )
        # handle m2m field
        initial['amenities'] = get_amenity_ids_from_session(self.session_handler)

        self.realty_form = RealtyGeneralInfoForm(request.POST or None, initial=initial)
        return super(RealtyGeneralInfoEditView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'realty_form': self.realty_form,
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        if self.realty_form.is_valid():
            self.session_handler.create_or_update_items(data=self.realty_form.cleaned_data)

            # 'serialize' m2m field
            self.session_handler.add_new_item(
                new_key='amenities',
                new_value=[amenity.name for amenity in self.realty_form.cleaned_data['amenities']],
            )

            return redirect(reverse('realty:new_realty_location'))
        return self.render_to_response(
            context={
                'realty_form': self.realty_form,
            },
        )


class RealtyLocationEditView(
    LoginRequiredMixin,
    RealtySessionDataRequiredMixin,
    generic.base.TemplateResponseMixin,
    generic.View,
):
    """View for editing Realty location (part of the multi-step form).

    Step-2
    """

    template_name = 'realty/realty/creation_steps/step_2_location.html'

    required_session_data = get_keys_with_prefixes(
        names=get_required_fields_from_form_with_model(
            forms_with_models=[
                FormWithModel(RealtyGeneralInfoForm, Realty),
            ],
        ),
        prefix=REALTY_FORM_SESSION_PREFIX,
    )
    location_form: AddressForm = None
    session_handler: SessionHandler = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.session_handler = SessionHandler(
            session=request.session,
            keys_collector_name=REALTY_FORM_KEYS_COLLECTOR_NAME,
            session_prefix=REALTY_FORM_SESSION_PREFIX,
        )
        initial = self.session_handler.get_items_by_keys(keys=get_field_names_from_form(AddressForm))
        self.location_form = AddressForm(request.POST or None, initial=initial)
        return super(RealtyLocationEditView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'location_form': self.location_form,
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        if self.location_form.is_valid():
            self.session_handler.create_or_update_items(data=self.location_form.cleaned_data)
            return redirect(reverse('realty:new_realty_description'))

        return self.render_to_response(
            context={
                'location_form': self.location_form,
            },
        )


class RealtyDescriptionEditView(
    LoginRequiredMixin,
    RealtySessionDataRequiredMixin,
    generic.base.TemplateResponseMixin,
    generic.View,
):
    """View for editing realty description (part of multi-step form).

    Step-3
    """

    template_name = 'realty/realty/creation_steps/step_3_description.html'

    required_session_data = get_keys_with_prefixes(
        names=get_required_fields_from_form_with_model(
            forms_with_models=[
                FormWithModel(RealtyGeneralInfoForm, Realty),
                FormWithModel(AddressForm, Address),
            ],
        ),
        prefix=REALTY_FORM_SESSION_PREFIX,
    )
    description_form: RealtyDescriptionForm = None
    session_handler: SessionHandler = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.session_handler = SessionHandler(
            session=request.session,
            keys_collector_name=REALTY_FORM_KEYS_COLLECTOR_NAME,
            session_prefix=REALTY_FORM_SESSION_PREFIX,
        )
        initial = self.session_handler.get_items_by_keys(
            keys=get_field_names_from_form(RealtyDescriptionForm),
        )
        self.description_form = RealtyDescriptionForm(request.POST or None, initial=initial)
        return super(RealtyDescriptionEditView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'description_form': self.description_form,
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        if self.description_form.is_valid():
            self.session_handler.create_or_update_items(data=self.description_form.cleaned_data)
            return redirect(reverse('realty:new_realty'))
        return self.render_to_response(
            context={
                'description_form': self.description_form,
            },
        )


class RealtyImageOrderView(
    LoginRequiredMixin,
    JsonRequestResponseMixin,
    generic.View,
):
    """View for changing RealtyImages' order."""

    def post(self, request, *args, **kwargs):
        response = list(self.request_json.items())
        update_images_order(new_order=convert_response_to_orders(response))
        return self.render_json_response(
            context_dict={
                'saved': 'OK',
            },
        )

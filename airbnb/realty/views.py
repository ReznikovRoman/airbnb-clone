from typing import Optional

from django.views import generic
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, reverse, redirect
from django.db.models import QuerySet
from django.contrib.auth.mixins import LoginRequiredMixin

from addresses.forms import AddressForm
from addresses.models import Address
from hosts.models import RealtyHost
from .models import Realty, RealtyImage, CustomDeleteQueryset
from .forms import RealtyForm, RealtyTypeForm, RealtyImageFormSet
from .constants import MAX_REALTY_IMAGES_COUNT
from .services.images import get_realty_images_by_realty_id


class RealtyListView(generic.ListView):
    """Display all realty objects."""
    model = Realty
    template_name = 'realty/realty/list.html'
    paginate_by = 3
    realty_type_form = None

    def dispatch(self, request, *args, **kwargs):
        # TODO: get initial form data from session
        self.realty_type_form = RealtyTypeForm()
        return super(RealtyListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        available_realty = Realty.available.all()

        city_slug = self.kwargs.get('city_slug', None)
        if city_slug:
            available_realty = available_realty.filter(location__city_slug=city_slug)

        realty_types = self.request.GET.getlist('realty_type', None)
        if realty_types:
            available_realty = available_realty.filter(realty_type__in=realty_types)

        return available_realty

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RealtyListView, self).get_context_data(**kwargs)
        context['realty_count'] = self.get_queryset().count()

        city_slug = self.kwargs.get('city_slug', 'All cities')
        context['city'] = city_slug.capitalize()

        context['realty_type_form'] = self.realty_type_form
        return context


class RealtyDetailView(generic.DetailView):
    """Display a single Realty."""
    model = Realty
    template_name = 'realty/realty/detail.html'


class RealtyEditView(LoginRequiredMixin,
                     generic.base.TemplateResponseMixin,
                     generic.View):
    """View for creating or updating a single Realty."""
    template_name = 'realty/realty/form.html'
    realty: Optional[Realty] = None
    address: Optional[Address] = None
    realty_images: Optional[CustomDeleteQueryset[RealtyImage]] = None
    is_creating_new_realty: bool = True  # True if we are creating new Realty, False otherwise

    def dispatch(self, request: HttpRequest, realty_id: Optional[int] = None, *args, **kwargs):
        if realty_id:  # if we are editing an existing Realty object
            self.realty = get_object_or_404(Realty, id=realty_id)
            self.address = self.realty.location
            self.is_creating_new_realty = False
            self.realty_images = self.realty.images.all()

        return super(RealtyEditView, self).dispatch(request, realty_id, *args, **kwargs)

    def get(self, request: HttpRequest, realty_id: Optional[int] = None, *args, **kwargs):
        realty_form = RealtyForm(instance=self.realty)
        address_form = AddressForm(instance=self.address)
        realty_image_formset = RealtyImageFormSet(queryset=get_realty_images_by_realty_id(realty_id))

        return self.render_to_response(
            context={
                'realty_form': realty_form,
                'address_form': address_form,
                'realty_image_formset': realty_image_formset,
                'is_creating_new_realty': self.is_creating_new_realty,
                'realty_images': self.realty_images,
                'max_realty_images_count': MAX_REALTY_IMAGES_COUNT,
            }
        )

    def post(self, request: HttpRequest, realty_id: Optional[int] = None, *args, **kwargs):
        realty_form = RealtyForm(data=request.POST, instance=self.realty)
        address_form = AddressForm(data=request.POST, instance=self.address)
        realty_image_formset = RealtyImageFormSet(
            data=request.POST,
            files=request.FILES,
            queryset=get_realty_images_by_realty_id(realty_id),
        )

        if realty_form.is_valid():
            new_realty: Realty = realty_form.save(commit=False)

            # TODO: Set realty host properly (User registration, permissions - another milestone)
            new_realty.host = RealtyHost.objects.first()

            if address_form.is_valid():
                new_address: Address = address_form.save()
                new_realty.location = new_address
                new_realty.save()

                realty_form.save_m2m()  # save many to many fields

                if realty_image_formset.is_valid():
                    valid_image_formsets = [image_formset for image_formset in realty_image_formset
                                            if image_formset.cleaned_data]
                    for image_form in valid_image_formsets:
                        new_image: RealtyImage = image_form.save(commit=False)
                        new_image.realty = new_realty
                        new_image.save()

                return redirect(reverse('realty:detail', kwargs={'slug': new_realty.slug}))

        return self.render_to_response(
            context={
                'realty_form': realty_form,
                'address_form': address_form,
                'realty_image_formset': realty_image_formset,
                'is_creating_new_realty': self.is_creating_new_realty,
                'realty_images': self.realty_images,
                'max_realty_images_count': MAX_REALTY_IMAGES_COUNT,
            }
        )


'''

Realty multi-step form (saving data in the session)

Step - 1:
    - Name/Title
    - Property type

Step - 2:
    - Beds count
    - Max guests count
    - Price per night

Step - 3:
    - Amenities (inline formset):
        - Amenity name (select from multiple choices)

Step - 4:
    - location (inline formset):
        - Country
        - City
        - Street

Step - 5:
    - Realty description
    
--- SAVE REALTY ---

Step - 6:
    - Realty images (inline formset), max - 6 images:
        - Image - ajax form submission
        
'''

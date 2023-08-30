from django.contrib import admin
from django import forms
from multiupload.fields import MultiFileField
from .models import Product, ProductImage, ShippingInfo, Raffle, Series, SeriesImage
from django.db.models import Q


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductForm(forms.ModelForm):
    files = MultiFileField(min_num=1, max_num=5, max_file_size=1024 * 1024 * 5)

    class Meta:
        model = Product
        fields = '__all__'

    def save(self, commit=True):
        product = super().save(commit=commit)

        images = self.cleaned_data.get('images')
        if images:
            for image in images:
                ProductImage.objects.create(product=product, file=image)

        return product


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    list_filter = ['name', 'description']
    search_fields = ['name', 'description']
    ordering = ['name', 'description']
    inlines = [ProductImageInline]


admin.site.register(Product, ProductAdmin)


class ShippingInfoForm(forms.ModelForm):
    class Meta:
        model = ShippingInfo
        fields = '__all__'

    def save(self, commit=True):
        shipping_info = super().save(commit=commit)
        return shipping_info


class ShippingInfoAdmin(admin.ModelAdmin):
    list_display = ['shipping_locations', 'width', 'height', 'depth', 'weight']


admin.site.register(ShippingInfo, ShippingInfoAdmin)


class RaffleForm(forms.ModelForm):
    class Meta:
        model = Raffle
        fields = '__all__'

    def save(self, commit=True):
        raffle = super().save(commit=commit)
        return raffle


class RaffleAdmin(admin.ModelAdmin):
    list_display = ['begin_datetime', 'end_datetime', 'product',
                    'product_price', 'ticket_price', 'num_pairs', 'shipping_info']


admin.site.register(Raffle, RaffleAdmin)


class SeriesImageInline(admin.TabularInline):
    model = SeriesImage
    extra = 1


class SeriesForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = '__all__'


class SeriesForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = '__all__'


class SeriesAdmin(admin.ModelAdmin):
    list_display = ['name']
    raw_id_fields = ['brand']
    inlines = [SeriesImageInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj is None:
            form.base_fields['brand'].initial = request.user.id
            # Make the field read-only
            form.base_fields['brand'].disabled = True

        return form


admin.site.register(Series, SeriesAdmin)

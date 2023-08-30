from datetime import datetime
import os
from django.shortcuts import redirect, render
from django.contrib import messages

from raffleshop import settings
from .forms import NewUserForm
from .models import DeliveryAddress, PaymentInfo, Product, ProductImage, Raffle, Series, ShippingInfo, Ticket
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate


def home(request):
    nike_raffles = Raffle.objects.filter(
        product__series__brand__first_name='Nike')
    nb_raffles = Raffle.objects.filter(
        product__series__brand__first_name='New Balance')
    adidas_raffles = Raffle.objects.filter(
        product__series__brand__first_name='Adidas')
    air_raffles = Raffle.objects.filter(
        product__series__brand__first_name='Air Jordan')
    return render(request, "home.html", {'nike_raffles': nike_raffles,
                                         'nb_raffles': nb_raffles,
                                         'adidas_raffles': adidas_raffles,
                                         'air_raffles': air_raffles})


def raffle(request, identifier):
    requested_raffle = Raffle.objects.get(id=identifier)
    series_from_brand = Series.objects.filter(
        brand=requested_raffle.product.series.brand)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect("login")

        ticket, created = Ticket.objects.get_or_create(checked_out=False, raffle=requested_raffle,
                                                       shopping_cart=request.user.user_profile.shopping_cart)
        if created:
            ticket.save()
            messages.success(request, f"Ticked added to cart!")
        else:
            messages.info(request, f"Ticked already in cart.")

    if request.user.is_authenticated:
        already_has_ticket = Ticket.objects.filter(
            raffle=requested_raffle, shopping_cart=request.user.user_profile.shopping_cart).exists()
        has_bought_ticket = Ticket.objects.filter(checked_out=True,
                                                  raffle=requested_raffle,
                                                  shopping_cart=request.user.user_profile.shopping_cart).exists()
        return render(request, "raffle.html", {'raffle': requested_raffle,
                                               'series_from_brand': series_from_brand,
                                               'already_has_ticket': already_has_ticket,
                                               'has_bought_ticket': has_bought_ticket})

    return render(request, "raffle.html", {'raffle': requested_raffle,
                                           'series_from_brand': series_from_brand})


def series(request, identifier):
    series = Series.objects.get(id=identifier)
    raffles_for_series = Raffle.objects.filter(product__series=series)
    return render(request, "series.html", {'series': series, 'raffles_for_series': raffles_for_series})


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"You have successfully logged in!")
                return redirect("home")
            else:
                messages.error(request, "Invalid credentials.")
        else:
            messages.error(request, "Invalid credentials.")
    else:
        if request.user.is_authenticated:
            return redirect("home")
        form = AuthenticationForm()
    return render(request, "login.html", {'login_form': form})


def logout(request):
    auth_logout(request)
    messages.info(request, "You have logged out.")
    return redirect("home")


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account successfuly created!')
            auth_login(request, user)
            return redirect("home")
    else:
        if request.user.is_authenticated:
            return redirect("home")
        form = NewUserForm()
    return render(request, "register.html", {"register_form": form})


def cart(request):
    if not request.user.is_authenticated:
        return redirect("login")

    unchecked_tickets = Ticket.objects.filter(checked_out=False,
                                              shopping_cart=request.user.user_profile.shopping_cart)
    checked_tickets = Ticket.objects.filter(checked_out=True,
                                            shopping_cart=request.user.user_profile.shopping_cart)

    return render(request, "cart.html", {"unchecked_tickets": unchecked_tickets,
                                         "checked_tickets": checked_tickets})


def checkout_shipping(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        new_city = request.POST.get("new_city")
        new_street = request.POST.get("new_street")
        new_postal_code = request.POST.get("new_postal_code")

        new_address, created = DeliveryAddress.objects.get_or_create(
            city=new_city,
            street=new_street,
            postal_code=new_postal_code,
            user=request.user
        )

        return redirect("checkout_shipping")

    tickets = Ticket.objects.filter(checked_out=False,
                                    shopping_cart=request.user.user_profile.shopping_cart)
    total_ticket_price = sum(ticket.raffle.ticket_price for ticket in tickets)

    return render(request, "checkout_shipping.html", {'tickets': tickets, 'total_ticket_price': total_ticket_price})


def checkout_payment(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        payment_action = request.POST.get("payment_action")
        print(payment_action)
        new_card_type = request.POST.get("new_card_type")
        new_name_on_card = request.POST.get("new_name_on_card")
        new_cvv = request.POST.get("new_cvv")

        new_address, created = PaymentInfo.objects.get_or_create(
            card_type=new_card_type,
            name_on_card=new_name_on_card,
            cvv=new_cvv,
            user=request.user
        )

        return redirect("checkout_payment")

    tickets = Ticket.objects.filter(checked_out=False,
                                    shopping_cart=request.user.user_profile.shopping_cart)
    total_ticket_price = sum(ticket.raffle.ticket_price for ticket in tickets)

    return render(request, "checkout_payment.html", {'tickets': tickets, 'total_ticket_price': total_ticket_price})


def to_payment(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        # TODO: Process address
        return redirect("checkout_payment")


def complete_payment(request):
    if not request.user.is_authenticated:
        return redirect("login")

    # TODO: Process payment
    for ticket in Ticket.objects.filter(shopping_cart=request.user.user_profile.shopping_cart):
        ticket.checked_out = True
        ticket.save()

    messages.success(request, f"Tickets purchased successfully!")
    return redirect("home")


def sellers(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_staff:
                auth_login(request, user)
                return redirect("sellers_dashboard")
            else:
                messages.error(request, "Invalid credentials.")
        else:
            messages.error(request, "Invalid credentials.")
    else:
        if request.user.is_authenticated:
            return redirect("sellers_dashboard")
        form = AuthenticationForm()
    return render(request, "sellers.html", {'login_form': form})


def sellers_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect("home")
    raffles_from_seller = Raffle.objects.filter(
        product__series__brand__username=request.user.username)
    series_from_seller = Series.objects.filter(
        brand__username=request.user.username)
    return render(request, "sellers_dashboard.html", {'raffles': raffles_from_seller,
                                                      'series': series_from_seller})


def save_uploaded_file(uploaded_file):
    unique_filename = f"uploaded_{uploaded_file.name}"

    file_path = os.path.join(
        settings.MEDIA_ROOT, 'product_images', unique_filename)

    with open(file_path, 'wb') as destination_file:
        for chunk in uploaded_file.chunks():
            destination_file.write(chunk)

    return file_path


def create_product(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect("home")

    if request.method == 'POST':
        pipe = {}
        uploaded_images = request.FILES.getlist('images')
        uploaded_image_paths = []
        for uploaded_image in uploaded_images:
            uploaded_image_path = save_uploaded_file(uploaded_image)
            uploaded_image_paths.append(uploaded_image_path)
        pipe['images'] = uploaded_image_paths
        pipe['name'] = request.POST.get('name')
        pipe['description'] = request.POST.get('description')
        pipe['series_id'] = request.POST.get('series')

        request.method = 'GET'
        return create_raffle_first(request, pipe=pipe)


def create_raffle_first(request, pipe=None):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect("home")

    if request.method == 'POST':
        pipe = request.session.get('pipe', {})
        pipe['product_price'] = request.POST.get('product_price')
        pipe['ticket_price'] = request.POST.get('ticket_price')
        pipe['num_pairs'] = request.POST.get('num_pairs')

        request.method = 'GET'
        return create_raffle_second(request, pipe)

    raffles_from_seller = Raffle.objects.filter(
        product__series__brand__username=request.user.username)
    series_from_seller = Series.objects.filter(
        brand__username=request.user.username)

    request.session['pipe'] = pipe

    return render(request, "create_raffle_first.html", {'raffles': raffles_from_seller, 'series': series_from_seller})


def create_raffle_second(request, pipe=None):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect("home")

    if request.method == 'POST':
        pipe = request.session.get('pipe', {})
        width = request.POST.get('width')
        height = request.POST.get('height')
        depth = request.POST.get('depth')
        weight = request.POST.get('weight')
        shipping_locations = request.POST.getlist('shipping_locations')

        begin_datetime_str = request.POST.get('begin_datetime')
        end_datetime_str = request.POST.get('end_datetime')
        begin_datetime = datetime.strptime(
            begin_datetime_str, '%Y-%m-%dT%H:%M')
        end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M')

        product = Product(
            name=pipe['name'],
            description=pipe['description'],
            series_id=pipe['series_id']
        )
        product.save()

        shipping_info = ShippingInfo(
            width=width,
            height=height,
            depth=depth,
            weight=weight,
            shipping_locations=shipping_locations
        )
        shipping_info.save()

        raffle = Raffle(
            begin_datetime=begin_datetime,
            end_datetime=end_datetime,
            product=product,
            product_price=pipe['product_price'],
            ticket_price=pipe['ticket_price'],
            num_pairs=pipe['num_pairs'],
            shipping_info=shipping_info
        )
        raffle.save()

        uploaded_image_paths = pipe.get('images', [])
        for image_path in uploaded_image_paths:
            product_image = ProductImage(
                description="Description",
                product=product,
                file=image_path
            )
            product_image.save()

        messages.success(request, f"Raffle successfully created!")
        return sellers_dashboard(request)

    raffles_from_seller = Raffle.objects.filter(
        product__series__brand__username=request.user.username)
    series_from_seller = Series.objects.filter(
        brand__username=request.user.username)
    shipping_locations = ShippingInfo.LOCATION_CHOICES

    request.session['pipe'] = pipe

    return render(request, "create_raffle_second.html", {'raffles': raffles_from_seller, 'series': series_from_seller, 'shipping_locations': shipping_locations})

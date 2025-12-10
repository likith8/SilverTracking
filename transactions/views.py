from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import SilverGiven, ProductReturn
from .forms import SilverGivenForm, ProductReturnForm
from customers.models import Customer
from products.models import Product
from django.db.models import Q
from datetime import datetime,date
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils import timezone
from django.db.models import Sum
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
# -------------------------------------------------------
# Helper: Parse date from GET
# -------------------------------------------------------
def _parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except:
        return None


# =======================================================
#                 SILVER GIVEN
# =======================================================

def silver_given_create(request):
    if request.method == 'POST':
        form = SilverGivenForm(request.POST)
        if form.is_valid():
            silver = form.save(commit=False)
            customer = silver.customer

            # ADD to customer balance
            customer.opening_balance += silver.weight
            customer.opening_balance = round(customer.opening_balance, 3)
            customer.save()

            silver.save()
            return redirect('transactions:silver_given_list')
    else:
        form = SilverGivenForm()

    return render(request, 'transactions/silver_given_form.html', {'form': form})


def silver_given_edit(request, pk):
    record = get_object_or_404(SilverGiven, pk=pk)
    original_weight = record.weight

    if request.method == 'POST':
        form = SilverGivenForm(request.POST, instance=record)
        if form.is_valid():
            updated = form.save(commit=False)
            customer = updated.customer

            # Only adjust by difference
            delta = updated.weight - original_weight
            customer.opening_balance += delta
            customer.opening_balance = round(customer.opening_balance, 3)
            customer.save()

            updated.save()
            return redirect('transactions:silver_given_list')

    else:
        form = SilverGivenForm(instance=record)

    return render(request, 'transactions/silver_given_form.html', {'form': form, 'edit': True})


def silver_given_delete(request, pk):
    record = get_object_or_404(SilverGiven, pk=pk)
    next_page = request.GET.get('next', 'transactions:silver_given_list')

    if request.method == "POST":
        customer = record.customer

        # Reverse the effect
        customer.opening_balance -= record.weight
        customer.opening_balance = round(customer.opening_balance, 3)
        customer.save()

        record.delete()
        return redirect(next_page)

    return render(request, 'transactions/confirm_delete.html', {'record': record, 'next_page': next_page})


def silver_given_list(request):
    qs = SilverGiven.objects.select_related('customer').order_by('-date')

    start = _parse_date(request.GET.get('start_date', ''))
    end = _parse_date(request.GET.get('end_date', ''))
    customer_id = request.GET.get('customer', '')
    q = request.GET.get('q', '').strip()

    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    if customer_id:
        qs = qs.filter(customer_id=customer_id)
    if q:
        qs = qs.filter(
            Q(customer__name__icontains=q) |
            Q(weight__icontains=q) |
            Q(date__icontains=q)
        )

    customers = Customer.objects.all()

    return render(request, 'transactions/silver_given_list.html', {
        'records': qs,
        'customers': customers,
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
        'customer_selected': customer_id,
        'q': q,
    })


# =======================================================
#                 PRODUCT RETURN
# =======================================================

def product_return_create(request):
    products = Product.objects.all()

    if request.method == 'POST':
        form = ProductReturnForm(request.POST)
        if form.is_valid():
            pr = form.save(commit=False)

            # Pure weight
            pr.pure_weight = pr.gross_weight * (pr.melting_percent / 100)

            # MC calculation
            product = pr.product
            if product.mc_type == 'per_gram':
                pr.mc_amount = round(pr.gross_weight * product.mc_rate, 3)
            else:
                pr.mc_amount = round((pr.gross_weight / 1000) * product.mc_rate, 3)

            # Subtract pure weight from customer balance
            customer = pr.customer
            customer.opening_balance -= pr.pure_weight
            customer.opening_balance = round(customer.opening_balance, 3)
            customer.save()

            pr.save()
            return redirect('transactions:product_return_list')
    else:
        form = ProductReturnForm()

    return render(request, 'transactions/product_return_form.html', {
        'form': form,
        'products': products,
        'edit': False,
    })


def product_return_edit(request, pk):
    record = get_object_or_404(ProductReturn, pk=pk)
    original_pure = record.pure_weight
    products = Product.objects.all()

    if request.method == 'POST':
        form = ProductReturnForm(request.POST, instance=record)
        if form.is_valid():
            updated = form.save(commit=False)

            # Recalculate pure weight
            updated.pure_weight = updated.gross_weight * (updated.melting_percent / 100)

            # Recalculate MC
            product = updated.product
            if product.mc_type == 'per_gram':
                updated.mc_amount = round(updated.gross_weight * product.mc_rate, 3)
            else:
                updated.mc_amount = round((updated.gross_weight / 1000) * product.mc_rate, 3)

            # Adjust by difference
            customer = updated.customer
            delta = updated.pure_weight - original_pure
            customer.opening_balance -= delta
            customer.opening_balance = round(customer.opening_balance, 3)
            customer.save()

            updated.save()
            return redirect('transactions:product_return_list')

    else:
        form = ProductReturnForm(instance=record)

    return render(request, 'transactions/product_return_form.html', {
        'form': form,
        'products': products,
        'edit': True,
    })


def product_return_delete(request, pk):
    record = get_object_or_404(ProductReturn, pk=pk)
    next_page = request.GET.get('next', 'transactions:product_return_list')

    if request.method == "POST":
        customer = record.customer

        # Reverse the effect
        customer.opening_balance += record.pure_weight
        customer.opening_balance = round(customer.opening_balance, 3)
        customer.save()

        record.delete()
        return redirect(next_page)

    return render(request, 'transactions/confirm_delete.html', {'record': record, 'next_page': next_page})


def product_return_list(request):
    qs = ProductReturn.objects.select_related('customer', 'product').order_by('-date')

    start = _parse_date(request.GET.get('start_date', ''))
    end = _parse_date(request.GET.get('end_date', ''))
    customer_id = request.GET.get('customer', '')
    q = request.GET.get('q', '').strip()
    mc_status = request.GET.get('mc_status', '')

    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    if customer_id:
        qs = qs.filter(customer_id=customer_id)
    if q:
        qs = qs.filter(
            Q(customer__name__icontains=q) |
            Q(product__name__icontains=q) |
            Q(gross_weight__icontains=q) |
            Q(mc_amount__icontains=q)
        )
    if mc_status == 'given':
        qs = qs.filter(mc_given=True)
    elif mc_status == 'not_given':
        qs = qs.filter(mc_given=False)

    customers = Customer.objects.all()

    return render(request, 'transactions/product_return_list.html', {
        'records': qs,
        'customers': customers,
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
        'customer_selected': customer_id,
        'q': q,
        'mc_status': mc_status,
    })


# =======================================================
#                 TRANSACTION REPORT
# =======================================================
def transactions_report(request):
    customers = Customer.objects.all()

    selected_customer = request.GET.get("customer_id")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    download = request.GET.get("download")  # check if PDF requested

    silver_records = return_records = []
    total_given = total_return = 0
    current_balance = opening_range_balance = closing_range_balance = None
    customer = None

    # ---- FETCH CUSTOMER ----
    if selected_customer:
        customer = Customer.objects.get(id=selected_customer)
        current_balance = customer.opening_balance  # running balance stored in DB

    # ---- BUILD DATE FILTER ----
    filters = {}
    if selected_customer:
        filters["customer_id"] = selected_customer
    if from_date:
        filters["date__gte"] = from_date
    if to_date:
        filters["date__lte"] = to_date

    # ---- FETCH RANGE DATA ----
    silver_records = SilverGiven.objects.filter(**filters).order_by("date")
    return_records = ProductReturn.objects.filter(**filters).order_by("date")

    total_given = silver_records.aggregate(Sum("weight"))["weight__sum"] or 0
    total_return = return_records.aggregate(Sum("pure_weight"))["pure_weight__sum"] or 0

    # ---- CALCULATE OPENING BALANCE FOR SELECTED DATE RANGE ----
    if customer and from_date:
        silver_after = SilverGiven.objects.filter(
            customer=customer,
            date__gt=from_date
        ).aggregate(total=Sum('weight'))['total'] or 0

        return_after = ProductReturn.objects.filter(
            customer=customer,
            date__gt=from_date
        ).aggregate(total=Sum('pure_weight'))['total'] or 0

        opening_range_balance = customer.opening_balance - silver_after + return_after

    # ---- CALCULATE CLOSING BALANCE FOR SELECTED DATE RANGE ----
    if opening_range_balance is not None:
        closing_range_balance = opening_range_balance + total_given - total_return

    # ---- PREPARE RECORDS FOR PDF ----
    records = []

    if opening_range_balance is not None:
        records.append({
            "type": "Opening",
            "balance": opening_range_balance
        })

    for s in silver_records:
        records.append({
            "type": "Silver Given",
            "gross_weight": s.weight,
            "date": s.date.strftime("%d-%b-%Y"),
            "balance": None  # optional: running balance
        })

    for r in return_records:
        records.append({
            "type": "Product Return",
            "gross_return_weight":r.gross_weight,
            "pure_weight": r.pure_weight,
            "mc_amount": r.mc_amount,
            "product": r.product.name,
            "date": r.date.strftime("%d-%b-%Y"),
            "mc_given": r.mc_given,
            "balance": None  # optional
        })

    if closing_range_balance is not None:
        records.append({
            "type": "Closing",
            "balance": closing_range_balance
        })

    # ---- PDF DOWNLOAD ----
    if download == "invoice":
        template_path = "transactions/invoice_pdf.html"
        from_date_obj = None
        to_date_obj = None

        if from_date:
            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()

        if to_date:
            to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
        context = {
            "shop_name": "Sri Saravana Silver Works",
            "shop_address": "No 8/3 c cross Magadi Road GopalPuram",
            "shop_phone": "8310867726",
            "shop_email": "1618sanju@gmail.com",
            "customer": customer,
            "records": records,
            "total_given": total_given,
            "total_return": total_return,
            "balance": closing_range_balance or current_balance or 0,
            "current_balance": current_balance,
            "opening_range_balance": opening_range_balance,
            "closing_range_balance": closing_range_balance,
            "from_date": from_date_obj,
            "to_date": to_date_obj,
            "today": date.today().strftime("%d-%b-%Y"),
        }

        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="invoice_{customer.name if customer else "all"}.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse("We had some errors generating the PDF <pre>" + html + "</pre>")
        return response

    # ---- REGULAR HTML RENDER ----
    return render(request, "transactions/report.html", {
        "customers": customers,
        "selected_customer": selected_customer,
        "from_date": from_date,
        "to_date": to_date,
        "silver_records": silver_records,
        "return_records": return_records,
        "total_given": total_given,
        "total_return": total_return,
        "current_balance": current_balance,
        "opening_range_balance": opening_range_balance,
        "closing_range_balance": closing_range_balance,
    })
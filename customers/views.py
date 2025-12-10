from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer
from .forms import CustomerForm


# -------------------------------
# LIST
# -------------------------------
def customer_list(request):
    customers = Customer.objects.all().order_by('id')
    return render(request, 'customers/customer_list.html', {'customers': customers})


# -------------------------------
# CREATE
# -------------------------------
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customers:customer_list')
    else:
        form = CustomerForm()

    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Add Customer'})


# -------------------------------
# EDIT / UPDATE
# -------------------------------
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customers:customer_list')
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Edit Customer'})


# -------------------------------
# DELETE
# -------------------------------
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        entered_name = request.POST.get('confirm_name', '').strip()

        if entered_name == customer.name:
            # Delete customer and all related records automatically via CASCADE
            customer.delete()
            return redirect('customers:customer_list')
        else:
            return render(
                request,
                'customers/customer_confirm_delete.html',
                {
                    'customer': customer,
                    'error': 'Name does not match. Please type the exact customer name.'
                }
            )

    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})

from django.shortcuts import render
from .models import SilverGiven, ProductReturn
from customers.models import Customer
from datetime import datetime
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

# helper to parse date
def _parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except:
        return None

# -----------------------
# REPORT - View
# -----------------------
def transactions_report(request):
    start = _parse_date(request.GET.get('start_date', ''))
    end = _parse_date(request.GET.get('end_date', ''))

    silver_qs = SilverGiven.objects.select_related('customer').all()
    return_qs = ProductReturn.objects.select_related('customer', 'product').all()

    if start:
        silver_qs = silver_qs.filter(date__gte=start)
        return_qs = return_qs.filter(date__gte=start)
    if end:
        silver_qs = silver_qs.filter(date__lte=end)
        return_qs = return_qs.filter(date__lte=end)

    customers = Customer.objects.all()

    # Check if PDF download
    if request.GET.get('download') == 'pdf':
        template_path = 'transactions/report_pdf.html'
        context = {
            'silver_records': silver_qs,
            'return_records': return_qs,
            'customers': customers,
            'start_date': start,
            'end_date': end,
        }
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="transactions_report.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error generating PDF <pre>' + html + '</pre>')
        return response

    return render(request, 'transactions/report.html', {
        'silver_records': silver_qs,
        'return_records': return_qs,
        'customers': customers,
        'start_date': start,
        'end_date': end,
    })

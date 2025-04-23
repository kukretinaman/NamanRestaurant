from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import OrderInsights

@login_required
def insights_view(request):
    revenue = OrderInsights.total_revenue()
    top_items = OrderInsights.most_ordered_items()
    top_customers = OrderInsights.top_customers()

    return render(request, "system/insights.html", {
        "revenue": revenue,
        "top_items": top_items,
        "top_customers": top_customers,
    })

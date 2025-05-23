from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Ad, ExchangeProposal
from .forms import AdForm
from django.db.models import Q

@login_required
def ad_create(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            return redirect('ad_list')
    else:
        form = AdForm()
    return render(request, 'ads/ad_form.html', {'form': form})

@login_required
def ad_edit(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    if ad.user != request.user:
        return render(request, 'ads/error.html', {'message': 'You are not the author of this ad.'})
    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('ad_list')
    else:
        form = AdForm(instance=ad)
    return render(request, 'ads/ad_form.html', {'form': form})

@login_required
def ad_delete(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    if ad.user != request.user:
        return render(request, 'ads/error.html', {'message': 'You are not the author of this ad.'})
    if request.method == 'POST':
        ad.delete()
        return redirect('ad_list')
    return render(request, 'ads/ad_confirm_delete.html', {'ad': ad})

@login_required
def ad_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    condition = request.GET.get('condition')

    ads = Ad.objects.all()
    if query:
        ads = ads.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category:
        ads = ads.filter(category=category)
    if condition:
        ads = ads.filter(condition=condition)

    paginator = Paginator(ads, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ads/ad_list.html', {
        'page_obj': page_obj,
        'query': query,
        'category': category,
        'condition': condition,
        'category_choices': Ad.CATEGORY_CHOICES  
    })

@login_required
def proposal_create(request, ad_sender_id, ad_receiver_id):
    ad_sender = get_object_or_404(Ad, id=ad_sender_id)
    ad_receiver = get_object_or_404(Ad, id=ad_receiver_id)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        proposal = ExchangeProposal.objects.create(ad_sender=ad_sender, ad_receiver=ad_receiver, comment=comment)
        return redirect('proposal_list')
    return render(request, 'ads/proposal_form.html', {'ad_sender': ad_sender, 'ad_receiver': ad_receiver})

@login_required
def proposal_update(request, proposal_id):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(ExchangeProposal.status.field.choices).keys():
            proposal.status = status
            proposal.save()
        return redirect('proposal_list')
    return render(request, 'ads/proposal_update.html', {'proposal': proposal})

@login_required
def proposal_list(request):
    sender_id = request.GET.get('sender')
    receiver_id = request.GET.get('receiver')
    status = request.GET.get('status')

    proposals = ExchangeProposal.objects.all()
    if sender_id:
        proposals = proposals.filter(ad_sender_id=sender_id)
    if receiver_id:
        proposals = proposals.filter(ad_receiver_id=receiver_id)
    if status:
        proposals = proposals.filter(status=status)

    return render(request, 'ads/proposal_list.html', {'proposals': proposals})
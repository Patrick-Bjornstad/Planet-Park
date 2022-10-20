from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from reviews.forms import ReviewForm
from discovery.models import Park
from reviews.models import Review

# Create your views here.
@login_required(login_url='/')
def review_general(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            form_temp = form.save(commit=False)
            if 'image1' in request.FILES:
                form_temp.image1 = request.FILES['image1']
            if 'image2' in request.FILES:
                form_temp.image2 = request.FILES['image2']
            if 'image3' in request.FILES:
                form_temp.image3 = request.FILES['image3']
            form_temp.author = request.user
            form_temp.save()
            return redirect('reviews_list')
        else:
            return redirect('reviews_list')
    else:
        form = ReviewForm()
        context = {'form': form}
        return render(request, 'reviews/create.html', context)

@login_required(login_url='/')
def review_specific(request, park_code):
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            form_temp = form.save(commit=False)
            if 'image1' in request.FILES:
                form_temp.image1 = request.FILES['image1']
            if 'image2' in request.FILES:
                form_temp.image2 = request.FILES['image2']
            if 'image3' in request.FILES:
                form_temp.image3 = request.FILES['image3']
            form_temp.author = request.user
            form_temp.save()
            return redirect('reviews_list')
        else:
            return redirect('reviews_list')
    else:
        park_obj = Park.objects.filter(code=park_code)[0]
        initial = {'park': park_obj.park_id}
        form = ReviewForm(initial=initial)
        context = {'form': form}
        return render(request, 'reviews/create.html', context)

@login_required(login_url='/')
def reviews_list(request):
    reviews = Review.objects.all()
    url = 'https://res.cloudinary.com/htgpaa4ib/image/upload/v1649747850/'
    context = {'reviews': reviews, 'url': url}
    return render(request, 'reviews/list.html', context)

from django.contrib import messages
from django.db.models import Exists, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User

from .forms import PoliticianForm
from .models import Politician, Position, TermOfOffice

EDITOR_ROLES = (User.Role.EDITOR, User.Role.ADMIN)


@role_required(*EDITOR_ROLES)
def manage_list(request):
    politicians = (
        Politician.objects.select_related('party', 'created_by')
        .prefetch_related('terms__position')
    )
    return render(request, 'politicians/manage_list.html', {'politicians': politicians})


@role_required(*EDITOR_ROLES)
def politician_create(request):
    if request.method == 'POST':
        form = PoliticianForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.created_by = request.user
            politician = form.save()
            messages.success(request, f'{politician.full_name} was added.')
            return redirect('politicians:manage')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = PoliticianForm()
    return render(request, 'politicians/form.html', {'form': form, 'title': 'Add politician'})


@role_required(*EDITOR_ROLES)
def politician_edit(request, pk):
    politician = get_object_or_404(Politician, pk=pk)
    if request.method == 'POST':
        form = PoliticianForm(request.POST, request.FILES, instance=politician)
        if form.is_valid():
            form.save()
            messages.success(request, f'{politician.full_name} was updated.')
            return redirect('politicians:manage')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = PoliticianForm(instance=politician)
    return render(request, 'politicians/form.html', {
        'form': form, 'title': f'Edit {politician.full_name}',
    })


@role_required(*EDITOR_ROLES)
def politician_delete(request, pk):
    politician = get_object_or_404(Politician, pk=pk)
    if request.method == 'POST':
        name = politician.full_name
        if politician.photo:
            politician.photo.delete(save=False)
        politician.delete()
        messages.success(request, f'{name} was deleted.')
        return redirect('politicians:manage')
    return render(request, 'politicians/confirm_delete.html', {'politician': politician})

# ---- Public read-only views (visitors, citizens, editors, admins) ----

def directory(request):
    q = request.GET.get('q', '').strip()
    position_id = request.GET.get('position', '')

    latest_rank = (
        TermOfOffice.objects.filter(politician=OuterRef('pk'))
        .order_by('-start_year')
        .values('position__rank')[:1]
    )
    politicians = (
        Politician.objects.select_related('party')
        .prefetch_related('terms__position')
        .annotate(rank=Subquery(latest_rank))
        .order_by('rank', 'last_name', 'first_name')
    )

    # Search: every word must match a name or party
    for word in q.split():
        politicians = politicians.filter(
            Q(first_name__icontains=word) | Q(last_name__icontains=word)
            | Q(party__name__icontains=word) | Q(party__abbreviation__icontains=word)
        )

    # Filter by office level
    if position_id.isdigit():
        politicians = politicians.filter(
            Exists(TermOfOffice.objects.filter(
                politician=OuterRef('pk'), position_id=int(position_id),
            ))
        )

    return render(request, 'politicians/directory.html', {
        'politicians': politicians,
        'positions': Position.objects.all(),
        'q': q,
        'selected_position': position_id,
    })


def detail(request, pk):
    politician = get_object_or_404(
        Politician.objects.select_related('party', 'created_by').prefetch_related('terms__position'),
        pk=pk,
    )
    return render(request, 'politicians/detail.html', {'politician': politician})
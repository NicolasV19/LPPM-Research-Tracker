from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from contacts.forms import ContactForm
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Contact, Proposal
from .forms import ContactForm, ProposalForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse
import json
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required

# Create your views here.
#@login_required
#def index(request):
#    contacts = request.user.contacts.all().order_by('-created_at')
#    context = {
#        'contacts': contacts,
#        'form': ContactForm()
#        }
#    return render(request, 'contacts.html', context)

@login_required
def index(request):
    user = request.user

    # Check if user is admin/superuser
    if user.is_superuser or user.groups.filter(name='Pengusul').exists():
        # Show all proposals to admin
        proposals = Proposal.objects.all()
    else:
        # --- THIS IS THE CORRECTED LOGIC ---
        # Show proposals ONLY if the user created it OR is an assigned reviewer.
        proposals = Proposal.objects.filter(
            Q(reviewer_1=user) |
            Q(reviewer_2=user)
        ).distinct() # Use .distinct() to avoid duplicates

    # Order by creation date (newest first)
    proposals = proposals.order_by('-created_at')

    context = {
        'proposals': proposals,
        'form': ProposalForm(),
        'is_reviewer': user.groups.filter(name='Reviewer').exists(),
        'is_admin': user.is_superuser
    }
    return render(request, 'proposals/proposal_list.html', context)


@login_required
def search_contacts(request):
    query = request.GET.get('search', '')

    contacts =  request.user.contacts.filter(
        Q(name__icontains=query) | Q(email__icontains=query)
    )
    return render(request, 'partials/contact_list.html', {'contacts': contacts})

@login_required
@require_http_methods(['POST'])
def create_contact(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        contact = form.save(commit=False)
        contact.user = request.user
        contact.save()

        context = {'contact': contact}
        response = render(request, 'partials/contact-row.html', context)
        response['HX-Trigger'] = 'success'
        return response

@login_required
def logout_view(request):
    logout(request)
    return redirect('login') # Redirect to your login page or homepage after logout

@login_required
def edit_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
#    context = {}
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            # Return updated row so HTMX swaps it in
            return render(request, "contact-row.html", {"contact": contact})
    else:
        form = ContactForm(instance=contact)

    return render(request, "partials/edit-contact-modal.html", {"form": form, "contact": contact})

@login_required
def delete_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == "POST":
        contact.delete()
        return HttpResponse(status=204)

    return render(request, "partials/delete-conf-modal.html", {"contact": contact})

class CustomLoginView(LoginView):
    template_name = "contacts/login.html"

    def dispatch(self, request, *args, **kwargs):
        # If already logged in, don’t show login again
        if request.user.is_authenticated:
#            if request.user.is_staff:
#                return redirect(reverse('admin:index'))
                return redirect('/')
        return super().dispatch(request, *args, **kwargs)

#    def get_success_url(self):
#        user = self.request.user
#        if user.is_staff:
#            return reverse('admin:index')  # staff → admin
#        return '/'  # normal users → your site

# bwt LPPM
#def get_proposals_for_user(user):
    #"""Return the appropriate queryset based on user role"""
#    if user.is_superuser or user.groups.filter(name='Reviewer').exists():
#        return Proposal.objects.all()
#    else:
#        return Proposal.objects.filter(created_by=user)


@login_required
def proposal_list(request):
    user = request.user

    # --- THIS IS THE NEW CORE LOGIC ---
    # Superusers see everything
    if user.is_superuser or user.is_pengusul():
        proposals = Proposal.objects.all()
    else:
        # Others see proposals they created OR are assigned to review.
        # The Q object is used for OR conditions in a database query.
        proposals = Proposal.objects.filter( 
            Q(reviewer_1=user) | 
            Q(reviewer_2=user)
        ).distinct() # .distinct() prevents duplicates if a user is both proposer and reviewer

    # Your existing search and filter logic can remain the same
    query = request.GET.get('q', '')
    if query:
        proposals = proposals.filter(
            Q(name__icontains=query) |
            Q(leader__icontains=query) |
            Q(members__icontains=query)
        )
    # ... (add your other filters for status, type, etc. here)

    proposals = proposals.order_by('-created_at')

    context = {
        'proposals': proposals,
        'is_reviewer': user.groups.filter(name='Reviewer').exists(),
        'is_pengusul': user.groups.filter(name='Pengusul').exists(),
        'is_admin': user.is_superuser
    }
    return render(request, 'proposals/proposal_list.html', context)

@login_required
def proposal_create(request):
    if request.method == 'POST':
        form = ProposalForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.created_by = request.user
            proposal.save()
            return redirect('proposal_list')
    else:
        form = ProposalForm(user=request.user)

    return render(request, 'proposals/proposal_form.html', {
        'form': form,
        'title': 'Submit New Proposal'
    })

@login_required
def proposal_update(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    user = request.user

    # --- NEW PERMISSION CHECK ---
    # Allow if user is the creator, an assigned reviewer, or an admin.
    is_assigned_reviewer = (user == proposal.reviewer_1 or user == proposal.reviewer_2)
    if not (proposal.created_by == user or is_assigned_reviewer or user.is_superuser):
        return HttpResponseForbidden("You don't have permission to edit this proposal.")

    if request.method == 'POST':
        form = ProposalForm(request.POST, request.FILES, instance=proposal, user=user)
        if form.is_valid():
            form.save()
            return redirect('proposal_list')
    else:
        form = ProposalForm(instance=proposal, user=user)

    return render(request, 'proposals/proposal_form.html', {
        'form': form,
        'title': 'Edit Project',
        'proposal': proposal
    })

@login_required
def proposal_delete(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    user = request.user
    
    # --- NEW PERMISSION CHECK ---
    # Only the creator or an admin should be able to delete.
    if not (proposal.created_by == user or user.is_superuser):
        return HttpResponseForbidden("You don't have permission to delete this proposal.")

    if request.method == 'POST':
        proposal.delete()
        return redirect('proposal_list')

    return render(request, 'proposals/proposal_confirm_delete.html', {'proposal': proposal})


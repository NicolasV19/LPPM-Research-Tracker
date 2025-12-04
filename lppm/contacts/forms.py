from django import forms
from .models import Contact, Proposal
#from .views import is_reviewer


class ContactForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full text-white',
            'placeholder': 'Contact Name'
        })

    
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full text-white',
            'placeholder': 'Contact Name'
        })
    )

    class Meta:
        model= Contact
        fields= (
            'name', 'email'
        )
    

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['name', 'leader', 'members', 'type', 'file', 'catatan', 'catatan_2', 'status', 'reviewer_1', 'reviewer_2']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama Pengusul'
            }),
            'leader': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ketua Kelompok Pengusul'
            }),
            'members': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Anggota Kelompok Pengusul',
                'rows': 3
            }),
            'type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'catatan': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Catatan (opsional)',
                'rows': 3
            }),
            'catatan_2': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Catatan (opsional)',
                'rows': 3
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reviewer_1': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reviewer_2': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            is_reviewer_user = self.user.groups.filter(name='Reviewer').exists()

        # If user is not a reviewer, remove status and notes fields
            if not is_reviewer_user:
                self.fields.pop('status', None)
                self.fields['catatan'].widget.attrs['readonly'] = True
                self.fields['catatan'].widget.attrs['class'] = 'form-control bg-light'

                self.fields['catatan_2'].widget.attrs['readonly'] = True
                self.fields['catatan_2'].widget.attrs['class'] = 'form-control bg-light'
            
            if not self.user.is_superuser:
                self.fields.pop('reviewer_1', None)
                self.fields.pop('reviewer_2', None)

            # --- THIS IS THE CORRECTED LOGIC FOR READ-ONLY FIELDS ---
            # This logic only affects the appearance (UI)
            # It only runs for reviewers on existing proposals
            if is_reviewer_user and self.instance and self.instance.pk:
                # Check if this user is assigned as reviewer 1 or 2 on this proposal
                is_this_reviewer_1 = (self.instance.reviewer_1 == self.user)
                is_this_reviewer_2 = (self.instance.reviewer_2 == self.user)
                
                if is_this_reviewer_1:
                    # Reviewer 1 can only edit 'catatan', so 'catatan_2' is read-only
                    self.fields['catatan_2'].widget.attrs['readonly'] = True
                    self.fields['catatan_2'].widget.attrs['class'] = 'form-control bg-light' # Style it to look disabled
                    self.fields['catatan_2'].help_text = "Hanya Reviewer 2 yang dapat mengedit ini."
                
                elif is_this_reviewer_2:
                    # Reviewer 2 can only edit 'catatan_2', so 'catatan' is read-only
                    self.fields['catatan'].widget.attrs['readonly'] = True
                    self.fields['catatan'].widget.attrs['class'] = 'form-control bg-light' # Style it to look disabled
                    self.fields['catatan'].help_text = "Hanya Reviewer 1 yang dapat mengedit ini."
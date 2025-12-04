from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator

class User(AbstractUser):
    def save(self, *args, **kwargs):
          self.set_password(self.password)
          super().save(*args, **kwargs)


class Proposal(models.Model):
    PROPOSAL_TYPES = (
        ('penelitian', 'Penelitian'),
        ('PKM', 'PKM'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('revision', 'Revision')
    )

    name = models.CharField(max_length=50)
    leader = models.CharField(max_length=50)
    members = models.TextField(max_length=200)
    type = models.CharField(max_length=25, choices=PROPOSAL_TYPES)
    file = models.FileField(upload_to='projects/', blank=True, null=True, validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])])
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    catatan = models.TextField(max_length=200, blank=True, null=True)
    catatan_2 = models.TextField(max_length=200, blank=True, null=True)
    reviewer_1 = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='reviewer_1_proposals', limit_choices_to={'groups__name': 'Reviewer'})
    reviewer_2 = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='reviewer_2_proposals', limit_choices_to={'groups__name': 'Reviewer'})
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    #user = models.ForeignKey(
    #   User,
    #    on_delete=models.CASCADE,
    #    related_name='contacts'  #user.contacts.all()
    #)
#    document = models.FileField(
#        upload_to='contact_docs/'
#        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'txt'])]
#        blank=True
#        null=True
#    )

#class Proposal(models.Model):
 #   name = models.ForeignKey(
  #      User,
   #    editable=False
    #)
    #ketua = models.CharField(max_length=50)
    #anggota1 = models.CharField(max_length=50)
    #anggota2 = models.CharField(max_length=50)
    #anggota3 = models.CharField(max_length=50)

#class Meta:
#    unique_together = ('user', 'email')

def __str__(self):
    return f"{self.name} <{self.email}>"
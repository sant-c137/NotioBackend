# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.conf import settings
from django.utils.timezone import now

class Note(models.Model):
    note_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    creation_date = models.DateTimeField()
    last_modification = models.DateTimeField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tags = models.ManyToManyField("Tag", through="NoteTag")
    class Meta:
        managed = True
        db_table = "Note"

class SharedNotes(models.Model):
    shared_note_id = models.AutoField(primary_key=True)
    note = models.ForeignKey(Note, models.CASCADE)
    shared_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sharing_date = models.DateTimeField()
    permission = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "Shared_notes"
class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = True
        db_table = "Tag"

class NoteTag(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)  
    tag = models.ForeignKey("Tag", on_delete=models.CASCADE)  

    class Meta:
        managed = True
        db_table = "Note_Tag"
        unique_together = (("note", "tag"),)






from django.db import models
import os

class FileInfo(models.Model):
    user_id = models.IntegerField()  # Placeholder for foreign key, currently using integer
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    classification = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure the directory exists
        user_folder = os.path.join('user_files', f'user_{self.user_id}')
        os.makedirs(user_folder, exist_ok=True)
        self.file_path = os.path.join(user_folder, self.file_name)
        super().save(*args, **kwargs)


class ClassificationOption(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('user_id', 'name')

    def __str__(self):
        return f"{self.name} (user {self.user_id})"
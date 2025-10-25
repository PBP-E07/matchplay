from django.db import models
import uuid

# Create your models here.
class Blog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    summary = models.TextField()
    content = models.TextField()
    thumbnail = models.URLField(blank=True, null=True)
    author = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    blog_views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    
    def increment_views(self):
        self.blog_views += 1
        self.save()

    class Meta:
        # Urutkan berdasarkan tanggal terbaru
        ordering = ['-created_at']

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:blog-detail', kwargs={'pk': self.pk})


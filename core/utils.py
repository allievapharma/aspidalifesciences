from django.utils.text import slugify

def generate_unique_slug(instance, field_value, slug_field_name="slug"):
    """
    Generate a unique slug for a model instance.
    """
    base_slug = slugify(field_value)
    slug = base_slug
    counter = 1

    ModelClass = instance.__class__
    while ModelClass.objects.filter(**{slug_field_name: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug

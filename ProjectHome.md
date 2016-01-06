# Overview #

Django's field that stores labels in more than one language in database.

Just working on newforms-admin branch.

# Installing and using #

**Installation**
Download, unpack and copy files to ${PYTHON\_PATH}/site-packages/transdb (or anywhere else if you know what you're doing)

**Create your models:**
```
from transdb import TransCharField, TransTextField
[...]

class MyModel(models.Model):
  [...]
  my_char_field = TransCharField(max_length=32)
  my_text_field = TransTextField()
```

**If you need to use in models in a more advanced way:**
```
from transdb import TransDbField
from django.conf import settings
from django.utils.translation import get_language
from django.template.defaultfilters import slugify
[...]

class MyModel(models.Model):
  [...]
  my_char_field = TransCharField(max_length=32)
  my_text_field = TransTextField()
  slug_field = models.SlugField(editable=False)

  def __unicode__(self):
    return self.my_char_field

  def save(self):
    self.slug_field = slugify(self.my_char_field.get_in_language(settings.LANGUAGE_CODE))
    super(MyModel, self).save()
[...]
```

**Use as any other field in templates:**
```
[...]
<p>{{ object.my_field }}</p>
[...]
```

**And that's all, enjoy!**

# Serialization #

Due to technical reasons, serialization on models with TransDb fields has some specific restrictions.

Django comes with two serialization formats, xml and json.

TransDb requires two diferent methods when serializing, one that serializes information for all languages (for example for saving data as fixture). Other method should just return the current language (serialization for ajax processing).

Probably will change in the future, but now TransDb applies a method depending on the format, so
  * Use xml format for including all languages in serialization objects (and use TransDb serializer, see below).
  * User json format for returning just the current language in serialization objects.

For using TransDb serializer add next lines to your settings.py file:
```
SERIALIZATION_MODULES = {
    'xml': 'transdb.xml_serializer',
}
```

# Migration from non-translatable fields (and previous versions of TransDb) #

There is a wiki page MigrationProcedure that covers this subject.

# Techincal information #

**Internally** data is stored in database as a string in dictionary format, for example:
```
u'{u'en': u'This is english', u'ca': u'Això és català'}'
```
Field uses a subclass of unicode class, adding a raw\_data attribute to store the string with all languages, and implementing the get\_in\_language(language) method to allow access to a diferent language (diferent from the user's current language).

# Known issues #

  * See the list in http://code.google.com/p/transdb/issues/list
# Introduction #

Migration from a non-translatable field to a translatable one using transdb is a very easy procedure. Most of the work is done automatically when changing a CharField or a TextField to a TransCharField or a TextCharField.

# TransTextField #

TextField doesn't specify a length at SQL structure, so nothing has to be changed at database.

Changes in you model should be something like:

```
from django.db import models
[...]

class MyModel(models.Model):
  [...]
  my_text_field = models.TextField()
```

to

```
from django.db import models
from django-transdb import TransTextField
[...]

class MyModel(models.Model):
  [...]
  my_text_field = TransTextField()
```

Application will be working after this change, and you'll be able to translate field contents at the admin page. TransDb can work with TextField contents at database, using them as the primary language text (set by LANGUAGE\_CODE at settings.py).

# TransCharField #

As TextField you've to change your model, like:

```
from django.db import models
[...]

class MyModel(models.Model):
  [...]
  my_text_field = models.CharField(max_length=32)
```

to

```
from django.db import models
from django-transdb import TransCharField
[...]

class MyModel(models.Model):
  [...]
  my_text_field = TransCharField(max_length=32)
```

As well as changing models, it's necessary to change database structure. CharField has the max length specified at database, so you've to increase this length to fit all languages strings.

To know the estimated size required by your field, you can do something like:

```
$ python manage.py sqlall [YOUR_APPLICATION]
BEGIN;
CREATE TABLE `www_mymodel` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `my_text_field` varchar(154) NOT NULL,
)
;
COMMIT;
```

Where 154 it the recommended size, so you can execute:

```
ALTER TABLE `www_my_model` MODIFY COLUMN `my_text_field` varchar(154) NOT NULL;
```

or something like that depending on your database type.

# Migration from a previous version of TransDb #

When migratting from a previous version of TransDb you've to change some code.

At templates remove all occurrences of transdb filter, not required anymore:

```
<% load transdb %>
[...]
<p>{{ object.my_field|transdb }}</p>
[...]
```

to

```
[...]
<p>{{ object.my_field }}</p>
[...]
```

Then, at models (or views, or at any place you could have it), you've to change:

```
self.my_text_field[get_language()]
```

by

```
self.my_text_field
```

and

```
self.my_text_field[settings.LAGUAGE_CODE]
```

by

```
self.my_text_field.get_in_language(settings.LAGUAGE_CODE)
```
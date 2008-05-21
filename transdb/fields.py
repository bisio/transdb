from django.db import models
from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.core import validators
from django import forms as oldforms

def get_default_language_name():
    '''
    Get language from default language specified by LANGUAGE_CODE in settings
    Used in error messages
    '''
    lang_name = ''
    for lang in settings.LANGUAGES:
        if lang[0] == settings.LANGUAGE_CODE:
            lang_name = lang[1]
            break
    return force_unicode(lang_name)

class TransDbValue(unicode):
    '''
    This class implements a unicode string, but with a hidden attribute raw_data.
    When used as a string it returns the translation of the current language
    raw_data attribute stores a dictionary with all translations
    Also implements a method "get_in_language(language)" that returns the translation on any available language
    '''
    raw_data = {}

    def get_in_language(self, language):
        if self.raw_data and self.raw_data.has_key(language):
            return self.raw_data[language]
        else:
            return ''

class TransCharFormField(oldforms.TextField):
    '''
    '''
    def prepare(self, new_data):
        value = {}
        for lang_code, lang_name in settings.LANGUAGES:
            value[lang_code] = new_data['%s_%s' % (self.field_name, lang_code)]
        new_data[self.field_name] = value
        super(TransCharFormField, self).prepare(new_data)

    def get_input(self, name, value, lang, attrs, id=None):
        value_html = (value and ' value="%s"' % value) or ''
        id_html = (id and ' id="id_%s"' % name) or ''
        return '<input type="text" name="%s_%s"%s%s/>' % (name, lang, value_html, id_html)
        
    def render(self, value):
        if value and hasattr(value, 'raw_data'):
            value_dict = value.raw_data
        else:
            value_dict = {}
        output = []
        name = self.field_name
        for lang_code, lang_name in settings.LANGUAGES:
            value_for_lang = ''
            if value_dict.has_key(lang_code):
                value_for_lang = value_dict[lang_code]
            if lang_code == settings.LANGUAGE_CODE:
                input = self.get_input(name, value_for_lang, lang_code, "", True)
            else:
                input = self.get_input(name, value_for_lang, lang_code, "")
            output.append('<li style="list-style-type: none; float: left; margin-right: 1em;"><span style="display: block;">%s:</span>%s</li>' % (force_unicode(lang_name), input))
        return u'<ul>%s</ul>' % (u''.join(output))

    def isValidLength(self, data, form):
        print dir(self)
        if self.is_required and not data[settings.LANGUAGE_CODE]:
            raise validators.ValidationError, _("This field cannot be null for default language '%s'." % get_default_language_name())

class TransTextFormField(TransCharFormField):
    def get_input(self, name, value, lang, attrs, id=None):
        id_html = (id and ' id="id_%s"' % name) or ''
        return '<textarea rows="10" cols="40" type="text" name="%s_%s"%s>%s</textarea>' % (name, lang, id_html, value)

class TransField(models.Field):
    '''
    Model field to be subclassed
    Used for storing a string in many languages at database (with python's dictionary format)
    pickle module could be used, but wouldn't alow search on fields?
    '''

    def get_internal_type(self):
        return 'TextField'

    def to_python(self, value):
        if isinstance(value, dict): # formfield method makes this function be called with value as a dict
            python_value = value
        else:
            try:
                python_value = eval(value)
            except Exception:
                python_value = None
        if isinstance(python_value, dict) and (python_value.has_key(get_language()) or python_value.has_key(settings.LANGUAGE_CODE)):
            if python_value.has_key(get_language()):
                result = TransDbValue(python_value[get_language()])
            elif python_value.has_key(settings.LANGUAGE_CODE):
                result = TransDbValue(python_value[settings.LANGUAGE_CODE])
            result.raw_data = python_value
        else:
            result = TransDbValue(value)
            result.raw_data = {settings.LANGUAGE_CODE: value}
        return result
    
    def get_db_prep_save(self, value):
        return unicode(value.raw_data)

class TransCharField(TransField):
    __metaclass__ = models.SubfieldBase

    def get_manipulator_field_objs(self):
            return [TransCharFormField] 

class TransTextField(TransField):
    __metaclass__ = models.SubfieldBase

    def get_manipulator_field_objs(self):
            return [TransTextFormField] 


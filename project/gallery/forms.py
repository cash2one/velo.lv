from django import forms
from django_select2 import AutoHeavySelect2MultipleWidget
from django_select2.util import JSFunctionInContext
from gallery.select2_fields import PhotoNumberChoices
from velo.mixins.forms import RequestKwargModelFormMixin


class AssignNumberForm(RequestKwargModelFormMixin, forms.Form):

    numbers = PhotoNumberChoices(required=False, widget=AutoHeavySelect2MultipleWidget(select2_options={
        'ajax': {
            'dataType': 'json',
            'quietMillis': 100,
            'data': JSFunctionInContext('get_number_params'),
            'results': JSFunctionInContext('django_select2.process_results'),
        },
        "minimumResultsForSearch": 0,
        "minimumInputLength": 0,
        "closeOnSelect": True
    }))

    def __init__(self, *args, **kwargs):
        super(AssignNumberForm, self).__init__(*args, **kwargs)

        self.fields['numbers'].choices = ((1,1), (2,2))
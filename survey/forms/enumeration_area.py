from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, Form
from django.conf import settings
from survey.models import EnumerationArea, Location, LocationType

class EnumerationAreaForm(ModelForm):
    
    def __init__(self, locations=None, *args, **kwargs):
        super(EnumerationAreaForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['name', 'total_households']
        locations = locations or LocationsFilterForm().get_locations()
#         import pdb; pdb.set_trace()
        self.fields['locations'].queryset = locations
        self.fields.keyOrder.append('locations')

    class Meta:
        model = EnumerationArea
        widgets = {
            'name': forms.TextInput(attrs={"id": 'ea_name', "class": 'enumeration_area'}),
            'total_households' : forms.TextInput({'id' : 'total_households',  "class": 'enumeration_area'}),
            'locations': forms.SelectMultiple(attrs={'class': 'multi-select enumeration_area', 'id': 'ea-locations'})
        }

class LocationsFilterForm(Form):
    '''
        1. Used to filter out locations under a given main location (eg states under a country)
        2. Also to filter out locations under given ea if defined
    '''
    
    def __init__(self, *args, **kwargs):
        include_ea = kwargs.pop('include_ea', False)
        super(LocationsFilterForm, self).__init__(*args, **kwargs)
        for location_type in LocationType.objects.all():
            if location_type.parent is not None and location_type.is_leaf_node() == False:
                choices = [(loc.pk, loc.name) for loc in Location.objects.filter(type=location_type)]
                choices.insert(0, ('', '--------------------------------'))
                self.fields[location_type.name] = forms.ChoiceField(choices=choices)
                self.fields[location_type.name].required = False
                self.fields[location_type.name].widget.attrs['class'] = 'location_filter ea_filter chzn-select'
        if include_ea:
            choices = [(ea.pk, ea.name) for ea in EnumerationArea.objects.all()]
            choices.insert(0, ('', '--------------------------------'))
            self.fields['enumeration_area'] = forms.ChoiceField(choices=choices)
            self.fields['enumeration_area'].widget.attrs['class'] = 'location_filter chzn-select'
            self.fields['enumeration_area'].required = False
    
    def get_locations(self):
        loc = None
        ea = None
        if self.is_valid():
            for key in self.fields.keys():
                if key is not 'enumeration_area':
                    val = self.cleaned_data[key]
                    if val: 
                        loc = val
                if key is 'enumeration_area':
                    ea = self.cleaned_data[key]
        return get_leaf_locs(loc, ea)

    def get_enumerations(self):
        return EnumerationArea.objects.filter(locations__in=self.get_locations()).distinct()
    
def get_leaf_locs(loc_id=None, ea=None):
    if loc_id is None:
        location = Location.objects.get(parent=None)
    else:
        location = Location.objects.get(pk=loc_id)
    locations = location.get_leafnodes(True)
    if ea:
        locations = locations.filter(enumeration_areas__pk__in=ea)
    return locations.distinct()

# 
#     def save(self, commit=True, **kwargs):
#         batch = super(EnumerationAreaForm, self).save(commit=commit)
#         bc = BatchChannel.objects.filter(batch=batch)
#         bc.delete()
#         for val in kwargs['access_channels']:
#            BatchChannel.objects.create(batch=batch, channel=val)
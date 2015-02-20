from survey.models import Investigator


class ExportInvestigatorsService:

    def __init__(self, export_fields):
        self.investigators = Investigator.objects.all()
        self.HEADERS = export_fields

    def formatted_responses(self):
        _formatted_responses = [','.join([entry.upper() for entry in self.HEADERS])]
        for investigator in self.investigators:
            _formatted_responses.append(','.join(["%s"%str(investigator.__dict__.get(entry, '')) for entry in self.HEADERS]))
        return _formatted_responses

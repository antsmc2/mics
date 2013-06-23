# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'HouseHold.name'
        db.delete_column(u'survey_household', 'name')

        # Adding field 'HouseHold.head'
        db.add_column(u'survey_household', 'head',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.HouseholdHead'], null=True),
                      keep_default=False)

        # Adding field 'HouseHold.number_of_males'
        db.add_column(u'survey_household', 'number_of_males',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'HouseHold.number_of_females'
        db.add_column(u'survey_household', 'number_of_females',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'HouseHold.children_5_12_years'
        db.add_column(u'survey_household', 'children_5_12_years',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'HouseHold.children_13_17_years'
        db.add_column(u'survey_household', 'children_13_17_years',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'HouseHold.children_0_5_months'
        db.add_column(u'survey_household', 'children_0_5_months',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'HouseHold.children_6_11_months'
        db.add_column(u'survey_household', 'children_6_11_months',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'HouseHold.children_12_23_months'
        db.add_column(u'survey_household', 'children_12_23_months',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'HouseHold.children_24_59_months'
        db.add_column(u'survey_household', 'children_24_59_months',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'HouseHold.women_15_19_years'
        db.add_column(u'survey_household', 'women_15_19_years',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'HouseHold.children_20_49_years'
        db.add_column(u'survey_household', 'children_20_49_years',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'HouseHold.name'
        db.add_column(u'survey_household', 'name',
                      self.gf('django.db.models.fields.CharField')(default='dummy', max_length=100),
                      keep_default=False)

        # Deleting field 'HouseHold.head'
        db.delete_column(u'survey_household', 'head_id')

        # Deleting field 'HouseHold.number_of_males'
        db.delete_column(u'survey_household', 'number_of_males')

        # Deleting field 'HouseHold.number_of_females'
        db.delete_column(u'survey_household', 'number_of_females')

        # Deleting field 'HouseHold.children_5_12_years'
        db.delete_column(u'survey_household', 'children_5_12_years')

        # Deleting field 'HouseHold.children_13_17_years'
        db.delete_column(u'survey_household', 'children_13_17_years')

        # Deleting field 'HouseHold.children_0_5_months'
        db.delete_column(u'survey_household', 'children_0_5_months')

        # Deleting field 'HouseHold.children_6_11_months'
        db.delete_column(u'survey_household', 'children_6_11_months')

        # Deleting field 'HouseHold.children_12_23_months'
        db.delete_column(u'survey_household', 'children_12_23_months')

        # Deleting field 'HouseHold.children_24_59_months'
        db.delete_column(u'survey_household', 'children_24_59_months')

        # Deleting field 'HouseHold.women_15_19_years'
        db.delete_column(u'survey_household', 'women_15_19_years')

        # Deleting field 'HouseHold.children_20_49_years'
        db.delete_column(u'survey_household', 'children_20_49_years')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'locations.location': {
            'Meta': {'object_name': 'Location'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'point': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locations.Point']", 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['locations.Location']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'locations'", 'null': 'True', 'to': u"orm['locations.LocationType']"})
        },
        u'locations.locationtype': {
            'Meta': {'object_name': 'LocationType'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'primary_key': 'True'})
        },
        u'locations.point': {
            'Meta': {'object_name': 'Point'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '13', 'decimal_places': '10'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '13', 'decimal_places': '10'})
        },
        'survey.answerrule': {
            'Meta': {'object_name': 'AnswerRule'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'next_question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parent_question_rules'", 'null': 'True', 'to': "orm['survey.Question']"}),
            'question': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'rule'", 'unique': 'True', 'null': 'True', 'to': "orm['survey.Question']"}),
            'validate_with_option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.QuestionOption']", 'null': 'True'}),
            'validate_with_question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True'}),
            'validate_with_value': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2', 'null': 'True'})
        },
        'survey.batch': {
            'Meta': {'object_name': 'Batch'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'batches'", 'null': 'True', 'to': "orm['survey.Survey']"})
        },
        'survey.household': {
            'Meta': {'object_name': 'HouseHold'},
            'children_0_5_months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'children_12_23_months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'children_13_17_years': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'children_20_49_years': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'children_24_59_months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'children_5_12_years': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'children_6_11_months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'head': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.HouseholdHead']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'households'", 'null': 'True', 'to': "orm['survey.Investigator']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'number_of_females': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_males': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'women_15_19_years': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'survey.householdhead': {
            'Meta': {'object_name': 'HouseholdHead'},
            'age': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level_of_education': ('django.db.models.fields.CharField', [], {'default': "'Primary'", 'max_length': '100', 'null': 'True'}),
            'male': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Household'", 'max_length': '100'}),
            'occupation': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'resident_since': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'survey.indicator': {
            'Meta': {'object_name': 'Indicator'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'indicators'", 'null': 'True', 'to': "orm['survey.Batch']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2', 'null': 'True'})
        },
        'survey.investigator': {
            'Meta': {'object_name': 'Investigator'},
            'age': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'English'", 'max_length': '100', 'null': 'True'}),
            'level_of_education': ('django.db.models.fields.CharField', [], {'default': "'Primary'", 'max_length': '100', 'null': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locations.Location']", 'null': 'True'}),
            'male': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'mobile_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'survey.locationautocomplete': {
            'Meta': {'object_name': 'LocationAutoComplete'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locations.Location']", 'null': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'survey.multichoiceanswer': {
            'Meta': {'object_name': 'MultiChoiceAnswer'},
            'answer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.QuestionOption']", 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'household': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.HouseHold']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Investigator']", 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True'})
        },
        'survey.numericalanswer': {
            'Meta': {'object_name': 'NumericalAnswer'},
            'answer': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '5', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'household': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.HouseHold']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Investigator']", 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True'})
        },
        'survey.question': {
            'Meta': {'object_name': 'Question'},
            'answer_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'null': 'True', 'to': "orm['survey.Indicator']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2', 'null': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['survey.Question']"}),
            'subquestion': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'survey.questionoption': {
            'Meta': {'object_name': 'QuestionOption'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2', 'null': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'options'", 'null': 'True', 'to': "orm['survey.Question']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'survey.survey': {
            'Meta': {'object_name': 'Survey'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'survey.textanswer': {
            'Meta': {'object_name': 'TextAnswer'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'household': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.HouseHold']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Investigator']", 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True'})
        }
    }

    complete_apps = ['survey']
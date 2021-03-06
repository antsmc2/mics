# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'TextAnswer.answer'
        db.alter_column(u'survey_textanswer', 'answer', self.gf('django.db.models.fields.CharField')(max_length=150))

        # Changing field 'QuestionOption.text'
        db.alter_column(u'survey_questionoption', 'text', self.gf('django.db.models.fields.CharField')(max_length=150))

        # Changing field 'AnswerRule.action'
        db.alter_column(u'survey_answerrule', 'action', self.gf('django.db.models.fields.CharField')(max_length=150))

        # Changing field 'AnswerRule.condition'
        db.alter_column(u'survey_answerrule', 'condition', self.gf('django.db.models.fields.CharField')(max_length=150))

    def backwards(self, orm):

        # Changing field 'TextAnswer.answer'
        db.alter_column(u'survey_textanswer', 'answer', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'QuestionOption.text'
        db.alter_column(u'survey_questionoption', 'text', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'AnswerRule.action'
        db.alter_column(u'survey_answerrule', 'action', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'AnswerRule.condition'
        db.alter_column(u'survey_answerrule', 'condition', self.gf('django.db.models.fields.CharField')(max_length=100))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
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
            'action': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'next_question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parent_question_rules'", 'null': 'True', 'to': "orm['survey.Question']"}),
            'question': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'rule'", 'unique': 'True', 'null': 'True', 'to': "orm['survey.Question']"}),
            'validate_with_option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.QuestionOption']", 'null': 'True'}),
            'validate_with_question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True'}),
            'validate_with_value': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2', 'null': 'True'})
        },
        'survey.backend': {
            'Meta': {'object_name': 'Backend'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'survey.batch': {
            'Meta': {'object_name': 'Batch'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2', 'null': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'batches'", 'null': 'True', 'to': "orm['survey.Survey']"})
        },
        'survey.batchlocationstatus': {
            'Meta': {'object_name': 'BatchLocationStatus'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'open_locations'", 'null': 'True', 'to': "orm['survey.Batch']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'open_batches'", 'null': 'True', 'to': u"orm['locations.Location']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        'survey.children': {
            'Meta': {'object_name': 'Children'},
            'aged_between_0_5_months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'aged_between_12_23_months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'aged_between_13_17_years': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'aged_between_24_59_months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'aged_between_5_12_years': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'aged_between_6_11_months': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'household': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'children'", 'unique': 'True', 'null': 'True', 'to': "orm['survey.Household']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        'survey.formula': {
            'Meta': {'object_name': 'Formula'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'denominator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'as_denominator'", 'to': "orm['survey.Question']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'numerator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'as_numerator'", 'to': "orm['survey.Question']"})
        },
        'survey.household': {
            'Meta': {'object_name': 'Household'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'households'", 'null': 'True', 'to': "orm['survey.Investigator']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'number_of_females': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'number_of_males': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'survey.householdbatchcompletion': {
            'Meta': {'object_name': 'HouseholdBatchCompletion'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'completed_households'", 'null': 'True', 'to': "orm['survey.Batch']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'household': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'completed_batches'", 'null': 'True', 'to': "orm['survey.Household']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'completed_batches'", 'null': 'True', 'to': "orm['survey.Investigator']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        'survey.householdhead': {
            'Meta': {'object_name': 'HouseholdHead'},
            'age': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True'}),
            'household': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'head'", 'unique': 'True', 'null': 'True', 'to': "orm['survey.Household']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level_of_education': ('django.db.models.fields.CharField', [], {'default': "'Primary'", 'max_length': '100', 'null': 'True'}),
            'male': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'occupation': ('django.db.models.fields.CharField', [], {'default': "'16'", 'max_length': '100'}),
            'resident_since_month': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5'}),
            'resident_since_year': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1984'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True'})
        },
        'survey.indicator': {
            'Meta': {'object_name': 'Indicator'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'indicators'", 'null': 'True', 'to': "orm['survey.Batch']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2', 'null': 'True'})
        },
        'survey.investigator': {
            'Meta': {'object_name': 'Investigator'},
            'age': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Backend']", 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'English'", 'max_length': '100', 'null': 'True'}),
            'level_of_education': ('django.db.models.fields.CharField', [], {'default': "'Primary'", 'max_length': '100', 'null': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locations.Location']", 'null': 'True'}),
            'male': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'mobile_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'weights': ('django.db.models.fields.FloatField', [], {'default': '0'})
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
            'household': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Household']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Investigator']", 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True'}),
            'rule_applied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.AnswerRule']", 'null': 'True'})
        },
        'survey.numericalanswer': {
            'Meta': {'object_name': 'NumericalAnswer'},
            'answer': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '5', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'household': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Household']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Investigator']", 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True'}),
            'rule_applied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.AnswerRule']", 'null': 'True'})
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
            'text': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'survey.questionoption': {
            'Meta': {'object_name': 'QuestionOption'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2', 'null': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'options'", 'null': 'True', 'to': "orm['survey.Question']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'survey.randomhouseholdselection': {
            'Meta': {'object_name': 'RandomHouseHoldSelection'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'no_of_households': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'selected_households': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'household': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Household']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Investigator']", 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True'}),
            'rule_applied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.AnswerRule']", 'null': 'True'})
        },
        'survey.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'userprofile'", 'unique': 'True', 'to': u"orm['auth.User']"})
        },
        'survey.women': {
            'Meta': {'object_name': 'Women'},
            'aged_between_15_19_years': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'aged_between_20_49_years': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'household': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'women'", 'unique': 'True', 'null': 'True', 'to': "orm['survey.Household']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        }
    }

    complete_apps = ['survey']
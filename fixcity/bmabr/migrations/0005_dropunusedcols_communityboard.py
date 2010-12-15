
from south.db import db
from django.db import models
from fixcity.bmabr.models import *
import django.db.utils

class Migration:
    
    def forwards(self, orm):
        unused_cols_to_drop = ('neighborho',
                               'population',
                               'populat_01',
                               'populat_02',
                               'borough',
                               )
        for col in unused_cols_to_drop:
            try:
                db.delete_column(u'gis_community_board', col)
            except django.db.utils.DatabaseError:
                db.rollback_transaction()
                db.start_transaction()
                
    
    
    def backwards(self, orm):
        db.add_column(u'gis_community_board', 'borough',
                      models.CharField(max_length=20, null=True))
        db.add_column(u'gis_community_board', 'neighborho',
                      models.CharField(max_length=100, null=True))
        db.add_column(u'gis_community_board', 'population',
                      models.IntegerField(null=True))
        db.add_column(u'gis_community_board', 'populat_01',
                      models.IntegerField(null=True))
        db.add_column(u'gis_community_board', 'populat_02',
                      models.IntegerField(null=True))

        
    models = {
        'bmabr.comment': {
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rack': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bmabr.Rack']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'bmabr.communityboard': {
            'Meta': {'db_table': "u'gis_community_board'"},
            'board': ('django.db.models.fields.IntegerField', [], {}),
            'boro': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'borocd': ('django.db.models.fields.IntegerField', [], {}),
            'gid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'the_geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {})
        },
        'bmabr.emailsource': {
            'address': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['bmabr.Source']", 'unique': 'True', 'primary_key': 'True'})
        },
        'bmabr.neighborhoods': {
            'Meta': {'db_table': "u'gis_neighborhoods'"},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '43'}),
            'gid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'regionid': ('django.db.models.fields.IntegerField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'the_geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {})
        },
        'bmabr.rack': {
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bmabr.Source']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'bmabr.seeclickfixsource': {
            'image_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'issue_id': ('django.db.models.fields.IntegerField', [], {}),
            'reporter': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['bmabr.Source']", 'unique': 'True', 'primary_key': 'True'})
        },
        'bmabr.source': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'bmabr.statementofsupport': {
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            's_rack': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bmabr.Rack']"})
        },
        'bmabr.subwaystations': {
            'Meta': {'db_table': "u'gis_subway_stations'"},
            'alt_name': ('django.db.models.fields.CharField', [], {'max_length': '38'}),
            'borough': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'closed': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'cross_st': ('django.db.models.fields.CharField', [], {'max_length': '27'}),
            'express': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'gid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            'nghbhd': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'objectid': ('django.db.models.fields.TextField', [], {}),
            'routes': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'the_geom': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'transfers': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'bmabr.twittersource': {
            'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['bmabr.Source']", 'unique': 'True', 'primary_key': 'True'}),
            'status_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }
    
    complete_apps = ['bmabr']

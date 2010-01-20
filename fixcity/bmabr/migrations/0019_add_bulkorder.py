
from south.db import db
from django.db import models
from fixcity.bmabr.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'NYCDOTBulkOrder'
        db.start_transaction()
        db.create_table('bmabr_nycdotbulkorder', (
            ('id', orm['bmabr.nycdotbulkorder:id']),
            ('communityboard', orm['bmabr.nycdotbulkorder:communityboard']),
            ('user', orm['bmabr.nycdotbulkorder:user']),
            ('date', orm['bmabr.nycdotbulkorder:date']),
        ))
        db.send_create_signal('bmabr', ['NYCDOTBulkOrder'])
        db.commit_transaction()

        # That should have created a permission to create bulk orders...
        # but we need a new transaction before we can use it.
        db.start_transaction()
        from django.contrib.auth.models import Group, Permission
        perm = Permission.objects.get(codename='add_nycdotbulkorder')
        # Add a group with that permission.
        group = Group(name='bulk_ordering')
        group.save()
        group.permissions.add(perm)
        group.save()

        # The rest is auto-generated:
        # Adding field 'Rack.locked'
        db.add_column('bmabr_rack', 'locked', orm['bmabr.rack:locked'])
        
        # Changing field 'Borough.shape_area'
        # (to signature: django.db.models.fields.DecimalField(max_digits=1000, decimal_places=100))
        db.alter_column(u'gis_boroughs', 'shape_area', orm['bmabr.borough:shape_area'])
        
        # Changing field 'Borough.shape_leng'
        # (to signature: django.db.models.fields.DecimalField(max_digits=1000, decimal_places=100))
        db.alter_column(u'gis_boroughs', 'shape_leng', orm['bmabr.borough:shape_leng'])
        
        # Changing field 'CityRack.objectid'
        # (to signature: django.db.models.fields.DecimalField(max_digits=1000, decimal_places=100))
        db.alter_column(u'gis_cityracks', 'objectid', orm['bmabr.cityrack:objectid'])
        
        # Changing field 'CityRack.oppaddress'
        # (to signature: django.db.models.fields.DecimalField(max_digits=1000, decimal_places=100))
        db.alter_column(u'gis_cityracks', 'oppaddress', orm['bmabr.cityrack:oppaddress'])
        
        # Changing field 'CityRack.borocode'
        # (to signature: django.db.models.fields.DecimalField(max_digits=1000, decimal_places=100))
        db.alter_column(u'gis_cityracks', 'borocode', orm['bmabr.cityrack:borocode'])
        
        # Changing field 'CityRack.address'
        # (to signature: django.db.models.fields.DecimalField(max_digits=1000, decimal_places=100))
        db.alter_column(u'gis_cityracks', 'address', orm['bmabr.cityrack:address'])
        
        # Changing field 'CityRack.y'
        # (to signature: django.db.models.fields.DecimalField(max_digits=1000, decimal_places=100))
        db.alter_column(u'gis_cityracks', 'y', orm['bmabr.cityrack:y'])
        
        # Changing field 'CityRack.x'
        # (to signature: django.db.models.fields.DecimalField(max_digits=1000, decimal_places=100))
        db.alter_column(u'gis_cityracks', 'x', orm['bmabr.cityrack:x'])
        
        db.commit_transaction()
    
    
    def backwards(self, orm):
        # Remove the group that can add bulk orders.
        from django.contrib.auth.models import Group
        group = Group.objects.get(name='bulk_ordering')
        group.delete()

        # Deleting model 'NYCDOTBulkOrder'
        db.delete_table('bmabr_nycdotbulkorder')
        
        # Deleting field 'Rack.locked'
        db.delete_column('bmabr_rack', 'locked')
        
        # Don't try to set decimial_places back to 1000 as this causes errors.
        # Not sure how things ever worked in the first place!
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'bmabr.borough': {
            'Meta': {'db_table': "u'gis_boroughs'"},
            'borocode': ('django.db.models.fields.SmallIntegerField', [], {}),
            'boroname': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'gid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'shape_area': ('django.db.models.fields.DecimalField', [], {'max_digits': '1000', 'decimal_places': '100'}),
            'shape_leng': ('django.db.models.fields.DecimalField', [], {'max_digits': '1000', 'decimal_places': '100'}),
            'the_geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {})
        },
        'bmabr.cityrack': {
            'Meta': {'db_table': "u'gis_cityracks'"},
            'address': ('django.db.models.fields.DecimalField', [], {'max_digits': '1000', 'decimal_places': '100'}),
            'alt_addres': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            'boro_1': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'borocode': ('django.db.models.fields.DecimalField', [], {'max_digits': '1000', 'decimal_places': '100'}),
            'c_racksid': ('django.db.models.fields.CharField', [], {'max_length': '17'}),
            'from__cros': ('django.db.models.fields.CharField', [], {'max_length': '22'}),
            'gid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '13'}),
            'large': ('django.db.models.fields.IntegerField', [], {}),
            'neighborho': ('django.db.models.fields.CharField', [], {'max_length': '21'}),
            'objectid': ('django.db.models.fields.DecimalField', [], {'max_digits': '1000', 'decimal_places': '100'}),
            'oppaddress': ('django.db.models.fields.DecimalField', [], {'max_digits': '1000', 'decimal_places': '100'}),
            'rackid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'side_of_st': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'small': ('django.db.models.fields.IntegerField', [], {}),
            'street_nam': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            'the_geom': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'to__cross': ('django.db.models.fields.CharField', [], {'max_length': '22'}),
            'x': ('django.db.models.fields.DecimalField', [], {'max_digits': '1000', 'decimal_places': '100'}),
            'y': ('django.db.models.fields.DecimalField', [], {'max_digits': '1000', 'decimal_places': '100'}),
            'zip_code_1': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        'bmabr.communityboard': {
            'Meta': {'db_table': "u'gis_community_board'"},
            'board': ('django.db.models.fields.IntegerField', [], {}),
            'borocd': ('django.db.models.fields.IntegerField', [], {}),
            'borough': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bmabr.Borough']"}),
            'gid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'the_geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {})
        },
        'bmabr.emailsource': {
            'address': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['bmabr.Source']", 'unique': 'True', 'primary_key': 'True'})
        },
        'bmabr.nycdotbulkorder': {
            'communityboard': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bmabr.CommunityBoard']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'bmabr.rack': {
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
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
        'bmabr.twittersource': {
            'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['bmabr.Source']", 'unique': 'True', 'primary_key': 'True'}),
            'status_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['bmabr']
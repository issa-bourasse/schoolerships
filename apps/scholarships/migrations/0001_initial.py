# Generated by Django 4.2.7 on 2025-07-18 06:01

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SearchSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_name', models.CharField(max_length=200)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('target_scholarships', models.IntegerField(default=10000)),
                ('scholarships_found', models.IntegerField(default=0)),
                ('websites_searched', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('running', 'Running'), ('paused', 'Paused'), ('completed', 'Completed'), ('failed', 'Failed')], default='running', max_length=20)),
                ('ai_model_used', models.CharField(blank=True, max_length=100)),
                ('search_strategy', models.TextField(blank=True)),
                ('success_rate', models.FloatField(default=0.0)),
                ('average_processing_time', models.FloatField(default=0.0)),
                ('notes', models.TextField(blank=True)),
                ('error_log', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'search_sessions',
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='WebsiteTarget',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('url', models.URLField(max_length=1000, unique=True)),
                ('domain', models.CharField(db_index=True, max_length=200)),
                ('website_type', models.CharField(choices=[('university', 'University'), ('government', 'Government Portal'), ('foundation', 'Foundation/NGO'), ('company', 'Company'), ('database', 'Scholarship Database'), ('other', 'Other')], db_index=True, max_length=50)),
                ('discovered_by_ai', models.BooleanField(default=True)),
                ('discovery_method', models.CharField(blank=True, max_length=100)),
                ('discovered_at', models.DateTimeField(auto_now_add=True)),
                ('last_scraped', models.DateTimeField(blank=True, null=True)),
                ('scrape_count', models.IntegerField(default=0)),
                ('success_count', models.IntegerField(default=0)),
                ('scholarships_found', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('is_blocked', models.BooleanField(default=False)),
                ('block_reason', models.CharField(blank=True, max_length=200)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('language', models.CharField(blank=True, max_length=50)),
            ],
            options={
                'db_table': 'website_targets',
                'ordering': ['-scholarships_found', '-last_scraped'],
                'indexes': [models.Index(fields=['domain', 'is_active'], name='website_tar_domain_b6dddb_idx'), models.Index(fields=['website_type', 'country'], name='website_tar_website_658d87_idx')],
            },
        ),
        migrations.CreateModel(
            name='Scholarship',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=500)),
                ('provider', models.CharField(db_index=True, max_length=300)),
                ('country', models.CharField(db_index=True, max_length=100)),
                ('region', models.CharField(blank=True, max_length=100)),
                ('tunisia_eligible', models.BooleanField(db_index=True, default=False)),
                ('eligible_countries', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, help_text='List of eligible countries', size=None)),
                ('field_of_study', models.CharField(db_index=True, max_length=200)),
                ('academic_level', models.CharField(choices=[('bachelor', "Bachelor's Degree"), ('master', "Master's Degree"), ('phd', 'PhD/Doctorate'), ('professional', 'Professional Development'), ('bootcamp', 'Bootcamp/Certificate'), ('any', 'Any Level')], db_index=True, max_length=50)),
                ('ai_relevance_score', models.FloatField(db_index=True, default=0.0)),
                ('web_dev_relevance_score', models.FloatField(db_index=True, default=0.0)),
                ('it_relevance_score', models.FloatField(db_index=True, default=0.0)),
                ('overall_relevance_score', models.FloatField(db_index=True, default=0.0)),
                ('funding_type', models.CharField(choices=[('full', 'Fully Funded'), ('partial', 'Partially Funded'), ('tuition', 'Tuition Only'), ('living', 'Living Expenses Only')], db_index=True, default='full', max_length=20)),
                ('funding_amount', models.CharField(blank=True, max_length=200)),
                ('funding_coverage', models.TextField(blank=True)),
                ('application_deadline', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('application_url', models.URLField(max_length=1000, validators=[django.core.validators.URLValidator()])),
                ('application_process', models.TextField(blank=True)),
                ('required_documents', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, size=None)),
                ('language_requirements', models.CharField(blank=True, max_length=200)),
                ('gpa_requirement', models.CharField(blank=True, max_length=100)),
                ('age_requirement', models.CharField(blank=True, max_length=100)),
                ('other_requirements', models.TextField(blank=True)),
                ('duration', models.CharField(blank=True, max_length=100)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('number_of_awards', models.CharField(blank=True, max_length=100)),
                ('contact_email', models.EmailField(blank=True, max_length=254)),
                ('contact_phone', models.CharField(blank=True, max_length=50)),
                ('contact_website', models.URLField(blank=True, max_length=1000)),
                ('source_url', models.URLField(db_index=True, max_length=1000)),
                ('source_website', models.CharField(db_index=True, max_length=200)),
                ('scraped_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('is_verified', models.BooleanField(db_index=True, default=False)),
                ('verification_notes', models.TextField(blank=True)),
                ('ai_processed', models.BooleanField(db_index=True, default=False)),
                ('ai_processing_notes', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'scholarships',
                'ordering': ['-overall_relevance_score', '-scraped_at'],
                'indexes': [models.Index(fields=['tunisia_eligible', 'is_active'], name='scholarship_tunisia_78392d_idx'), models.Index(fields=['field_of_study', 'academic_level'], name='scholarship_field_o_25435a_idx'), models.Index(fields=['funding_type', 'application_deadline'], name='scholarship_funding_16f24d_idx'), models.Index(fields=['overall_relevance_score', 'tunisia_eligible'], name='scholarship_overall_3ad8fb_idx')],
            },
        ),
    ]

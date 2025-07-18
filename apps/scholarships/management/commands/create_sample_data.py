"""
Management command to create sample scholarship data
Demonstrates the AI scholarship hunter system with realistic data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from apps.scholarships.models import Scholarship, SearchSession, WebsiteTarget
from apps.ai_agent.models import AIAgent, AIThought, SearchStrategy


class Command(BaseCommand):
    help = 'Create sample scholarship data for demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of sample scholarships to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(
            self.style.SUCCESS(f'Creating {count} sample scholarships...')
        )
        
        # Sample data
        providers = [
            'University of Cambridge', 'MIT', 'Stanford University', 'Oxford University',
            'ETH Zurich', 'Technical University of Munich', 'University of Toronto',
            'Australian National University', 'University of Tokyo', 'NUS Singapore',
            'KTH Royal Institute', 'EPFL', 'Imperial College London', 'Carnegie Mellon',
            'UC Berkeley', 'Harvard University', 'Yale University', 'Princeton University',
            'Caltech', 'University of Edinburgh', 'King\'s College London', 'LSE',
            'University of Melbourne', 'University of Sydney', 'McGill University',
            'European Commission', 'British Council', 'Fulbright Foundation',
            'DAAD Germany', 'Campus France', 'Netherlands Fellowship Programme'
        ]
        
        countries = [
            'United Kingdom', 'United States', 'Germany', 'France', 'Netherlands',
            'Switzerland', 'Canada', 'Australia', 'Singapore', 'Japan',
            'Sweden', 'Denmark', 'Norway', 'Finland', 'Belgium'
        ]
        
        fields = [
            'Computer Science', 'Artificial Intelligence', 'Machine Learning',
            'Web Development', 'Software Engineering', 'Data Science',
            'Cybersecurity', 'Information Technology', 'Robotics',
            'Digital Innovation', 'Computer Engineering', 'Information Systems'
        ]
        
        scholarship_names = [
            'AI Excellence Scholarship', 'Future Tech Leaders Program',
            'Digital Innovation Fellowship', 'Computer Science Merit Award',
            'Machine Learning Research Grant', 'Cybersecurity Excellence Fund',
            'Web Development Scholarship', 'Data Science Fellowship',
            'International Student Award', 'STEM Excellence Program',
            'Technology Innovation Grant', 'Digital Future Scholarship',
            'AI Research Fellowship', 'Computing Excellence Award',
            'Tech Leadership Program', 'Innovation Scholarship',
            'Global Tech Talent Award', 'Digital Skills Fellowship',
            'Future Engineers Program', 'Technology Merit Scholarship'
        ]
        
        # Create sample scholarships
        scholarships_created = 0
        
        for i in range(count):
            # Random scholarship data
            name = f"{random.choice(scholarship_names)} {random.randint(2024, 2025)}"
            provider = random.choice(providers)
            country = random.choice(countries)
            field = random.choice(fields)
            
            # Tunisia eligibility (70% chance)
            tunisia_eligible = random.random() < 0.7
            
            # Relevance scores
            ai_score = random.uniform(0.3, 1.0) if 'AI' in field or 'Machine Learning' in field else random.uniform(0.0, 0.5)
            web_dev_score = random.uniform(0.3, 1.0) if 'Web' in field else random.uniform(0.0, 0.5)
            it_score = random.uniform(0.4, 1.0) if any(term in field for term in ['Computer', 'Information', 'Cyber']) else random.uniform(0.0, 0.6)
            overall_score = (ai_score + web_dev_score + it_score) / 3
            
            # Application deadline (future dates)
            deadline = timezone.now() + timedelta(days=random.randint(30, 365))
            
            scholarship = Scholarship.objects.create(
                name=name,
                provider=provider,
                country=country,
                tunisia_eligible=tunisia_eligible,
                eligible_countries=['Tunisia', 'Global'] if tunisia_eligible else ['Global'],
                field_of_study=field,
                academic_level=random.choice(['bachelor', 'master', 'phd', 'any']),
                ai_relevance_score=ai_score,
                web_dev_relevance_score=web_dev_score,
                it_relevance_score=it_score,
                overall_relevance_score=overall_score,
                funding_type='full',
                funding_amount='Full tuition + living expenses',
                funding_coverage='100% funding including tuition, accommodation, and stipend',
                application_deadline=deadline,
                application_url=f'https://{provider.lower().replace(" ", "")}.edu/scholarships/{name.lower().replace(" ", "-")}',
                application_process='Online application with academic transcripts, personal statement, and references',
                required_documents=['Academic transcripts', 'Personal statement', 'CV/Resume', 'References'],
                language_requirements='English proficiency (IELTS 6.5+ or TOEFL 90+)',
                gpa_requirement='Minimum 3.5/4.0 or equivalent',
                other_requirements='Strong academic background in relevant field',
                duration=f'{random.randint(1, 4)} years',
                contact_email=f'scholarships@{provider.lower().replace(" ", "")}.edu',
                source_url=f'https://{provider.lower().replace(" ", "")}.edu/scholarships',
                source_website=provider.lower().replace(" ", "") + '.edu',
                is_active=True,
                is_verified=random.random() < 0.8,
                ai_processed=True
            )
            
            scholarships_created += 1
            
            if scholarships_created % 10 == 0:
                self.stdout.write(f'Created {scholarships_created} scholarships...')
        
        # Create sample search session
        session = SearchSession.objects.create(
            session_name='AI Scholarship Discovery Session',
            target_scholarships=10000,
            scholarships_found=scholarships_created,
            websites_searched=25,
            status='running',
            ai_model_used='deepseek-chat',
            search_strategy='AI-guided autonomous discovery with Tunisia focus',
            success_rate=85.5,
            notes='Autonomous AI agents discovering scholarships worldwide'
        )
        
        # Create sample website targets
        websites = [
            ('scholarshipportal.com', 'database', 'Netherlands'),
            ('studyportals.com', 'database', 'Netherlands'),
            ('cambridge.ac.uk', 'university', 'United Kingdom'),
            ('mit.edu', 'university', 'United States'),
            ('stanford.edu', 'university', 'United States'),
            ('ox.ac.uk', 'university', 'United Kingdom'),
            ('ethz.ch', 'university', 'Switzerland'),
            ('tum.de', 'university', 'Germany'),
            ('utoronto.ca', 'university', 'Canada'),
            ('anu.edu.au', 'university', 'Australia'),
            ('ec.europa.eu', 'government', 'Belgium'),
            ('britishcouncil.org', 'foundation', 'United Kingdom'),
            ('fulbright.org', 'foundation', 'United States'),
            ('daad.de', 'government', 'Germany'),
            ('campusfrance.org', 'government', 'France')
        ]
        
        for domain, website_type, country in websites:
            WebsiteTarget.objects.create(
                url=f'https://{domain}',
                domain=domain,
                website_type=website_type,
                country=country,
                discovered_by_ai=True,
                discovery_method='AI autonomous discovery',
                scrape_count=random.randint(1, 10),
                success_count=random.randint(1, 8),
                scholarships_found=random.randint(0, 15),
                is_active=True
            )
        
        # Skip AI agent creation for now due to migration issues
        # Will be added once database schema is properly set up
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- {scholarships_created} scholarships\n'
                f'- 1 search session\n'
                f'- {len(websites)} website targets'
            )
        )

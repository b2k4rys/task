from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from ads.models import Ad, ExchangeProposal
from django.db.models import Q

class AdTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpass123')

        self.client.login(username='testuser', password='testpass123')

        self.ad1 = Ad.objects.create(
            user=self.user,
            title='Laptop for Exchange',
            description='A good condition laptop',
            category='electronics',
            condition='used'
        )
        self.ad2 = Ad.objects.create(
            user=self.other_user,
            title='Books for Exchange',
            description='Set of novels',
            category='books',
            condition='new'
        )

    def test_ad_creation(self):
        response = self.client.post(reverse('ad_create'), {
            'title': 'New Smartphone',
            'description': 'Brand new smartphone for exchange',
            'category': 'electronics',
            'condition': 'new'
        })
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(Ad.objects.filter(title='New Smartphone').exists())

    def test_ad_edit_by_author(self):
        response = self.client.post(reverse('ad_edit', args=[self.ad1.id]), {
            'title': 'Updated Laptop',
            'description': 'A good condition laptop, updated',
            'category': 'electronics',
            'condition': 'used'
        })
        self.assertEqual(response.status_code, 302) 
        self.ad1.refresh_from_db()
        self.assertEqual(self.ad1.title, 'Updated Laptop')

    def test_ad_edit_by_non_author(self):
        self.client.logout()  
        self.client.login(username='otheruser', password='otherpass123')
        response = self.client.post(reverse('ad_edit', args=[self.ad1.id]), {
            'title': 'Updated Laptop',
            'description': 'A good condition laptop, updated',
            'category': 'electronics',
            'condition': 'used'
        })
        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'You are not the author of this ad.')

    def test_ad_delete_by_author(self):
        response = self.client.post(reverse('ad_delete', args=[self.ad1.id]))
        self.assertEqual(response.status_code, 302)  
        self.assertFalse(Ad.objects.filter(id=self.ad1.id).exists())

    def test_ad_delete_by_non_author(self):
        self.client.logout()  
        self.client.login(username='otheruser', password='otherpass123')
        response = self.client.post(reverse('ad_delete', args=[self.ad1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are not the author of this ad.')

    def test_ad_list_search(self):
        response = self.client.get(reverse('ad_list'), {'q': 'laptop'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop for Exchange')
        self.assertNotContains(response, 'Books for Exchange')

    def test_ad_list_filter_category(self):
        response = self.client.get(reverse('ad_list'), {'category': 'electronics'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop for Exchange')
        self.assertNotContains(response, 'Books for Exchange')

    def test_ad_list_filter_condition(self):
        response = self.client.get(reverse('ad_list'), {'condition': 'new'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Books for Exchange')
        self.assertNotContains(response, 'Laptop for Exchange')

    def test_ad_list_pagination(self):
        for i in range(10):
            Ad.objects.create(
                user=self.user,
                title=f'Ad {i}',
                description='Test ad',
                category='other',
                condition='new'
            )
        response = self.client.get(reverse('ad_list'))
        self.assertEqual(response.status_code, 200)
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), 5)  
        response = self.client.get(reverse('ad_list'), {'page': 2})
        self.assertEqual(response.status_code, 200)

class ExchangeProposalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpass123')

        self.client.login(username='testuser', password='testpass123')

        self.ad1 = Ad.objects.create(
            user=self.user,
            title='Laptop for Exchange',
            description='A good condition laptop',
            category='electronics',
            condition='used'
        )
        self.ad2 = Ad.objects.create(
            user=self.other_user,
            title='Books for Exchange',
            description='Set of novels',
            category='books',
            condition='new'
        )

    def test_proposal_create(self):
        response = self.client.post(reverse('proposal_create', args=[self.ad1.id, self.ad2.id]), {
            'comment': 'I would like to exchange my laptop for your books.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ExchangeProposal.objects.filter(ad_sender=self.ad1, ad_receiver=self.ad2).exists())

    def test_proposal_update(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Exchange request'
        )
        response = self.client.post(reverse('proposal_update', args=[proposal.id]), {
            'status': 'accepted'
        })
        self.assertEqual(response.status_code, 302)  
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'accepted')

    def test_proposal_list_filter_by_status(self):
        ExchangeProposal.objects.create(ad_sender=self.ad1, ad_receiver=self.ad2, comment='Proposal 1')
        ExchangeProposal.objects.create(ad_sender=self.ad2, ad_receiver=self.ad1, comment='Proposal 2', status='accepted')
        response = self.client.get(reverse('proposal_list'), {'status': 'pending'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Proposal 1')
        self.assertNotContains(response, 'Proposal 2')

    def test_proposal_list_filter_by_sender(self):
        ExchangeProposal.objects.create(ad_sender=self.ad1, ad_receiver=self.ad2, comment='Proposal 1')
        ExchangeProposal.objects.create(ad_sender=self.ad2, ad_receiver=self.ad1, comment='Proposal 2')
        response = self.client.get(reverse('proposal_list'), {'sender': self.ad1.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Proposal 1')
        self.assertNotContains(response, 'Proposal 2')
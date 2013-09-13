from __future__ import with_statement

from django.template import Template, Context, defaultfilters
from expn_fw.core.test import expnTestCase as TestCase
from django.utils import translation, tzinfo
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.utils.timezone import utc

import expn_fw.contrib.container.interfaces  as interfaces
import expn_fw.contrib.container as container


class EncryptableTests(TestCase):
    
    def setUp(self):
        pass
    
    def test_is_encrypted(self):
        private   =  container.SensitiveData()
        #private.set_data(self.private_str)
        
        self.assertFalse(interfaces.Encryptable.is_encrypted("test"))
        self.assertTrue(interfaces.Encryptable.is_encrypted(private._encrypt("test")))
        
        self.assertFalse(private.is_encrypted("test"))
        self.assertTrue(private.is_encrypted(private._encrypt("test")))
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Data structures that store matching metres for known patterns."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest

import match_result
import simple_identifier


class BadInput(unittest.TestCase):

  def __init__(self, *args, **kwargs):
    super(BadInput, self).__init__(*args, **kwargs)
    self.identifier = simple_identifier.SimpleIdentifier()

  def testEmpty(self):
    """Identifier should fail with empty input."""
    # self.assertRaises(identifier.EmptyInputError,
    #                   self.identifier.IdentifyFromLines, [])
    self.assertIsNone(self.identifier.IdentifyFromLines([]))

  def testNoSyllables(self):
    """Identifier should return no result, for input containing no syllabes."""
    # self.assertIsNone(self.identifier.IdentifyFromLines(['t', 't', 't', 't']))
    self.assertFalse(self.identifier.IdentifyFromLines(['t', 't', 't', 't']))


class KnownValues(unittest.TestCase):

  def __init__(self, *args, **kwargs):
    super(KnownValues, self).__init__(*args, **kwargs)
    self.identifier = simple_identifier.SimpleIdentifier()

  def AssertSingleMatchResultEquals(self, results, metre_name, match_type):
    try:
      assert isinstance(results, list)
      assert len(results) == 1
      result = results[0]
      assert result == metre_name
    except AssertionError:
      print('\n\nMismatch: Got results')
      if results is None:
        print('\tNo results')
      else:
        print(match_result.Description(results, 4))
      print('instead of')
      print('\tMetre name: %s' % metre_name)
      print('\tMatch type: %s' % match_type)
      raise self.failureException

  def testFineAnustubh(self):
    """Good anuṣṭubh should be recognized."""
    verse = ['karmaṇyevādhikāraste',
             'mā phaleṣu kadācana |',
             'mā karmaphalahetur bhūr',
             'mā te saṅgo stvakarmaṇi ||47||']
    self.AssertSingleMatchResultEquals(self.identifier.IdentifyFromLines(verse),
                                       'Anuṣṭup (Śloka)',
                                       match_result.MATCH_TYPE.FULL)

  def testFirstOffAnustubh(self):
    """Anuṣṭubh with first pāda wrong should be recognized."""
    verse = ['तपःस्वाध्यायनिरतं तपस्वी वाग्विदां वरम् ।',
             'नारदं परिपप्रच्छ वाल्मीकिर्मुनिपुङ्गवम् ।। 1.1.1 ।।']
    self.AssertSingleMatchResultEquals(
        self.identifier.IdentifyFromLines(verse),
        'Anuṣṭup (Śloka)',
        match_result.MATCH_TYPE.FULL)

  def testFineMandakranta(self):
    """A valid example of Mandākrāntā should be recognized."""
    verse = ['kazcit kAntAvirahaguruNA svAdhikArAt pramattaH $',
             'zApenAstaMgamitamahimA varSabhogyeNa bhartuH &',
             'yakSaz cakre janakatanayAsnAnapuNyodakeSu %',
             'snigdhacchAyAtaruSu vasatiM rAmagiryAzrameSu // 1.1 //']
    self.AssertSingleMatchResultEquals(
        self.identifier.IdentifyFromLines(verse),
        'Mandākrāntā',
        match_result.MATCH_TYPE.FULL)

  def testMandakrantaWithVpl(self):
    """Mandākrāntā with viṣama-pādānta-laghu."""
    verse = ['tvayy AdAtuM jalam avanate zArGgiNo varNacaure $',
             'tasyAH sindhoH pRthum api tanuM dUrabhAvAt pravAham &',
             'prekSiSyante gaganagatayo nUnam Avarjya dRSTir %',
             'ekaM bhuktAguNam iva bhuvaH sthUlamadhyendranIlam // 1.49 //']
    self.AssertSingleMatchResultEquals(
        self.identifier.IdentifyFromLines(verse),
        'Mandākrāntā',
        match_result.MATCH_TYPE.FULL)

  def testAryaKnown(self):
    """A known example of Āryā should be recognized."""
    verse = ['siṃhaḥ śiśur api nipatati',
             'mada-malina-kapola-bhittiṣu gajeṣu |',
             'prakṛtir iyaṃ sattvavatāṃ',
             'na khalu vayas tejaso hetuḥ ||']
    self.AssertSingleMatchResultEquals(
        self.identifier.IdentifyFromLines(verse),
        'Āryā (strict schema)',
        match_result.MATCH_TYPE.FULL)

  def testAryaUnknown(self):
    """An example of Āryā that has not been explicitly added."""
    verse = ['nītijñā niyatijñā'
             'vādajñā api bhavanti vedajñāḥ',
             'brahmajñā api labhyā',
             'svājñāna-jñānino viralāḥ']
    self.AssertSingleMatchResultEquals(
        self.identifier.IdentifyFromLines(verse),
        'Āryā (strict schema)',
        match_result.MATCH_TYPE.FULL)

  def testBadVerse(self):
    """Test a verse that has typos, and see if correct metre can be guessed."""
    verse = ['स्मराहुताशनमुर्मुरचूर्णतां दधुरिवाम्रवनस्य रजःकणाः ।',
             'निपातिताः परितः पथिकव्रजानुपरि ते परितेपुरतो भृशम् ॥']
    assert self.identifier.IdentifyFromLines(verse) is not None

if __name__ == '__main__':
  unittest.main()

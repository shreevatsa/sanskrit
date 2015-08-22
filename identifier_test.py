#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Data structures that store matching metres for known patterns."""

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import identifier_pipeline


class BadInput(unittest.TestCase):

  def __init__(self, *args, **kwargs):
    super(BadInput, self).__init__(*args, **kwargs)
    self.identifier = identifier_pipeline.IdentifierPipeline()

  def testEmpty(self):
    """Identifier should fail with empty input."""
    self.assertIsNone(self.identifier.IdentifyFromLines([]))

  def testNoSyllables(self):
    """Identifier should return no result, for input containing no syllabes."""
    # self.assertIsNone(self.identifier.IdentifyFromLines(['t', 't', 't', 't']))
    (full_match, results) = self.identifier.IdentifyFromLines(['t', 't', 't', 't'])
    self.assertFalse(full_match)
    self.assertFalse(results)


class KnownValues(unittest.TestCase):

  def __init__(self, *args, **kwargs):
    super(KnownValues, self).__init__(*args, **kwargs)
    self.identifier = identifier_pipeline.IdentifierPipeline()

  def AssertSingleMatchResultEquals(self, identification, metre_name):
    try:
      (full_match, results) = identification
      assert full_match
      assert isinstance(results, list)
      assert len(results) == 1
      result = results[0]
      assert result == metre_name
    except AssertionError:
      print('\n\nMismatch: Got results')
      if results is None:
        print('\tNo results')
      else:
        print('\n'.join('        Metre name: %s' % result for result in results))
      print('instead of')
      print('\tMetre name: %s' % metre_name)
      raise

  def testFineAnustubh(self):
    """Good anuṣṭubh should be recognized."""
    verse = ['karmaṇyevādhikāraste',
             'mā phaleṣu kadācana |',
             'mā karmaphalahetur bhūr',
             'mā te saṅgo stvakarmaṇi ||47||']
    self.AssertSingleMatchResultEquals(self.identifier.IdentifyFromLines(verse), 'Anuṣṭup (Śloka)')

  def testFirstOffAnustubh(self):
    """Anuṣṭubh with first pāda wrong should be recognized."""
    verse = ['तपःस्वाध्यायनिरतं तपस्वी वाग्विदां वरम् ।',
             'नारदं परिपप्रच्छ वाल्मीकिर्मुनिपुङ्गवम् ।। 1.1.1 ।।']
    self.AssertSingleMatchResultEquals(self.identifier.IdentifyFromLines(verse), 'Anuṣṭup (Śloka)')

  def testFineMandakranta(self):
    """A valid example of Mandākrāntā should be recognized."""
    verse = ['kazcit kAntAvirahaguruNA svAdhikArAt pramattaH $',
             'zApenAstaMgamitamahimA varSabhogyeNa bhartuH &',
             'yakSaz cakre janakatanayAsnAnapuNyodakeSu %',
             'snigdhacchAyAtaruSu vasatiM rAmagiryAzrameSu // 1.1 //']
    self.AssertSingleMatchResultEquals(self.identifier.IdentifyFromLines(verse), 'Mandākrāntā')

  def testMandakrantaWithVpl(self):
    """Mandākrāntā with viṣama-pādānta-laghu."""
    verse = ['tvayy AdAtuM jalam avanate zArGgiNo varNacaure $',
             'tasyAH sindhoH pRthum api tanuM dUrabhAvAt pravAham &',
             'prekSiSyante gaganagatayo nUnam Avarjya dRSTir %',
             'ekaM bhuktAguNam iva bhuvaH sthUlamadhyendranIlam // 1.49 //']
    self.AssertSingleMatchResultEquals(self.identifier.IdentifyFromLines(verse), 'Mandākrāntā')

  def testAryaKnown(self):
    """A known example of Āryā should be recognized."""
    verse = ['siṃhaḥ śiśur api nipatati',
             'mada-malina-kapola-bhittiṣu gajeṣu |',
             'prakṛtir iyaṃ sattvavatāṃ',
             'na khalu vayas tejaso hetuḥ ||']
    self.AssertSingleMatchResultEquals(self.identifier.IdentifyFromLines(verse), 'Āryā')

  def testAryaUnknown(self):
    """An example of Āryā that has not been explicitly added."""
    verse = ['nītijñā niyatijñā'
             'vādajñā api bhavanti vedajñāḥ',
             'brahmajñā api labhyā',
             'svājñāna-jñānino viralāḥ']
    self.AssertSingleMatchResultEquals(self.identifier.IdentifyFromLines(verse), 'Āryā')

  def testBadVerse(self):
    """Test a verse that has typos, and see if correct metre can be guessed."""
    verse = ['स्मराहुताशनमुर्मुरचूर्णतां दधुरिवाम्रवनस्य रजःकणाः ।',
             'निपातिताः परितः पथिकव्रजानुपरि ते परितेपुरतो भृशम् ॥']
    (full_match, results) = self.identifier.IdentifyFromLines(verse)
    self.assertFalse(full_match)
    self.assertIsNotNone(results)

if __name__ == '__main__':
  unittest.main()

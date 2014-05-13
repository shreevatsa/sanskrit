# -*- coding: utf-8 -*-
"""List of metres from Vrtta-ratnakara, input by Dr. Dhaval Patel."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

dhaval_vrtta_data_small = [
    ('śrī', 'G'),
    ('strī', 'GG'),
    ('nārī', 'GGG'),
    ('mṛgī', 'GLG'),
    ('kanyā', 'GGGG'),
    ('paṅkti', 'GLLGG'),
    ('tanumadhyā', 'GGLLGG'),
    ('śaśivadanā', 'LLLLGG'),
    ('vasumatī', 'GGLLLG'),
    ('madhumatī', 'LLLLLLG'),
    ('madalekhā', 'GGGLLGG'),
    ('kumāralalitā', 'LGLLLGG'),
    ('haṁsamālā', 'LLGGLGG'),
    ('vidyunmālā', 'GGGG — GGGG'),
    # ('chitrapadā', 'GLLGLLGG'),  # Shouldn't this be citrapadā?
    ('māṇavaka', 'GLLGGLLG'),
    ('haṁsaruta', 'GGGLLLGG'),
    # ('samānikā', 'GLGLGLGL'),   # Ends in laghu, not adding for now
    ('pramāṇikā', 'LGLGLGLG'),
    ('campakamālā', 'GLLGGGLLGG'),
    ('nārācaka', 'GGLGLGLG'),
    ('halamukhī', 'GLGLLLLLG'),
    ('bhujagaśiśubhṛtā', 'LLLLLLG — GG'),
    ('śuddhavirāṭ', 'GGGLLGLGLG'),
    ('paṇava', 'GGGLL — LLGGG'),
    ('mayūrasāriṇī', 'GLGLGLGLGG'),
    # ('rukmavatī', 'GLLGGGLLGG'),  # Same as campakamālā above
    ('mattā', 'GGGG — LLLLGG'),
    ('manoramā', 'LLLGLGLGLG'),
    ('upasthitā', 'GG — LLGLLGLG'),
    # ('indravajrā', 'GGLGGLLGLGG'),  # covered by upajāti
    # ('upendravajrā', 'LGLGGLLGLGG'),  # covered by upajāti
    ('sāndrapada', 'GLLGGLLLLGG'),
    ('sumukhī', 'LLLLG — LLGLLG'),
    ('dodhaka', 'GLLGLLGLLGG'),
    # ('śālinī', 'GGGG — GLGGLGG'),  # in curated
    ('vātormī', 'GGGG — LLGGLGG'),
    ('bhramaravilasita', 'GGGG — LLLLLLG'),
    # ('śrī', 'GLLGG — LLLLGG'),  # Another same name above
    # ('rathoddhatā', 'GLGLLLGLGLG'),  # in curated
    # ('svāgatā', 'GLGLLLGLLGG'),  # in curated
    ('vṛntā', 'LLLL — LLLLGGG'),
    ('bhadrikā', 'LLLLLLGLGLG'),
    ('śyenikā', 'GLGLGLGLGLG'),
    # These two are the same!
    # ('upasthita', 'LGLLLGGGLGG'),  # same as śikhaṇḍita below
    # ('śikhaṇḍita', 'LGLLLGGGLGG'),  # same as upasthita above
    ('śikhaṇḍita / upasthita', 'LGLLLGGGLGG'),  # added
    ('mauktikamālā / kalasvanavaṁśaḥ', 'GLLGLLGGLLG'),  # name from other list
    ('candravartma', 'GLGLLLGLLLLG'),
    # ('vaṁśastha', 'LGLGGLLGLGLG'),  # in curated
    # ('indravaṁśā', 'GGLGGLLGLGLG'),  # in curated
    # ('toṭaka', 'LLGLLGLLGLLG'),  # in curated
    # ('drutavilambita', 'LLLGLLGLLGLG'),  # in curated
    # ('puṭa', 'LLLLLLGGGLGG'),  # in data_dhaval with better name
    # ('pramuditavadanā', 'LLLLLLGLGGLG'), #  Same as prabhā below
    # ('mauktidadāma', 'LGLLGLLGLLGL'),  # Ends in laghu, not adding for now
    ('kusumavicitrā', 'LLLLGG — LLLLGG'),
    ('jaloddhatagati', 'LGLLLGLGLLLG'),
    # ('bhujaṅgaprayāta', 'LGGLGGLGGLGG'),  # in curated
    # ('sragviṇī', 'GLGGLGGLGGLG'),  # in curated
    ('priyaṁvadā', 'LLLGLLLGLGLG'),
    ('maṇimālā', 'GGLLGGGGLLGG'),
    ('lalitā', 'GGLGLLLGLGLG'),
    # ('pramitākṣarā', 'LLGLGLLLGLLG'),  # in curated
    ('ujjvalā', 'LLLLLLGLLGLG'),
    ('vaiśvadevī', 'GGGGG — GLGGLGG'),
    ('jaladharamālā', 'GGGG — LLLLGGGG'),
    ('navamālinī / nayamālinī', 'LLLL — GLGLLLGG'),  # nayamālinī in other list
    # ('prabhā', 'LLLLLLGLGGLG'),  # = pramuditavadanā above, also in curated.
    ('mālatī', 'LLLLGLLGLGLG'),
    ('pañcacāmara', 'LGLGLGLGLGLG'),
    ('tāmarasa', 'LLLLGLLGLLGG'),
    # ('kṣamā', 'LLLLLLGGLGGLG'), # In curated (kept there for more names)
    # ('praharṣiṇī', 'GGGLLLLGLGLGG'),  # in curated
    # ('rucirā', 'LGLGLLLLGLGLG'),  # in curated (kept there for more names)
    # ('mattamayūra', 'GGGG — GLLGGLLGG'), # better name
    # ('mañjubhāṣiṇī', 'LLGLGLLLGLGLG'),  # in curated
    ('kalahaṁsaḥ / nandinī', 'LLGLGLLLGLLGG'),  # kalahaṁsaḥ in other list
    ('candrikā', 'LLLL — LLGGLGLGG'),
    ('asambādhā', 'GGGGG — LLLLLLGGG'),
    ('aparājitā', 'LLLLLLG — LGLLGLG'),
    ('praharaṇakalikā', 'LLLLLLG — LLLLLLG'),
    # ('vasantatilakā', 'GGLGLLLGLLGLGG'),  # in curated
    ('induvadanā', 'GLLLGLLLGLLLGG'),
    ('alolā', 'GGGLLGG — GGGLLGG'),
    # These three below are the same!
    ('śaśikalā', 'LLLLLLL — LLLLLLLG'),
    # ('mālā', 'LLLLLL — LLLLLLLLG'),
    # ('maṇiguṇanikara', 'LLLLLLLL — LLLLLLG'),
    # ('malinī', 'LLLLLLGG — GLGGLGG'),  # Already in curated
    # ('prabhadraka', 'LLLLGLGLLLGLGLG'), # better name
    ('elā', 'LLGLG — LLLLLLLLGG'),
    ('candralekhā', 'GGGGLGG — GGLGGLGG'),
    ('ṛṣabhagajavilasita', 'GLLGLG — LLLLLLLLLG'),
    ('vāṇinī', 'LLLLGLGLLLGLGLGG'),
    # ('śikhariṇī', 'LGGGGG — LLLLLGGLLLG'),  # in curated
    # ('pṛthvī', 'LGLLLGLG — LLLGLGGLG'),  # in curated
    # ('vaṁśapatrapatita', 'GLLGLGLLLGLL — LLLLG'), # better name
    # ('hariṇī', 'LLLLLG — GGGG — LGLLGLG'),  # in curated
    # ('mandākrāntā', 'GGGG — LLLLLG — GLGGLGG'),  # in curated
    # ('narkuṭaka', 'LLLLGLGLLLGLLGLLG'),  # same as kokilaka below
    # ('kokilaka', 'LLLLGLG — LLLGLL — GLLG'),  # in curated
    ('kusumitalatāvellitā', 'GGGGG — LLLLLG — GLGGLGG'),
    ('meghavisphurjita', 'LGGGGG — LLLLLG — GLGGLGG'),
    # ('śārdulavikrīḍita', 'GGGLLGLGLLLG — GGLGGLG'),  # in curated
    ('suvadanā', 'GGGGLGG — LLLLLLG — GGLLLG'),
    # ('vṛtta', 'GLGLGLGLGLGLGLGLGLGL'),  # ends in laghu, not adding for now
    # ('sragdharā', 'GGGGLGG — LLLLLLG — GLGGLGG'),  # in curated
    ('madraka', 'GLLGLGLLLG — LGLLLGLGLLLG'),
    ('aśvalalita', 'LLLLGLGLLLG — LGLLLGLGLLLG'),  # adritanayā in other list
    ('mattākrīḍam', 'GGGGGGGG—LLLLL—LLLLLLLLLG'),  # last 'm' from other list
    ('tanvī', 'GLLGG — LLLLLLG — GLLGLLLLLLGG'),
    ('krauñcapadā', 'GLLGG — GLLGGLLL — LLLLLLL —LLLLG'),
    ('bhujaṅgavijṛmbhita', 'GGGGGGGG — LLLLLLLLLLG —LGLLGLG'),
    ('apavāha', 'GGGLLLLLL — LLLLLL — LLLLLL — LLGGG'),
    ('caṇḍavṛṣṭiprayātadaṇḍaka', 'LLLLLLGLGGLGGLGGLGGLGGLGGLG'),
    ('arṇadaṇḍaka', 'LLLLLLGLGGLGGLGGLGGLGGLGGLGGLG'),
    ('arṇavadaṇḍaka', 'LLLLLLGLGGLGGLGGLGGLGGLGGLGGLGGLG'),
    ('vyāladaṇḍaka', 'LLLLLLGLGGLGGLGGLGGLGGLGGLGGLGGLGGLG'),
    ('jīmūtadaṇḍaka', 'LLLLLLGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLG'),
    ('līlākaradaṇḍaka', 'LLLLLLGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLG'),
    ('uddāmadaṇḍaka', 'LLLLLLGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLG'),
    ('śaṅkhadaṇḍaka', 'LLLLLLGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLG'),
    ('samudradaṇḍaka', 'LLLLLLGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLG'),
    ('bhujaṅgadaṇḍaka',
     'LLLLLLGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLGGLG'),
    ('pracitakadaṇḍaka', 'LLLLLLLGGLGGLGGLGGLGGLGGLGG'),
    ('upacitrā', ['LLGLLGLLGLG', 'GLLGLLGLLGG']),  # even pada same as dodhaka
    ('drutamadhyā', ['GLLGLLGLLGG', 'LLLLGLLGLLGG']),  # odd same as dodhaka
    ('vegavatī', ['LLGLLGLLGLLGG', 'GLLGLLGLLGG']),
    ('bhadravirāṭ', ['GGLLGLGLGG', 'GGGLLGLGLG']),
    ('ketumatī', ['LLGLGLLLGG', 'GLLGLGLLLGG']),
    # ('ākhyānikī', ['GGLGGLLGLGG', 'LGLGGLLGLGG']),  # covered by upajāti
    # ('viparītākhyānikī', ['LGLGGLLGLGG', 'GGLGGLLGLGG']), # covered by upajāti
    ('hariṇaplutā', ['LLGLLGLLGLG', 'LLLGLLGLLGLG']),
    # ('aparavaktra', ['LLLLLLGLGLG', 'LLLLGLLGLGLG']), # in curated
    # ('puṣpitāgrā', ['LLLLLLGLGLGG', 'LLLLGLLGLGLGG']), # in curated
    ('yavātparāmatīya', ['GLGLGLGLGLGL', 'LGLGLGLGLGLG']),
    # What is this?
    # ('padacaturūrdhva', ['........',
    #                      '............',
    #                      '................',
    #                      '....................']),
    ('āpīḍa', ['LLLLLLGG',
               'LLLLLLLLLLGG',
               'LLLLLLLLLLLLLLGG',
               'LLLLLLLLLLLLLLLLLLGG']),
    ('kalikā', ['LLLLLLLLLLGG',
                'LLLLLLGG',
                'LLLLLLLLLLLLLGG',
                'LLLLLLLLLLLLLLLLLLGG']),
    ('lavalī', ['LLLLLLLLLLGG',
                'LLLLLLLLLLLLLLGG',
                'LLLLLLGG',
                'LLLLLLLLLLLLLLLLLLGG']),
    ('amṛtadhārā', ['LLLLLLLLLLGG',
                    'LLLLLLLLLLLLLLGG',
                    'LLLLLLLLLLLLLLLLLLGG',
                    'LLLLLLGG']),
    # ('udgatā', ['LLGLGLLLGL',   # already in curated
    #             'LLLLLGLGLG',
    #             'GLLLLLLGLLG',
    #             'LLGLGLLLGLGLG']),
    ('saurabhaka', ['LLGLGLLLGL',
                    'LLLLLGLGLG',
                    'GLGLLLGLLG',
                    'LLGLGLLLGLGLG']),
    ('lalita', ['LLGLGLLLGL',
                'LLLLLGLGLG',
                'LLLLLLLLGLLG',
                'LLGLGLLLGLGLG']),
    ('upasthitapracupita', ['GGGLLGLGLGLLGG',
                            'LLGLLLLGLGLGG',
                            'LLLLLLLLG',
                            'LLLLLLLLLLGLLGG']),
    ('vardhamāna', ['GGGLLGLGLGLLGG',
                    'LLGLLLLGLGLGG',
                    'LLLLLGLLL',
                    'LLLLLLLLLLGLLGG']),
    ('śuddhavirāḍārṣabha', ['GGGLLGLGLGLLGG',
                            'LLGLLLLGLGLGG',
                            'GGLLGLGLG',
                            'LLLLLLLLLLGLLGG']),
    ]
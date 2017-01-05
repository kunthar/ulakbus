# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Unvan Ekle

Hitap'a personelin Unvan bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetUnvanEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Unvan Bilgi Ekleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetUnvanInsert',
        'fields': {
            'asilVekil': 'asil_vekil',
            'atamaSekli': 'atama_sekli',
            'hizmetSinifi': 'hizmet_sinifi',
            'tckn': 'tckn',
            'unvanKod': 'unvan_kod',
            'unvanTarihi': 'unvan_tarihi',
            'unvanBitisTarihi': 'unvan_bitis_tarihi',
            'kurumOnayTarihi': 'kurum_onay_tarihi',
            'fhzOrani': 'fhz_orani'
        },
        'date_filter': ['unvanTarihi', 'unvanBitisTarihi', 'kurumOnayTarihi'],
        'required_fields': ['tckn', 'unvanKod', 'unvanTarihi', 'hizmetSinifi', 'asilVekil',
                            'atamaSekli', 'kurumOnayTarihi']
    }

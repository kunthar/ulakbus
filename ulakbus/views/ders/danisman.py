# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
"""Danışman Modülü

İlgili İş Akışlarına ait sınıf ve metotları içeren modüldür.

Dönem bazlı danışman atanmasını sağlayan iş akışını yönetir.

"""
from pyoko.exceptions import ObjectDoesNotExist

from pyoko import ListNode
from zengine import forms
from zengine.forms import fields
from zengine.views.crud import CrudView, form_modifier
from ulakbus.models.ogrenci import Donem, DonemDanisman, Okutman
from ulakbus.models.auth import Unit
from collections import OrderedDict
from ulakbus.views.ders.ders import prepare_choices_for_model


class DonemDanismanForm(forms.JsonForm):
    """``DonemDanismanAtama`` sınıfı için form olarak kullanılacaktır.

    """

    ileri = fields.Button("İleri")


class DonemDanismanListForm(forms.JsonForm):
    class Okutmanlar(ListNode):
        secim = fields.Boolean(type="checkbox")
        ad_soyad = fields.String('Ad Soyad')
        key = fields.String('Key', hidden=True)

    kaydet = fields.Button("Kaydet")


class DonemDanismanAtama(CrudView):
    """Dönem Danışman Atama İş Akışı

    Dönem Danışman Atama, aşağıda tanımlı iş akışı adımlarını yürütür.

    - Bölüm Seç
    - Öğretim Elemanlarını Seç
    - Kaydet
    - Kayıt Bilgisi Göster

     Bu iş akışında kullanılan metotlar şu şekildedir:

     Dönem Formunu Listele:
        Kayıtlı dönemleri listeler

     Bölüm Seç:
        Kullanıcının bölüm başkanı olduğu bölümleri listeler

     Öğretim Elemanlarını Seç:
        Seçilen bölümdeki öğretim elemanları listelenir.

     Kaydet:
        Seçilen dönem ve bölüm için seçilen danışman kayıtlarını yapar.

     Kayıt Bilgisi Göster:
        Seçilen öğretim elemanları, dönem ve bölüm bilgilerinden oluşturulan kaydın özeti
        gösterilir.
        Bu adımdan sonra iş akışı sona erer.

     Bu sınıf ``CrudView`` extend edilerek hazırlanmıştır. Temel model
     ``DonemDanisman`` modelidir. Meta.model bu amaçla kullanılmıştır.

     Adımlar arası geçiş manuel yürütülmektedir.

    """

    class Meta:
        model = "DonemDanisman"

    def danisman_sec(self):

        unit = self.current.role.unit
        self.current.task_data['unit_yoksis_no'] = unit.yoksis_no
        okutmanlar = Okutman.objects.set_params(sort='ad asc, soyad asc').filter(birim_no=unit.yoksis_no)
        donem = Donem.objects.get(guncel=True)
        _form = DonemDanismanListForm(current=self, title="Okutman Seçiniz")

        for okt in okutmanlar:
            donem_danismani =_form.Okutmanlar(ad_soyad='%s %s' % (okt.ad, okt.soyad),
                                     key=okt.key)
            try:
                DonemDanisman.objects.get(donem=donem, okutman=okt, bolum=unit)
                donem_danismani.secim = True
            except ObjectDoesNotExist:
                donem_danismani.secim = False

        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_selection"] = False

    def danisman_kaydet(self):
        yoksis_no = self.current.task_data['unit_yoksis_no']
        unit = Unit.objects.get(yoksis_no=yoksis_no)
        donem = Donem.objects.get(guncel=True)
        danismanlar = self.current.input['form']['Okutmanlar']

        # Bölümün ilgili dönemine ait bütün danışmanları sil
        try:
            for dd in DonemDanisman.objects.filter(donem=donem, bolum=unit):
                dd.delete()
        except:
            pass

        for danisman in danismanlar:
            if danisman['secim']:
                key = danisman['key']
                okutman = Okutman.objects.get(key)
                donem_danisman = DonemDanisman()
                donem_danisman.donem = donem
                donem_danisman.okutman = okutman
                donem_danisman.bolum = unit
                try:
                    donem_danisman.save()
                except Exception as e:
                    print(e.message)

    def kayit_bilgisi_ver(self):
        yoksis_no = self.current.task_data['unit_yoksis_no']
        unit = Unit.objects.get(yoksis_no=yoksis_no)
        donem = Donem.objects.get(guncel=True)

        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Danismanlar Kaydedildi',
            "msg": '%s dönemi için %s programına ait danışman listesi kaydedilmiştir' % (
                donem, unit)}

    @form_modifier
    def donem_danisman_list_form_inline_edit(self, serialized_form):
        """DonemDanismanListForm'da seçim alanına inline edit özelliği sağlayan method.

        """
        if 'Okutmanlar' in serialized_form['schema']['properties']:
            serialized_form['inline_edit'] = ['secim']

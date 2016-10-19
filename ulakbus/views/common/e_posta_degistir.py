# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from zengine.views.crud import CrudView
from zengine.forms import JsonForm
from zengine.forms import fields
from ulakbus.services.zato_wrapper import E_PostaYolla
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.views.common.profil_sayfasi_goruntuleme import mesaj_goster
from ulakbus.views.common.profil_sayfasi_goruntuleme import aktivasyon_kodu_uret
from zengine.lib.cache import EMailVerification


class EPostaForm(JsonForm):
    birincil_e_posta = fields.String(__(u"Birincil e-postanız"))


class EPostaDegistir(CrudView):
    """
    Kullanıcıların birincil e-posta adreslerini değiştirebilmelerini sağlar,
    bu değişim yapılırken kullanıcıdan yeni belirlediği e-posta adresini doğrulaması
    istenir.
    """

    def yeni_e_posta_girisi(self):
        """
        Kullanıcının birincil e_posta değişikliğini yapabileceği ekran oluşturulur ve birincil olarak belirlemek
        istediği e_posta adresini girmesi istenir. Bu işlem sonunda girdiği adrese doğrulama linki gönderilecektir.

        """
        _form = EPostaForm(current=self.current, title=_(u'Yeni E-Posta Girişi'))
        _form.help_text = _(u"""Birincil olarak belirlemek istediğiniz e-posta adresinize
                          doğrulama linki gönderilecektir.""")
        _form.birincil_e_posta = self.current.user.e_mail
        _form.e_posta = fields.String(_(u"Birincil olarak belirlemek istediğiniz e-posta adresinizi yazınız."))
        _form.degistir = fields.Button(_(u"Doğrulama Linki Yolla"))
        self.form_out(_form)

    def e_posta_bilgisini_kaydet(self):
        """
        Doğrulama linki gönderilecek e_posta adresi oluşturulan aktivasyon kodu ile cache'e kaydedilir.

        """

        self.current.task_data["bilgi"] = self.current.task_data["e_posta"] = self.input['form']['e_posta']
        self.current.task_data["aktivasyon"] = aktivasyon_kodu_uret()
        EMailVerification(self.current.task_data["aktivasyon"]).set(self.current.task_data["bilgi"], 7200)

    def aktivasyon_maili_yolla(self):
        """
        Hashlenmiş 40 karakterli bir aktivasyon kodu üretilir ve cache'e atılır. Zato servisi ile
        kullanıcının yeni olarak belirlediği e_posta adresine doğrulama linki gönderilir.

        """

        posta_gonder = E_PostaYolla(service_payload={
            "wf_name": self.current.task_data['wf_name'],
            "e_posta": self.current.task_data["e_posta"],
            "aktivasyon_kodu": self.current.task_data["aktivasyon"],
            "bilgi": self.current.task_data["bilgi"]})

        posta_gonder.zato_request()

    def link_gonderimi_bilgilendir(self):
        """
        Doğrulama linki yollandığında kullanıcı linkin yollandığına dair bilgilendirilir.

        """
        self.current.task_data['msg'] = _(u"""'%s' adresinize doğrulama linki gönderilmiştir.
        Lütfen e-posta'nızdaki bağlantı linkine tıklayarak e-posta adresinin size ait
        olduğunu doğrulayınız. """) % (self.current.task_data['e_posta'])

        mesaj_goster(self, 'E-Posta Doğrulama', 'info')

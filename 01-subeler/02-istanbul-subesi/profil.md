# İstanbul Şubesi - Şube Profili ve Operasyonel Yapı

## 1. Genel Tanım ve Lokasyon Rolü
İstanbul Şubesi, holdingin ticari kalbi, satış operasyonları, pazarlama stratejileri ve bölgesel saha ekiplerinin ana üssüdür. Finansal merkez Ankara'da yer alırken, müşteri ilişkileri, büyük kurumsal sözleşmeler ve pazarlama faaliyetleri İstanbul Maslak ofisinden yürütülmektedir.

* **Lokasyon:** Maslak / Sarıyer, İstanbul
* **Personel Kapasitesi:** 150 Personel (Ofis İçi ve Dinamik Saha Ekipleri)
* **Ağ Rolü:** Dağıtık Şube (Distributed Branch with DIA - Direct Internet Access & SD-WAN Spoke)
* **Çalışma Rejimi:** Hibrit ve Yüksek Mobiliteye Sahip Saha Entegrasyonu

---

## 2. Departman Dağılımı ve Personel Profili

| Departman | Personel Sayısı | Rol ve Görev Tanımları | Kullanılan Temel Sistemler | Ağ ve Güvenlik Profili |
| :--- | :---: | :--- | :--- | :--- |
| **Kurumsal Satış & İhale** | 60 | Müşteri portföy yönetimi, teklif hazırlama, ihale takibi | Salesforce CRM, SAP SD, MS Office 365, DocuSign | Yüksek harici SaaS kullanımı, mobil VPN gereksinimi |
| **Dijital Pazarlama & İletişim**| 40 | Sosyal medya yönetimi, dijital reklamlar, grafik ve video içerik üretimi | Adobe Creative Cloud, Meta Business Suite, Google Analytics, YouTube | Yüksek bant genişliği, CDN ve multimedya transferi |
| **Bölgesel Saha Ekipleri** | 35 | Müşteri yerinde teknik destek, sözleşme teslimatı, saha denetimi | Mobil Tabletler, Saha Destek Portalı, Mobil CRM | 802.1X dinamik doğrulama, ZTNA / EDR ajan kontrolü |
| **Lokal Operasyon & İdari** | 15 | Ofis idaresi, lokal faturalama, kargo/lojistik ve sekreterya | EBYS, Lokal Yazıcılar, IP Telefonlar | Sabit kurumsal VLAN erişimi |
| **Toplam** | **150** | - | - | - |

---

## 3. Günlük Trafik Dinamikleri ve Misafir Yoğunluğu

İstanbul ofisi, haftalık ortalama 100-150 harici ziyaretçi, müşteri ve ajans temsilcisine ev sahipliği yapmaktadır. Bu nedenle:
1. **Misafir Ağı (Guest Wi-Fi):** Şirket içi kurumsal ağdan (VLAN 110) fiziksel/mantıksal olarak tamamen izole edilmiş, yalnızca internet çıkışına izin veren ve bant genişliği sınırlandırılmış özel bir Misafir VLAN'ı (VLAN 120) zorunludur.
2. **SaaS ve Bulut Ağırlıklı Operasyon:** Satış ve pazarlama ekiplerinin trafiğinin %80'i Microsoft 365, Teams, Zoom ve Salesforce üzerinedir. Tüm bu trafiği Ankara Genel Merkez üzerinden dolaştırmak gereksiz gecikme (hairpinning) yaratacağından, Direct Internet Access (DIA) mimarisi benimsenmiştir.

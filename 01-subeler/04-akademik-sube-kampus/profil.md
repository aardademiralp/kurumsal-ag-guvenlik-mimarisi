# Akademik Şube ve Kampüs - Lokasyon Profili ve Kullanıcı Dinamikleri

## 1. Genel Tanım ve Kampüs Rolü
Akademik Şube ve Üniversite Kampüsü, holdingin eğitim, akademik araştırma, bilimsel yayın ve yüksek kapasiteli dijital kütüphane altyapısına ev sahipliği yapan en yüksek kullanıcı yoğunluğuna sahip lokasyonudur. Kampüs; fakülteler, öğrenci yurtları, amfiler, bilgisayar laboratuvarları ve modern bir dijital kütüphaneden oluşan geniş bir alana yayılmıştır.

* **Lokasyon:** İncek Kampüsü, Ankara
* **Toplam Kullanıcı Nüfusu:** 10.700 Kişi (10.000 Öğrenci + 500 Akademisyen + 200 İdari Personel)
* **Ağ Rolü:** Yüksek Yoğunluklu Kampüs Omurgası (High-Density Campus Backbone with Eduroam & 10G Core)
* **Çalışma Rejimi:** 7/24 Kesintisiz (Yurtlar ve LMS gece yoğunluğu, amfiler gündüz yoğunluğu)

---

## 2. Kullanıcı Grupları ve Kampüs Fonksiyonel Birimleri

| Kullanıcı / Birim Grubu | Nüfus | Coğrafi Alanlar | Temel Dijital İhtiyaçlar | Güvenlik ve Ağ Profili |
| :--- | :---: | :--- | :--- | :--- |
| **Öğrenci Kitlesi** | 10.000 | Amfiler, Öğrenci Yurtları, Kütüphane, Kafeteryalar | Eduroam Wi-Fi, LMS (Moodle/Canvas), Mobil Video, Araştırma | Sıkı İç İzolasyon, P2P/Torrent Engelleme, Kota/QoS |
| **Akademik Personel (Öğretim Üyeleri)**| 500 | Fakülte Binaları, Dekanlıklar, Araştırma Laboratuvarları | Bilimsel Veritabanları (IEEE, ScienceDirect), Zoom, LMS Yönetimi | Yüksek Öncelikli İnternet, Akademik VLAN, Araştırma İzni |
| **İdari İşler & Öğrenci İşleri**| 200 | Rektörlük, Öğrenci İşleri Daire Bşk., Personel Dairesi | Öğrenci Bilgi Sistemi (ÖBS), EBYS, Kurumsal Finans/Bordro | Katı Kurumsal İzolasyon, 802.1X EAP-TLS, KVKK Hassasiyeti |
| **Kampüs Veri Merkezi / LMS** | - | Kampüs Sistem Odası | LMS Sunucuları, Dijital Kütüphane Depoları, Web Portalları | DMZ / Sunucu Güvenliği, Anti-DDoS, WAF Koruması |
| **Toplam Kullanıcı** | **10.700** | - | - | - |

---

## 3. Kampüs Yaşam Döngüsü ve Trafik Dinamikleri

1. **Gündüz Saatleri (08:30 - 17:30):**
   * Trafik yoğunluğu amfiler, fakülte derslikleri ve kütüphanede toplanır.
   * Eşzamanlı video akışları, interaktif ders sunumları ve kütüphane veri tabanı taramaları tepe noktaya ulaşır.
2. **Akşam ve Gece Saatleri (18:00 - 02:00):**
   * Trafik odağı öğrenci yurtlarına (3.000 yatak kapasitesi) kayar.
   * Çevrimiçi eğitim kayıtlarının izlenmesi, araştırma projeleri ve yüksek hacimli eğlence/multimedya akışı (YouTube, Twitch, Netflix vb.) gerçekleşir.
3. **Eduroam (Education Roaming) Entegrasyonu:**
   * Dünyanın her yerinden gelen misafir araştırmacılar ve diğer üniversite mensupları kendi kurumsal kimlikleriyle (802.1X RADIUS) kampüs Wi-Fi ağına doğrudan bağlanır.

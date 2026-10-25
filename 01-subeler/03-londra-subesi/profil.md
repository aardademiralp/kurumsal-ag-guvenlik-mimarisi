# Londra Şubesi - Şube Profili ve Uluslararası Operasyon Mimarisi

## 1. Genel Tanım ve Lokasyon Rolü
Londra Şubesi, holdingin uluslararası ticaret operasyonları, küresel fon ve yatırım ilişkileri, uluslararası hukuk müşavirliği ve Avrupa merkezli C-Level yönetim temaslarının yürütüldüğü prestij ve finans üssüdür. Az sayıda ancak yüksek yetkili ve hassas veriyle çalışan personelin yer aldığı bu ofiste güvenlik seviyesi en üst düzeydedir (Maximum Security & High Privacy).

* **Lokasyon:** Canary Wharf / City of London, Birleşik Krallık (UK)
* **Personel Kapasitesi:** 50 Personel (Yüksek Kıdemli Uzmanlar ve Yöneticiler)
* **Ağ Rolü:** Güvenli Uluslararası Uç Nokta (Secure International Spoke with ZTNA & Strict Geo-IP)
* **Çalışma Rejimi:** Tam Zamanlı & Sık Seyahat Eden VIP Mobil Kullanıcılar

---

## 2. Departman Dağılımı ve Rol Matrisi

| Departman | Personel Sayısı | Rol ve Görev Tanımı | İşlenen Verinin Gizlilik Seviyesi | Kritik Sistem Gereksinimi |
| :--- | :---: | :--- | :--- | :--- |
| **Uluslararası Ticaret & Hazine** | 20 | Küresel emtia ticareti, döviz/arbitraj, uluslararası sözleşmeler | Gizli / Finansal (Confidential) | Bloomberg Terminal, Refinitiv Eikon, SAP Treasury |
| **Uluslararası Hukuk & Tahkim** | 15 | Sınır ötesi tahkim, M&A sözleşmeleri, küresel mevzuat uyumu | Çok Gizli (Strictly Confidential) | Güvenli Sanal Veri Odası (VDR), Şifreli EBYS |
| **Avrupa Yönetim İcra Kurulu** | 10 | Holding Avrupa temsilciliği, fon yöneticileri, C-Suite | En Üst Düzey Yönetim (Restricted) | ZTNA Sertifikalı VIP İstemciler, Güvenli Telepresence |
| **Lokal Operasyon & VIP Destek**| 5 | Londra ofis koordinasyonu, lokal BT ve VIP masaüstü desteği | Sistem Güvenliği | Lokal OOBM, Jumpbox, FortiGate/Palo Alto Konsol |
| **Toplam** | **50** | - | - | - |

---

## 3. Güvenlik ve Uyum Gereksinimleri (UK GDPR & ZTNA)

1. **UK Data Protection Act 2018 & UK GDPR:**
   * Londra ofisinde üretilen ve işlenen verilerin AB ve Birleşik Krallık dışındaki ülkelere aktarımı sıkı denetime tabidir.
   * Şifresiz hiçbir veri hattı üzerinden kurum içi iletişim yapılamaz.
2. **Sıfır Güven Ağ Erişimi (ZTNA):**
   * Kullanıcılar ofiste olsalar dahi salt IP/VLAN bazında doğrudan sunuculara erişemezler; cihaz sağlık durumu (Device Posture: EDR aktif, OS güncel, disk şifreli) ve mTLS sertifikası her istekte doğrulanır.
3. **Ofis İçi Sessizlik ve Fiziksel Standart:**
   * Canary Wharf ofis mimarisi açık ofis ve akustik toplantı odalarından oluştuğu için sistem odası ayrılmış küçük bir kabinetten ibarettir. Ağ ve güvenlik donanımının kompakt, az güç tüketen ve fansız/düşük gürültülü (low-noise / fanless) olması şarttır.

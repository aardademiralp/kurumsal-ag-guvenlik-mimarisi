# Akademik Şube ve Kampüs - IP Adresleme ve VLAN Segmentasyon Planı

## 1. Mimari Adresleme Stratejisi
Kampüs ağı, 10.000 öğrenci ve bini aşkın personelin yaratacağı devasa Layer 2 broadcast fırtınalarını (broadcast domain explosion) önlemek için dikkatle alt ağlara (subnets) ve VLAN havuzlarına (VLAN Pooling) bölünmüştür.

* **Öğrenci Wi-Fi / Eduroam Süperneti:** `10.100.0.0/16` (Toplam 65.534 IP adresi). Bu süpernet, kablosuz kontrolcüler (WLC) üzerinde 6 adet dinamik alt-VLAN (VLAN 300-305) arasında hash tabanlı döndürülür (`VLAN Pooling / Hash-based assignment`).
* **Fakülte ve İdari Birimler Süperneti:** `10.101.0.0/16`

---

## 2. Detaylı IP ve VLAN Tablosu

| VLAN ID | VLAN Adı | Güvenlik Bölgesi (Zone) | Ağ Adresi (CIDR) | Alt Ağ Maskesi | Varsayılan Ağ Geçidi (GW) | DHCP Dağıtım Aralığı | Statik Rezerve Alan | Açıklama |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **300** | `VLAN_CAMPUS_EDUROAM_1` | `Zone_Campus_Student` | `10.100.0.0/19` | `255.255.224.0` | `10.100.0.1` | `10.100.0.10 - 10.100.31.254` | `10.100.0.2 - 10.100.0.9` | Amfiler & Kütüphane Wi-Fi Havuzu 1 (8.190 IP) |
| **301** | `VLAN_CAMPUS_EDUROAM_2` | `Zone_Campus_Student` | `10.100.32.0/19` | `255.255.224.0` | `10.100.32.1` | `10.100.32.10 - 10.100.63.254`| `10.100.32.2 - 10.100.32.9` | Öğrenci Yurtları Wi-Fi Havuzu 2 (8.190 IP) |
| **302** | `VLAN_CAMPUS_EDUROAM_3` | `Zone_Campus_Student` | `10.100.64.0/19` | `255.255.224.0` | `10.100.64.1` | `10.100.64.10 - 10.100.95.254`| `10.100.64.2 - 10.100.64.9` | Açık Alanlar & Sosyal Tesisler Havuz 3 (8.190 IP) |
| **303** | `VLAN_CAMPUS_EDUROAM_4` | `Zone_Campus_Student` | `10.100.96.0/19` | `255.255.224.0` | `10.100.96.1` | `10.100.96.10 - 10.100.127.254`| `10.100.96.2 - 10.100.96.9`| Mühendislik & Fen Lab Wi-Fi Havuzu 4 (8.190 IP) |
| **304** | `VLAN_CAMPUS_EDUROAM_5` | `Zone_Campus_Student` | `10.100.128.0/19`| `255.255.224.0` | `10.100.128.1` | `10.100.128.10 - 10.100.159.254`| `10.100.128.2 - 10.100.128.9`| Tıp Fakültesi & Hastane Wi-Fi Havuzu 5 (8.190 IP) |
| **305** | `VLAN_CAMPUS_EDUROAM_6` | `Zone_Campus_Student` | `10.100.160.0/19`| `255.255.224.0` | `10.100.160.1` | `10.100.160.10 - 10.100.191.254`| `10.100.160.2 - 10.100.160.9`| Spor Tesisleri & Konukevi Wi-Fi Havuzu 6 (8.190 IP) |
| **310** | `VLAN_CAMPUS_ACADEMIC` | `Zone_Campus_Academic`| `10.101.10.0/24` | `255.255.255.0` | `10.101.10.1` | `10.101.10.50 - 10.101.10.250`| `10.101.10.2 - 10.101.10.49` | Akademisyen Ofisleri & PC'leri (500 Personel) |
| **320** | `VLAN_CAMPUS_ADMIN_OBS`| `Zone_Campus_Admin` | `10.101.20.0/24` | `255.255.255.0` | `10.101.20.1` | `10.101.20.50 - 10.101.20.250`| `10.101.20.2 - 10.101.20.49` | Rektörlük, Öğrenci İşleri, Personel Dairesi |
| **330** | `VLAN_CAMPUS_SERVERS` | `Zone_Campus_DC_LMS` | `10.101.30.0/24` | `255.255.255.0` | `10.101.30.1` | *DHCP Kapalı* | `10.101.30.2 - 10.101.30.254` | Kampüs LMS (Moodle), Kütüphane Sunucuları, DNS |
| **399** | `VLAN_CAMPUS_OOBM` | `Zone_Campus_OOBM` | `10.101.99.0/24` | `255.255.255.0` | `10.101.99.1` | *DHCP Kapalı* | `10.101.99.2 - 10.101.99.254` | Omurga Switchler, NGFW Mgmt, PDU, AP Kontrolcüsü |

---

## 3. DHCP Yapılandırması ve Lease Süreleri

1. **Öğrenci Wi-Fi Havuzları (VLAN 300-305):**
   * **Kiralama Süresi (Lease Time):** `120 Dakika (2 Saat)`.
   * *Gerekçe:* Öğrenciler kampüste sürekli yer değiştirmekte ve amfi aralarında farklı AP'lere geçmektedir. Kısa kiralama süresi IP adreslerinin tükenmesini (pool exhaustion) engeller.
   * **DNS Dağıtımı:** `10.101.30.10` (Kampüs Yerel Caching DNS) ve `1.1.1.1`.
2. **Akademik Personel (VLAN 310) ve İdari İşler (VLAN 320):**
   * **Kiralama Süresi:** `8 Gün`.
   * **DNS Dağıtımı:** `10.10.100.10` (Merkezi Active Directory DC) ve `10.101.30.10`.

---

## 4. Kampüs Sunucu ve Kritik IP Rezervasyonları (VLAN 330)

* `10.101.30.10`: Kampüs Birincil Caching DNS & NTP Sunucusu (BIND9 / Chrony)
* `10.101.30.11`: Kampüs İkincil DNS Sunucusu
* `10.101.30.20`: Öğrenim Yönetim Sistemi (LMS Moodle Web Front-End 01)
* `10.101.30.21`: Öğrenim Yönetim Sistemi (LMS Moodle Web Front-End 02)
* `10.101.30.25`: LMS PostgreSQL / Redis Kümesi VIP
* `10.101.30.30`: Öğrenci Bilgi Sistemi (ÖBS) Veri Tabanı Uygulama Sunucusu
* `10.101.30.50`: FreeRADIUS / Eduroam Ulusal Kimlik Doğrulama Gateway Sunucusu (ULAKBİM Proxy)

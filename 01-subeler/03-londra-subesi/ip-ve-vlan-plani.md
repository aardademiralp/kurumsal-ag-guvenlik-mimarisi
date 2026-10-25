# Londra Şubesi - IP Adresleme ve VLAN Segmentasyon Planı

## 1. Mimari Adresleme Stratejisi
Londra Şubesi, holding global IP planında `10.30.0.0/16` süpernet bloğuna ayrılmıştır. Şubede misafir ağı bulunmamakta; harici konuklar yalnızca hücresel veri (5G Hotspot) üzerinden çalışmaktadır. Ofis içi tüm istemciler kurumsal sertifikalı dizüstü bilgisayarlar ve kurumsal mobil cihazlardan oluşmaktadır.

---

## 2. Detaylı IP ve VLAN Tablosu

| VLAN ID | VLAN Adı | Güvenlik Bölgesi (Zone) | Ağ Adresi (CIDR) | Alt Ağ Maskesi | Varsayılan Ağ Geçidi (GW) | Kullanılabilir IP Aralığı | DHCP Dağıtım Havuzu | Statik Rezerve Alan (Cihaz / Sunucu) |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **210** | `VLAN_LON_CORP_USERS` | `Zone_LON_Trust` | `10.30.10.0/24` | `255.255.255.0` | `10.30.10.1` | `10.30.10.2 - 10.30.10.254` | `10.30.10.50 - 10.30.10.200` | `10.30.10.2 - 10.30.10.49` (Bloomberg Terminals, VC Unit) |
| **299** | `VLAN_LON_OOBM` | `Zone_LON_Mgmt` | `10.30.99.0/24` | `255.255.255.0` | `10.30.99.1` | `10.30.99.2 - 10.30.99.254` | *DHCP Kapalı* | `10.30.99.2 - 10.30.99.254` (Palo Alto PA-440, PoE Switch, AP) |

---

## 3. Alt Ağ Yapılandırma ve Servis Parametreleri

### VLAN 210 - Uluslararası Kurumsal Kullanıcılar (10.30.10.0/24)
* **Ağ Kimliği:** `10.30.10.0`
* **Yayın Adresi:** `10.30.10.255`
* **Varsayılan Ağ Geçidi:** `10.30.10.1` (Palo Alto PA-440 Arayüzü `ethernet1/2.210`)
* **Birincil DNS:** `10.10.100.10` (Ankara DC01 - Güvenli IPsec tüneli üzerinden)
* **İkincil DNS:** `1.1.1.1` (Cloudflare DoH / TLS Şifreli Genel DNS)
* **NTP Sunucusu:** `10.10.100.10` (Ankara NTP) & `uk.pool.ntp.org`
* **Doğrulama Mekanizması:** 802.1X EAP-TLS (Cisco ISE / Active Directory PKI sertifikası zorunlu). Cihazda geçerli sertifika yoksa port otomatik olarak kapatılır (`err-disable`).
* **IP Rezervasyonları:**
  - `10.30.10.10`: Canary Wharf Boardroom Cisco Webex Room Bar Pro
  - `10.30.10.11`: Londra Hukuk Konferans Terminali
  - `10.30.10.15`: Bloomberg Professional Dedicated Terminal 01
  - `10.30.10.16`: Bloomberg Professional Dedicated Terminal 02
  - `10.30.10.20`: Güvenli PIN Korumalı Kurumsal MFP Yazıcı (VDR çıktısı için)

### VLAN 299 - Out-of-Band Management (OOBM) (10.30.99.0/24)
* **Ağ Kimliği:** `10.30.99.0`
* **Varsayılan Ağ Geçidi:** `10.30.99.1`
* **Özellik:** Dış internete kapalıdır. Yalnızca Ankara BT Yönetim Jumpbox'ından gelen IPsec tüneli içi SSH/HTTPS oturumlarına cevap verir.
* **IP Rezervasyonları:**
  - `10.30.99.10`: Palo Alto PA-440 `MGT` Portu
  - `10.30.99.20`: Cisco Catalyst 1000 24-Port Gigabit Yönetilebilir Switch
  - `10.30.99.31 - 10.30.99.32`: Cisco Catalyst 9120AX Wi-Fi 6 AP'ler
  - `10.30.99.80`: APC Akıllı UPS Ağ Yönetim Kartı

# İstanbul Şubesi - IP Adresleme ve VLAN Segmentasyon Planı

## 1. Mimari Adresleme Stratejisi
İstanbul Şubesi, holding ağ mimarisinde kurumsal iç ağ için `10.20.0.0/16` süpernet bloğuna, misafir ve harici ziyaretçi erişimi için ise RFC 1918 `172.16.20.0/24` bloğuna yerleştirilmiştir. Bu ayrım, misafir trafiğinin kurumsal iç IP bloklarına yönlenmesini donanım seviyesinde önlemek ve firewall üzerinde rota izolasyonu (VRF veya policy-based routing) sağlamak amacıyla uygulanmıştır.

---

## 2. Detaylı IP ve VLAN Tablosu

| VLAN ID | VLAN Adı | Güvenlik Bölgesi (Zone) | Ağ Adresi (CIDR) | Alt Ağ Maskesi | Varsayılan Ağ Geçidi (GW) | Kullanılabilir IP Aralığı | DHCP Dağıtım Havuzu | Statik Rezerve Alan (Sunucu/Yazıcı/AP) |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **110** | `VLAN_IST_CORP_USERS` | `Zone_IST_Trust` | `10.20.10.0/24` | `255.255.255.0` | `10.20.10.1` | `10.20.10.2 - 10.20.10.254` | `10.20.10.50 - 10.20.10.220` | `10.20.10.2 - 10.20.10.49` (Ağ Yazıcıları, Konferans Üniteleri) |
| **120** | `VLAN_IST_GUEST_WIFI` | `Zone_IST_Guest` | `172.16.20.0/24` | `255.255.255.0` | `172.16.20.1` | `172.16.20.2 - 172.16.20.254` | `172.16.20.10 - 172.16.20.250` | *Yok (Tüm Misafirler Dinamik DHCP)* |
| **199** | `VLAN_IST_LOCAL_MGMT` | `Zone_IST_Mgmt` | `10.20.99.0/24` | `255.255.255.0` | `10.20.99.1` | `10.20.99.2 - 10.20.99.254` | *DHCP Kapalı* | `10.20.99.2 - 10.20.99.254` (FortiGate, FortiSwitch, FortiAP) |

---

## 3. Alt Ağ Yapılandırma ve Servis Parametreleri

### VLAN 110 - Ofis İçi Kurumsal Kullanıcılar (10.20.10.0/24)
* **Ağ Kimliği:** `10.20.10.0`
* **Varsayılan Ağ Geçidi:** `10.20.10.1` (FortiGate L3 Arayüzü `internal.110`)
* **Birincil DNS:** `10.10.100.10` (Ankara DC01 - IPsec Tüneli üzerinden kurumsal Active Directory DNS)
* **İkincil DNS:** `10.10.100.11` (Ankara DC02)
* **Kullanıcı Sayısı:** 150 Personel (DHCP havuzu 171 IP ile fazlasıyla yeterli)
* **Güvenlik Doğrulaması:** 802.1X WPA3-Enterprise (SSID: `HOLDING-CORP-IST`)
* **Statik Rezervasyonlar:**
  - `10.20.10.10`: Maslak Büyük Toplantı Odası Video Konferans Terminali
  - `10.20.10.15`: Satış Departmanı Çok Fonksiyonlu Ağ Yazıcısı
  - `10.20.10.16`: Pazarlama Departmanı Renkli Plotter/Yazıcı

### VLAN 120 - Misafir / Guest Ağı (172.16.20.0/24)
* **Ağ Kimliği:** `172.16.20.0`
* **Varsayılan Ağ Geçidi:** `172.16.20.1` (FortiGate L3 Arayüzü `internal.120`)
* **DNS Sunucuları:** `1.1.1.1` (Cloudflare), `8.8.8.8` (Google DNS)
  - *Not:* Misafir istemcilere kesinlikle Ankara kurumsal DC DNS'leri verilmez; doğrudan genel güvenli DNS dağıtılır.
* **Doğrulama ve Erişim:** Web Tabanlı Karşılama Sayfası (Captive Portal - SMS OTP ile 8 saatlik oturum izni).
* **İstemci İzolasyonu (Client Isolation):** FortiAP üzerinde `block-intra-ssid-traffic` aktif edilmiştir. Misafir cihazlar birbirlerinin IP'lerine paket gönderemez (Peer-to-Peer engeli).

### VLAN 199 - Lokal Ağ Ekipman Yönetimi (10.20.99.0/24)
* **Varsayılan Ağ Geçidi:** `10.20.99.1`
* **Rezervasyonlar:**
  - `10.20.99.10`: FortiGate 100F Management Arayüzü
  - `10.20.99.20`: FortiSwitch 248E-FPOE Omurga/Kenar Switch
  - `10.20.99.31 - 10.20.99.36`: FortiAP 431F Kablosuz Erişim Noktaları

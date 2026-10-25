# Ankara Genel Merkez - IP Adresleme ve VLAN Segmentasyon Planı

## 1. Mimari Adresleme Stratejisi
Ankara Genel Merkezi, holding ağ hiyerarşisinde `10.10.0.0/16` süpernet bloğuna tahsis edilmiştir. Bu sayede tüm alt ağlar (subnets) WAN omurgasında ve BGP yönlendirme tablolarında tek bir CIDR bloğu olarak özetlenebilir (`route summarization`).

Mikro-segmentasyon prensiplerine tam uyum sağlamak amacıyla kullanıcı departmanları, hassas finans sistemleri ve donanımsal yönetim arabirimleri farklı Layer 2 broadcast alanlarına (VLAN) ve Layer 3 güvenlik bölgelerine (Security Zone) ayrılmıştır.

---

## 2. Detaylı IP ve VLAN Tablosu

| VLAN ID | VLAN Adı | Güvenlik Bölgesi (Zone) | Ağ Adresi (CIDR) | Alt Ağ Maskesi | Varsayılan Ağ Geçidi (GW) | Kullanılabilir IP Aralığı | DHCP Dağıtım Havuzu | Statik Rezerve Alan (Sunucu/Yazıcı/Cihaz) |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **10** | `VLAN_HQ_MGMT_USERS` | `Trust_Executive` | `10.10.10.0/24` | `255.255.255.0` | `10.10.10.1` | `10.10.10.2 - 10.10.10.254` | `10.10.10.50 - 10.10.10.200` | `10.10.10.2 - 10.10.10.49` (VIP Konsollar, Telepresence) |
| **20** | `VLAN_HQ_FINANCE` | `Trust_Finance` | `10.10.20.0/24` | `255.255.255.0` | `10.10.20.1` | `10.10.20.2 - 10.10.20.254` | `10.10.20.50 - 10.10.20.200` | `10.10.20.2 - 10.10.20.49` (Hazine Terminali, SWIFT PC) |
| **30** | `VLAN_HQ_OPS_ADMIN` | `Trust_Corporate` | `10.10.30.0/24` | `255.255.255.0` | `10.10.30.1` | `10.10.30.2 - 10.10.30.254` | `10.10.30.50 - 10.10.30.220` | `10.10.30.221 - 10.10.30.254` (Ağ Yazıcıları, IP Kameralar) |
| **99** | `VLAN_HQ_OOBM` | `Zone_OOBM` | `10.10.99.0/24` | `255.255.255.0` | `10.10.99.1` | `10.10.99.2 - 10.10.99.254` | *DHCP Kapalı* | `10.10.99.2 - 10.10.99.254` (Switch/FW Mgmt, iDRAC, PDU) |

---

## 3. Altyapı Transit ve Yüksek Erişilebilirlik (HA) Blokları

Firewall kümeleri, Core Switch interconnect hatları ve şubeler arası SD-WAN bağlantıları için ayrılan altyapı blokları aşağıdadır:

| Segment Tanımı | Arabirim / Port | IP Bloğu (CIDR) | Cihaz A IP | Cihaz B IP | Açıklama |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Core Switch - NGFW Transit** | `LACP Port-Channel 1` | `10.10.50.0/29` | `10.10.50.1` (Core-VLAN50-SVI) | `10.10.50.2` (NGFW HA Active VIP) | L3 Transit Yönlendirme Ağı |
| **NGFW HA Kontrol (HA1)** | `Dedicated 1G RJ45` | `169.254.1.0/30` | `169.254.1.1/30` (FW-01 Mgmt/HA1) | `169.254.1.2/30` (FW-02 Mgmt/HA1) | Heartbeat, Konfigürasyon Senkronizasyonu |
| **NGFW HA Oturum Eşleme (HA2)**| `Dedicated 10G SFP+` | `169.254.2.0/30` | `169.254.2.1/30` (FW-01 HA2) | `169.254.2.2/30` (FW-02 HA2) | Stateful Tablo ve ARP Tablosu Eşleme |
| **Merkezi Sunucu Çiftliği (DC)**| `Nexus 9300 Trunk` | `10.10.100.0/24`| `10.10.100.1` (GW VIP) | `10.10.100.10` (AD DC1), `10.10.100.11` (AD DC2) | Kurumsal Active Directory, DNS, NTP, CA |

---

## 4. IP Tahsis Detayları ve Rezervasyon Tablosu

### VLAN 10 - Yönetim (10.10.10.0/24)
* **Ağ Kimliği (Network ID):** `10.10.10.0`
* **Yayın Adresi (Broadcast):** `10.10.10.255`
* **Varsayılan Ağ Geçidi:** `10.10.10.1` (Firewall L3 Alt-arabirim `ae1.10`)
* **DNS Sunucuları:** `10.10.100.10`, `10.10.100.11`
* **NTP Sunucusu:** `10.10.100.10`
* **IP Rezervasyonları:**
  - `10.10.10.10`: Yönetim Kurulu Odası Cisco Webex Room Kit Pro
  - `10.10.10.11`: CEO Ofisi Telepresence Terminali
  - `10.10.10.12`: Hukuk & C-Level VIP Güvenli MFP Yazıcı (802.1X Sertifikalı)

### VLAN 20 - Finans ve Hazine (10.10.20.0/24)
* **Ağ Kimliği (Network ID):** `10.10.20.0`
* **Yayın Adresi (Broadcast):** `10.10.20.255`
* **Varsayılan Ağ Geçidi:** `10.10.20.1` (Firewall L3 Alt-arabirim `ae1.20`)
* **Özel Güvenlik Kriteri:** Bu VLAN'daki tüm portlar 802.1X EAP-TLS sertifika tabanlı kimlik denetimine tabidir. Misafir veya bilinmeyen MAC adresleri anında Blackhole VLAN 999'a düşürülür.
* **IP Rezervasyonları:**
  - `10.10.20.10`: SWIFT Gateway Terminal 01 (Statik MAC-IP bağlama)
  - `10.10.20.11`: SWIFT Gateway Terminal 02 (Statik MAC-IP bağlama)
  - `10.10.20.15`: Bloomberg Professional Finansal Analiz Terminali
  - `10.10.20.20`: Finans Departmanı Güvenli Çek/Senet Yazıcısı (TLS Print)

### VLAN 30 - İdari İşler ve Operasyon (10.10.30.0/24)
* **Ağ Kimliği (Network ID):** `10.10.30.0`
* **Yayın Adresi (Broadcast):** `10.10.30.255`
* **Varsayılan Ağ Geçidi:** `10.10.30.1` (Firewall L3 Alt-arabirim `ae1.30`)
* **IP Rezervasyonları:**
  - `10.10.30.221 - 10.10.30.235`: Çok Fonksiyonlu Kurumsal Ağ Yazıcıları (Departman bazlı)
  - `10.10.30.240 - 10.10.30.254`: Kat Bilgi Ekranları ve Digital Signage Cihazları

### VLAN 99 - Out-of-Band Management (10.10.99.0/24)
* **Ağ Kimliği (Network ID):** `10.10.99.0`
* **Yayın Adresi (Broadcast):** `10.10.99.255`
* **Varsayılan Ağ Geçidi:** `10.10.99.1` (L3 Core Switch OOBM SVI / Dedicated OOBM Router)
* **Özellik:** Bu ağ kesinlikle internete çıkış yapamaz (No Default Route to WAN). Yalnızca BT yönetim jumpbox sunucusundan (Bastion Host) SSH/HTTPS ile erişilebilir.
* **IP Rezervasyonları:**
  - `10.10.99.10`: NGFW-01 Management Port
  - `10.10.99.11`: NGFW-02 Management Port
  - `10.10.99.20`: Core Switch 01 OOBM Portu (Cisco Catalyst 9500 Gi0/0)
  - `10.10.99.21`: Core Switch 02 OOBM Portu (Cisco Catalyst 9500 Gi0/0)
  - `10.10.99.31 - 10.10.99.45`: Erişim Kenar Switchleri OOBM Portları (Stack Master)
  - `10.10.99.50 - 10.10.99.70`: Sunucu iDRAC / iLO Donanımsal Yönetim Kartları
  - `10.10.99.80`: APC Akıllı PDU ve Kesintisiz Güç Kaynağı (UPS) Yönetim Kartı

# Ankara Genel Merkez - NGFW Kurulum ve Devreye Alma Rehberi

Bu belge, Ankara Genel Merkezinde konumlandırılan **Palo Alto Networks PA-3410 Active/Passive HA** kümesinin adım adım kurulum prosedürünü, fiziksel kablolamadan BGP yönlendirmesine, canlıya geçiş (cutover) ve geri alma (rollback) planına kadar eksiksiz olarak detaylandırır.

---

## 1. Fiziksel Montaj ve Out-of-Band Management (OOBM) Kurulumu

### 1.1. Kabinet ve Güç Bağlantısı
* Cihazlar (PA-3410-01 ve PA-3410-02), Merkez Sistem Odası Kabinet A01 ve Kabinet A02 içerisine 1U yüksekliğinde rack rayları ile monte edilir.
* Her bir cihazın yedekli güç kaynakları (PSU-1 ve PSU-2), bağımsız A ve B PDU hatlarına bağlanır (UPS A ve UPS B beslemesi).

### 1.2. OOBM ve Konsol Erişimi
* Her iki cihazın `MGT` portu, izole yönetim anahtarına (Cisco Catalyst 9200L - VLAN 99) Cat6A U/FTP kablo ile bağlanır.
* Statik Yönetim IP Tanımlamaları:
  - **PA-3410-01 (Birincil):** IP: `10.10.99.10/24`, GW: `10.10.99.1`, DNS: `10.10.100.10`
  - **PA-3410-02 (İkincil):** IP: `10.10.99.11/24`, GW: `10.10.99.1`, DNS: `10.10.100.10`
* Konsol kablosu (RJ45-to-DB9/USB) ile Opengear Konsol Sunucusuna (Port 1 ve Port 2) bağlantı sağlanır.

```text
# İlk CLI Konfigürasyonu (PA-3410-01):
set deviceconfig system ip-address 10.10.99.10 netmask 255.255.255.0 default-gateway 10.10.99.1 dns-setting servers primary 10.10.100.10
set deviceconfig system hostname HQ-NGFW-01
commit
```

---

## 2. Active/Passive High Availability (HA) Kümelemesi

### 2.1. Fiziksel HA Bağlantıları
* **HA1 (Control Link):** İki cihazın `HA1` portları doğrudan cross Cat6A kablo ile bağlanır (Keepalive, konfigürasyon eşitleme, SSH tüneli).
* **HA1 Backup:** Port `eth1/12` yönetim switchi üzerinden yedek HA1 kontrol linki olarak yapılandırılır.
* **HA2 (Data Link):** İki cihazın `HA2` (SFP+) portları 10G DAC kablo ile doğrudan birbirine bağlanır (State synchronization, ARP tablosu, oturum transferi).

### 2.2. HA Yapılandırma Parametreleri
* **Group ID:** `10`
* **Mode:** `Active-Passive`
* **HA1 IP PA-3410-01:** `169.254.1.1/30` | **HA1 IP PA-3410-02:** `169.254.1.2/30`
* **HA2 IP PA-3410-01:** `169.254.2.1/30` | **HA2 IP PA-3410-02:** `169.254.2.2/30`
* **Election Parameters:**
  - Device Priority: PA-3410-01 = `90` (Öncelikli Active), PA-3410-02 = `100` (Passive).
  - Preemptive: `Disabled` (Trafiğin gereksiz yere geri dönerek mikro kesinti yaşatmasını önlemek için devre dışı bırakılır).
  - Heartbeat Interval: `1000 ms`, Threshold: `3` kayıp kalp atışı (3 saniye failover süresi).

---

## 3. LACP Trunk ve Core Switch Bağlantısı (802.3ad)

NGFW ile Omurga Anahtarları (Cisco Catalyst 9500 StackWise-Virtual) arasında fiziksel hat yedekliliği ve agregasyon için IEEE 802.3ad LACP Port-Channel oluşturulur.

### 3.1. Port Haritası
* `eth1/5` (PA-3410) -> Core-SW-01 Port `Te1/0/1` (10G Fiber)
* `eth1/6` (PA-3410) -> Core-SW-02 Port `Te2/0/1` (10G Fiber)
* Bu iki port `ae1` (Aggregate Ethernet 1) mantıksal arabiriminde birleştirilir.

### 3.2. Alt-Arabirim (Sub-Interface) ve 802.1Q Tag Konfigürasyonu

| Mantıksal Port | VLAN Tag | IP Adresi / CIDR | Güvenlik Bölgesi (Zone) |
| :--- | :---: | :--- | :--- |
| `ae1.10` | 10 | `10.10.10.1/24` | `Trust_Executive` |
| `ae1.20` | 20 | `10.10.20.1/24` | `Trust_Finance` |
| `ae1.30` | 30 | `10.10.30.1/24` | `Trust_Corporate` |
| `ae1.50` | 50 | `10.10.50.2/29` | `Transit_Core_L3` |

---

## 4. BGP/OSPF Yönlendirme ve SD-WAN Konfigürasyonu

### 4.1. Dinamik Yönlendirme Mimarisi (BGP & OSPF)
* **İç Ağ (LAN/OSPF):** Core switch ile NGFW arasında OSPFv2 Area 0 yapılandırılır.
  - Core Switch Router-ID: `10.10.50.1`, NGFW Router-ID: `10.10.50.2`
  - Ağ: `10.10.50.0/29` (Point-to-Point network type, Hello: 10s, Dead: 40s).
* **Dış Ağ (WAN/eBGP):** Çift ISP ile eBGP peering kurulur.
  - Ankara HQ Otonom Sistem Numarası (ASN): `AS64512` (Private BGP AS).
  - ISP-A (Türk Telekom) Peer: `195.175.10.1` (AS9121). Local: `195.175.10.2/30`.
  - ISP-B (Turkcell Superonline) Peer: `212.58.20.1` (AS34984). Local: `212.58.20.2/30`.
  - BGP Attributes: ISP-A üzerinden Local Preference `200`, ISP-B üzerinden Local Preference `100` (Primary/Backup ya da Multi-Homing).

### 4.2. SD-WAN Hub Yapılandırması
* İstanbul, Londra ve Kampüs şubelerinden gelen IPsec tüneller `Tunnel.1` (SD-WAN Interface) üzerinde sonlandırılır.
* Canlı paket ölçüm mekanizması (Probing: HTTP Ping her 1000ms'de bir 8.8.8.8 ve HQ DNS'e) ile hat kalitesi anlık izlenir.

---

## 5. Canlıya Geçiş (Cutover) ve Geri Alma (Rollback) Planı

### 5.1. Canlıya Geçiş Aşamaları (Cutover Checklist)
* **Zaman Penceresi:** Cumartesi 02:00 - 05:00 (İşlem Dışı Bakım Saati)
* **Adım 1 (02:00 - 02:20):** Fiziksel ve L1/L2 link doğrulama (LACP status `bundled`, HA linkleri `sync`).
* **Adım 2 (02:20 - 02:45):** BGP ve OSPF komşuluklarının ayağa kaldırılması, yönlendirme tablolarının doğrulanması.
* **Adım 3 (02:45 - 03:30):** Varsayılan ağ geçitlerinin Core Switch SVI'larından NGFW sub-interface'lerine aktarılması (Default gateway migration).
* **Adım 4 (03:30 - 04:15):** UAT (Kullanıcı Kabul Testi) senaryolarının çalıştırılması:
  - Finans VLAN 20 -> SAP Sunucuları (TCP 3300/443) erişim testi.
  - VoIP santral ve video konferans ses kalitesi (MOS skoru $\ge 4.2$).
  - İstanbul ve Londra şube IPsec VPN erişim kontrolü.
* **Adım 5 (04:15 - 04:30):** Panorama senkronizasyonu ve log akışının SIEM'e teyidi.

### 5.2. Geri Alma (Rollback) Kriterleri ve Prosedürü
* **Rollback Tetikleyicileri:**
  1. Çekirdek finans sistemlerine (SAP/SWIFT) bağlantının 04:00 itibarıyla sağlanamaması.
  2. BGP rotalarında flapping (sürekli düşüp kalkma) oluşması ve ISP erişiminin kesilmesi.
  3. HA kümesinde Split-Brain durumu tespit edilmesi.
* **Rollback Eylemleri:**
  1. Core Switch üzerindeki eski statik rota ve SVI yapılandırmasına geri dönülür (`copy flash:backup-config.cfg running-config`).
  2. NGFW LACP portları geçici olarak `shutdown` edilir.
  3. Trafik eski omurga yönlendiricilerine aktarılır (Süre: Azami 12 dakika).

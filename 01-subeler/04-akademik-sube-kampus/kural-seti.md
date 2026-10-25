# Akademik Şube ve Kampüs - Güvenlik Duvarı Kural Seti ve İzolasyon Matrisi

Bu belge, Kampüs FortiGate 1800F güvenlik duvarı kümesinde uygulanan kural setini içerir. Öğrenci ağının idari ve akademik sistemlerden mutlak izolasyonu, P2P/Torrent engellemeleri ve DNS tünelleme koruması üretim kurallarıyla yapılandırılmıştır.

---

## 1. Güvenlik Bölgeleri (Zones) ve Arabirimler
* `Zone_Campus_Student`: VLAN 300-305 Öğrenci Wi-Fi & Eduroam (`10.100.0.0/16`)
* `Zone_Campus_Academic`: VLAN 310 Akademik Personel (`10.101.10.0/24`)
* `Zone_Campus_Admin`: VLAN 320 İdari İşler & ÖBS (`10.101.20.0/24`)
* `Zone_Campus_DC_LMS`: VLAN 330 Kampüs LMS Sunucuları & Kütüphane (`10.101.30.0/24`)
* `Zone_Campus_OOBM`: VLAN 399 Lokal Ekipman Yönetimi (`10.101.99.0/24`)
* `WAN_ULAKBIM`: 10G Ulusal Akademik Ağ
* `WAN_Commercial`: 10G Türk Telekom Ticari İnternet

---

## 2. Üretim Kural Seti Tablosu

| Rule ID | Kural Adı | Kaynak Bölge | Kaynak IP/CIDR | Hedef Bölge | Hedef IP/CIDR | Servis / Port | Eylem (Action) | Loglama | Güvenlik Profili (Security Profiles) |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **CMP-01** | `BLOCK_P2P_TORRENT_TOR` | `Zone_Campus_Student` | `10.100.0.0/16` | `any` | `any` | `any` | **DENY** | UTM Log | AppControl-Block (BitTorrent, eMule, Tor, I2P, Ultrasurf, Psiphon) |
| **CMP-02** | `BLOCK_DNS_TUNNELING` | `Zone_Campus_Student` | `10.100.0.0/16` | `any` | `any` | UDP/53, TCP/53 | **DENY** | Alert / Log | DNS-Filter-Strict (DNS Tunneling, DGA Domains, Botnet C2 Block) |
| **CMP-03** | `STUDENT_TO_INTERNAL_DROP`| `Zone_Campus_Student`| `10.100.0.0/16` | `Zone_Campus_Admin`, `Zone_Campus_OOBM` | `10.101.20.0/24`, `10.101.99.0/24`, `10.10.0.0/16` | `any` | **DENY** | Alert / Log | Strict-Campus-Isolation (Öğrenci ağı idari ağa kesinlikle erişemez) |
| **CMP-04** | `STUDENT_TO_LMS_WEB_ONLY`| `Zone_Campus_Student`| `10.100.0.0/16` | `Zone_Campus_DC_LMS`| `10.101.30.20`, `10.101.30.21` (LMS Web) | TCP/80, TCP/443 | **ACCEPT** | Session Close | WAF-Profile-LMS, IPS-Default, Rate-Limit (100 req/min) |
| **CMP-05** | `STUDENT_TO_LMS_DB_DROP` | `Zone_Campus_Student`| `10.100.0.0/16` | `Zone_Campus_DC_LMS`| `10.101.30.25` (DB VIP), `10.101.30.30` (ÖBS DB) | TCP/5432, TCP/3306, TCP/1521 | **DENY** | Alert / Log | Critical-DB-Breach-Alert (Öğrenci doğrudan DB'ye gidemez) |
| **CMP-06** | `STUDENT_INTERNET_ACCESS` | `Zone_Campus_Student`| `10.100.0.0/16` | `WAN_Commercial` | `any` | TCP/80, TCP/443 | **ACCEPT** | Session Close | WebFilter-Edu (Adult/Illegal/Gambling Drop), AV-Scan, Traffic-Shaper (10M Cap) |
| **CMP-07** | `ACADEMIC_TO_ULAKBIM_RES`| `Zone_Campus_Academic`| `10.101.10.0/24` | `WAN_ULAKBIM` | Bilimsel Kaynaklar (IEEE, ScienceDirect) | TCP/80, TCP/443 | **ACCEPT** | Session Close | High-QoS-AF21, Threat-Protection-Standard |
| **CMP-08** | `ACADEMIC_TO_LMS_ADMIN` | `Zone_Campus_Academic`| `10.101.10.0/24` | `Zone_Campus_DC_LMS`| `10.101.30.20`, `10.101.30.21` | TCP/443, TCP/22 (Öğretim Üyesi SSH) | **ACCEPT** | Session Start & End | MFA-Enforced, IPS-Strict |
| **CMP-09** | `ADMIN_OBS_ACCESS` | `Zone_Campus_Admin` | `10.101.20.0/24` | `Zone_Campus_DC_LMS`| `10.101.30.30` (ÖBS Core) | TCP/443, TCP/1521 | **ACCEPT** | Session Close | DLP-Student-Records (KVKK/PII Koruması), IPS-Strict |
| **CMP-10** | `ADMIN_OUT_SECURE_WEB` | `Zone_Campus_Admin` | `10.101.20.0/24` | `WAN_Commercial` | `any` | TCP/80, TCP/443 | **ACCEPT** | UTM Log | Deep-SSL-Inspection, AV-Enterprise, Category-Block |
| **CMP-11** | `EDUROAM_RADIUS_AUTH` | `Zone_Campus_Student`, `Zone_Campus_Academic` | `10.100.0.0/16`, `10.101.10.0/24` | `Zone_Campus_DC_LMS` | `10.101.30.50` (FreeRADIUS) | UDP/1812, UDP/1813 | **ACCEPT** | No Log (High Vol) | Trusted-Radius-Profile |
| **CMP-12** | `CAMPUS_OOBM_RESTRICT` | `any` | `any` | `Zone_Campus_OOBM` | `10.101.99.0/24` | `any` | **DENY** | Alert / Log | Mgmt-Attack-Alert (Sadece Ankara Bastion IP'sine izin verilir) |
| **CMP-99** | `CAMPUS_DEFAULT_DROP` | `any` | `any` | `any` | `any` | `any` | **DENY** | All Dropped | Syslog to SIEM (Splunk/Elastic TLS 6514) |

---

## 3. Özel Güvenlik ve İzolasyon Mekanizmaları

### 3.1. P2P, BitTorrent ve Telif Hakkı İhlali Engelleme (CMP-01)
Öğrencilerin yasa dışı dosya paylaşımı yapmasını ve üniversite IP bloklarının kara listeye (Blacklist/DMCA Notice) girmesini engellemek için FortiGate üzerinde L7 derin paket inceleme (DPI) ile BitTorrent şifreli el sıkışmaları, DHT (Distributed Hash Table) sorguları ve Tracker iletişimleri porttan bağımsız olarak drop edilir.

### 3.2. DNS Tünelleme ve Veri Kaçırma Koruması (CMP-02)
Öğrenci cihazlarının captive portal veya kural kısıtlamalarını aşmak için kullandığı `iodine`, `dnscat2` gibi DNS tünelleme araçları, paket boyutu, entropi analizi ve sorgu frekansı denetimiyle anında tespit edilip engellenir.

### 3.3. LMS Veri Tabanı Katı İzolasyonu (CMP-05)
LMS web sunucuları DMZ mantığında çalışır. Öğrenci veya dış kullanıcılar yalnızca HTTP/HTTPS portundan web ön yüzüne ulaşabilir. Veri tabanı sunucularının yer aldığı backend portlarına (PostgreSQL TCP 5432) öğrenci ağından gelen tüm istekler anında loglanarak engellenir.

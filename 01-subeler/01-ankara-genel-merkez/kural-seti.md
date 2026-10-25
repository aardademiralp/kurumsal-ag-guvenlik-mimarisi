# Ankara Genel Merkez - Güvenlik Duvarı Kural Seti ve Mikro-Segmentasyon Matrisi

Bu belge, Ankara Genel Merkez Palo Alto PA-3410 güvenlik duvarı kümesinde uygulanan üretim seviyesi (production-grade) kural setidir. Güvenlik politikası **"Default-Deny" (Varsayılan Olarak Engelle)** ve **"Zero-Trust Least Privilege" (En Az Ayrıcalık)** ilkelerine sıkı sıkıya bağlıdır.

---

## 1. Güvenlik Bölgeleri (Zones)
* `Trust_Executive`: VLAN 10 (Yönetim Kurulu & C-Level)
* `Trust_Finance`: VLAN 20 (Finans, Muhasebe ve Hazine)
* `Trust_Corporate`: VLAN 30 (Operasyon, İK, İdari İşler)
* `Zone_OOBM`: VLAN 99 (Donanımsal Yönetim Arabirimleri)
* `Zone_DC_Services`: VLAN 100 (Kurumsal Active Directory, DNS, NTP, Sertifika Otoritesi)
* `Zone_ERP_HANA`: VLAN 105 (SAP S/4HANA Uygulama ve Veritabanı Kümesi)
* `Untrust_WAN`: Dış Dünya / İnternet (ISP-A & ISP-B)

---

## 2. Üretim Kural Seti Tablosu

| Rule ID | Kural Adı | Kaynak Bölge (Src Zone) | Kaynak IP/CIDR | Hedef Bölge (Dst Zone) | Hedef IP/CIDR | Servis / Port | Uygulama (App-ID) | Eylem (Action) | Loglama | Güvenlik Profili (Security Profiles) |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **R-101** | `CORE_INFRA_DNS_NTP` | `Trust_Executive`, `Trust_Finance`, `Trust_Corporate` | `10.10.10.0/24`, `10.10.20.0/24`, `10.10.30.0/24` | `Zone_DC_Services` | `10.10.100.10`, `10.10.100.11` | UDP/53, TCP/53, UDP/123 | `dns`, `ntp` | **ALLOW** | Session End | DNS-Security-Strict, Default-AV |
| **R-102** | `AD_AUTH_KERBEROS` | `Trust_Executive`, `Trust_Finance`, `Trust_Corporate` | `10.10.10.0/24`, `10.10.20.0/24`, `10.10.30.0/24` | `Zone_DC_Services` | `10.10.100.10`, `10.10.100.11` | TCP/88, UDP/88, TCP/389, TCP/636, TCP/3268, TCP/445 | `kerberos`, `ldap`, `ms-ds-smb` | **ALLOW** | Session End | Vuln-Protect-Strict, Anti-Spyware |
| **R-103** | `FIN_TO_SWIFT_NET` | `Trust_Finance` | `10.10.20.10`, `10.10.20.11` (SWIFT PC) | `Untrust_WAN` | `194.107.240.0/24` (SWIFT Alliance Gateway) | TCP/443, TCP/10000 | `swift`, `ssl` | **ALLOW** | Session Start & End | SSL-Inbound-Inspect, Anti-Spyware-Strict, Custom-IPsec |
| **R-104** | `FIN_TO_SAP_ERP` | `Trust_Finance` | `10.10.20.0/24` | `Zone_ERP_HANA` | `10.10.105.10` - `10.10.105.20` | TCP/3200-3299, TCP/3300-3399, TCP/443, TCP/30015 | `sap`, `sap-fiori`, `ssl` | **ALLOW** | Session End | Financial-DLP-Strict, Vuln-Protect, File-Blocking |
| **R-105** | `FIN_BANK_APIS_OUT` | `Trust_Finance` | `10.10.20.0/24` | `Untrust_WAN` | Banka API IP Grupları (BKM/TCMB) | TCP/443 | `ssl` (Mutual TLS / mTLS) | **ALLOW** | Session End | Enterprise-DLP, Anti-Spyware, SSL-Decryption-Bypass (mTLS) |
| **R-106** | `FIN_DIRECT_INET_DROP`| `Trust_Finance` | `10.10.20.0/24` | `Untrust_WAN` | `any` | `any` | `any` | **DROP** | Alert / Log | Log-Finance-Violation (SIEM Alarm) |
| **R-107** | `EXEC_OUT_SECURE_WEB` | `Trust_Executive` | `10.10.10.0/24` | `Untrust_WAN` | `any` | TCP/80, TCP/443 | `web-browsing`, `ssl` | **ALLOW** | Session End | SSL-Forward-Proxy (Decryption), AV-Strict, URL-Filtering (Strict-Corp), WildFire |
| **R-108** | `EXEC_TO_SAP_REPORT` | `Trust_Executive` | `10.10.10.0/24` | `Zone_ERP_HANA` | `10.10.105.15` (Analytics Core) | TCP/443 | `sap-fiori`, `ssl` | **ALLOW** | Session End | Threat-Prev-Default, Financial-DLP-Monitor |
| **R-109** | `OPS_TO_ERP_AND_EBYS`| `Trust_Corporate` | `10.10.30.0/24` | `Zone_ERP_HANA` | `10.10.105.10` - `10.10.105.14` | TCP/3200, TCP/443 | `sap-gui`, `ssl` | **ALLOW** | Session End | Threat-Prev-Default, File-Blocking (Exe/VBS Drop) |
| **R-110** | `OPS_OUT_WEB_PROXY` | `Trust_Corporate` | `10.10.30.0/24` | `Untrust_WAN` | `any` | TCP/80, TCP/443 | `web-browsing`, `ssl`, `ms-office365` | **ALLOW** | Session End | URL-Filtering (Category-Block: Gambling, Weapons, P2P), AV-Default |
| **R-111** | `VOIP_TEAMS_ZOOM` | `Trust_Executive`, `Trust_Corporate` | `10.10.10.0/24`, `10.10.30.0/24` | `Untrust_WAN` | MS Teams / Zoom IP Ranges | UDP/5060, UDP/5061, UDP/3478-3481, UDP/16384-32767 | `ms-teams`, `zoom`, `sip`, `rtp` | **ALLOW** | Session End | QoS-EF-Marking (DSCP 46), Bypass-Decryption |
| **R-112** | `INTER_VLAN_LATERAL_DROP`| `Trust_Executive`, `Trust_Finance`, `Trust_Corporate` | `10.10.0.0/16` | `Trust_Executive`, `Trust_Finance`, `Trust_Corporate` | `10.10.0.0/16` | `any` | `any` | **DROP** | Alert / Log | Lateral-Movement-Alarm (Departmanlar arası doğrudan iletişim yasaktır) |
| **R-113** | `OOBM_BASTION_ACCESS`| `Trust_Corporate` | `10.10.30.5` (BT Bastion Host) | `Zone_OOBM` | `10.10.99.0/24` | TCP/22, TCP/443 | `ssh`, `ssl` | **ALLOW** | Session Start & End | MFA-Enforced-Rule, Vuln-Protect-Strict |
| **R-114** | `OOBM_OUTBOUND_DROP` | `Zone_OOBM` | `10.10.99.0/24` | `Untrust_WAN`, `any` | `any` | `any` | `any` | **DROP** | Alert / Log | Critical-Security-Event (OOBM dışarı çıkamaz) |
| **R-999** | `EXPLICIT_DENY_ALL` | `any` | `any` | `any` | `any` | `any` | `any` | **DROP** | Session Start & End | Log-All-Drops (SIEM Syslog Forwarding) |

---

## 3. Mikro-Segmentasyon ve Güvenlik Profilleri Detayları

1. **Finans İzolasyon Politikası (R-106):**
   * Finans ağı (`10.10.20.0/24`) içerisindeki hiçbir cihaz, genel internet sitelerine doğrudan erişemez.
   * Yalnızca önceden IP/FQDN bazında onaylanmış bankacılık API'leri ve SWIFT ağına izin verilir.
   * İnternet bankacılığı teftişi için SSL Decryption Bypass uygulanır (Banka mTLS sertifika zincirini bozmamak adına).

2. **Yanal İlerleme (Lateral Movement) Engeli (R-112):**
   * Şirket içi kullanıcı VLAN'larının (VLAN 10, VLAN 20, VLAN 30) birbirleri arasında L4/L7 konuşması Palo Alto üzerinde doğrudan engellenir.
   * Dosya paylaşımı gereken durumlarda istemciler birbirine bağlanamaz; doğrudan kurumsal SharePoint/OneDrive veya merkezi izole dosya sunucusu kullanılır.

3. **Veri Sızıntısı Önleme (Financial-DLP-Strict):**
   * Kredi kartı formatları (Luhn algoritması kontrolü), IBAN numaraları ve T.C. Kimlik No regex paternleri paket yükünde tespit edildiğinde oturum anında kesilir (`reset-both`) ve Güvenlik Operasyon Merkezine (SOC) P1 alarmı üretilir.

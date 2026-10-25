# İstanbul Şubesi - Güvenlik Duvarı Kural Seti ve Erişim Politikaları

Bu belge, İstanbul Şubesi FortiGate 100F güvenlik duvarı üzerinde uygulanan tam kural kümesini içerir. Kurallar misafir ağının mutlak izolasyonunu, kurumsal kullanıcıların doğrudan SaaS çıkışını ve merkez intranet bağlantılarını regüle eder.

---

## 1. Güvenlik Bölgeleri (Zones) ve Arabirimler
* `Zone_IST_Trust`: VLAN 110 Kurumsal Çalışanlar (`10.20.10.0/24`)
* `Zone_IST_Guest`: VLAN 120 Misafir / Ziyaretçi Ağı (`172.16.20.0/24`)
* `Zone_IST_Mgmt`: VLAN 199 Lokal Ekipman Yönetimi (`10.20.99.0/24`)
* `SDWAN_Internet`: wan1 (Birincil Türk Telekom) & wan2 (Yedek Vodafone)
* `Tunnel_Ankara`: Ankara Genel Merkezine giden IPsec VPN Tüneli

---

## 2. Üretim Kural Seti Tablosu

| Rule ID | Kural Adı | Kaynak Bölge | Kaynak IP/CIDR | Hedef Bölge | Hedef IP/CIDR | Servis / Port | Eylem (Action) | NAT Durumu | Loglama | Güvenlik Profilleri (UTM/DPI) |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **IST-01** | `GUEST_DNS_DHCP` | `Zone_IST_Guest` | `172.16.20.0/24` | `SDWAN_Internet` | `1.1.1.1`, `8.8.8.8` | UDP/53 (DNS), UDP/67-68 (DHCP) | **ACCEPT** | SNAT (Egress Interface) | All Sessions | DNS-Filter-Guest (Botnet/Adult Drop) |
| **IST-02** | `GUEST_HTTP_HTTPS_OUT`| `Zone_IST_Guest` | `172.16.20.0/24` | `SDWAN_Internet` | `any` | TCP/80, TCP/443 | **ACCEPT** | SNAT (Egress Interface) | UTM Log | WebFilter-Guest (Adult/P2P/Malware Drop), AV-Scan |
| **IST-03** | `GUEST_ISOLATION_DROP`| `Zone_IST_Guest` | `172.16.20.0/24` | `Zone_IST_Trust`, `Zone_IST_Mgmt`, `Tunnel_Ankara` | `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` | `any` | **DENY** | No NAT | Generate Alarm | Guest-Breach-Alert (İç ağa sızma girişimi) |
| **IST-04** | `CORP_TO_HQ_INFRA` | `Zone_IST_Trust` | `10.20.10.0/24` | `Tunnel_Ankara` | `10.10.100.10`, `10.10.100.11` (AD/DNS) | UDP/53, TCP/88, TCP/389, TCP/445, UDP/123 | **ACCEPT** | No NAT | Session Close | IPS-Default, Anti-Virus-Enterprise |
| **IST-05** | `CORP_TO_HQ_ERP` | `Zone_IST_Trust` | `10.20.10.0/24` | `Tunnel_Ankara` | `10.10.105.10` - `10.10.105.20` (SAP HANA) | TCP/3200, TCP/3300, TCP/443 | **ACCEPT** | No NAT | Session Close | IPS-High-Priority, DLP-Sensor (Financial/Customer) |
| **IST-06** | `CORP_TO_HQ_RESTRICT`| `Zone_IST_Trust` | `10.20.10.0/24` | `Tunnel_Ankara` | `10.10.10.0/24` (Yönetim), `10.10.20.0/24` (Hazine) | `any` | **DENY** | No NAT | Generate Alarm | Strict-Segmentation-Drop (Merkez hassas ağlara erişim yasak) |
| **IST-07** | `CORP_M365_DIA_OUT` | `Zone_IST_Trust` | `10.20.10.0/24` | `SDWAN_Internet` | ISDB: `Microsoft-Office365`, `Teams` | TCP/80, TCP/443, UDP/3478-3481 | **ACCEPT** | SNAT (Egress Interface) | Session Close | SSL-Inspection-Bypass (M365 Optimize), QoS AF41 |
| **IST-08** | `CORP_SAAS_WEB_OUT` | `Zone_IST_Trust` | `10.20.10.0/24` | `SDWAN_Internet` | `any` | TCP/80, TCP/443 | **ACCEPT** | SNAT (Egress Interface) | UTM Log | Deep-SSL-Inspection, AV-Default, WebFilter-Corp, FileFilter |
| **IST-09** | `CORP_VOIP_ZOOM_OUT` | `Zone_IST_Trust` | `10.20.10.0/24` | `SDWAN_Internet` | Zoom / Webex IP Listesi | UDP/5060, UDP/5061, UDP/16384-32767 | **ACCEPT** | SNAT (Egress Interface) | Session Close | QoS-EF-Marking (DSCP 46) |
| **IST-10** | `MGMT_ACCESS_FROM_HQ` | `Tunnel_Ankara` | `10.10.30.5` (Ankara BT Bastion) | `Zone_IST_Mgmt` | `10.20.99.0/24` | TCP/22, TCP/443 | **ACCEPT** | No NAT | Session Start/End | Admin-Auth-Log, IPS-Strict |
| **IST-11** | `MGMT_OUTBOUND_DROP` | `Zone_IST_Mgmt` | `10.20.99.0/24` | `any` | `any` | `any` | **DENY** | No NAT | Alert | Management-Isolation-Violation |
| **IST-99** | `DEFAULT_DENY_ALL` | `any` | `any` | `any` | `any` | `any` | **DENY** | No NAT | All Dropped | Syslog to Splunk/Elastic (Port 6514) |

---

## 3. Kural Güvenlik Politikası Açıklamaları

1. **Misafir Ağı İzolasyon Garantisi (IST-03):**
   * Misafir VLAN'ından (`172.16.20.0/24`) gelen hiçbir paket RFC 1918 özel kurumsal adreslerine (`10.0.0.0/8`) geçemez. FortiGate üzerinde bu kural, genel web erişim kurallarının önüne konularak donanımsal filtreleme sağlanmıştır.
2. **Merkez İntranet Kısıtlamaları (IST-06):**
   * İstanbul şubesi kullanıcıları Ankara Genel Merkezindeki sadece kendi görev tanımlarına uygun sunuculara (SAP CRM/SD modülleri ve Active Directory) erişebilir. Ankara Yönetim (`10.10.10.0/24`) ve Finans/Hazine (`10.10.20.0/24`) ağlarına İstanbul'dan gelen tüm oturumlar anında `DENY` edilir.
3. **M365 Direct Internet Access Optimizasyonu (IST-07):**
   * Microsoft'un resmi ağ rehberine uygun olarak, Teams ve Exchange Online uç noktaları FortiGate ISDB (Internet Service Database) üzerinden algılanır; bu paketlerde gecikmeyi önlemek için SSL Decryption Bypass uygulanır ve bant genişliği QoS motoru ile önceliklendirilir (DSCP AF41).

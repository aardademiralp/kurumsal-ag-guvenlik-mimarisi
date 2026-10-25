# Londra Şubesi - Güvenlik Duvarı Kural Seti, Geo-IP ve ZTNA Politikaları

Bu belge, Londra Şubesi Palo Alto Networks PA-440 güvenlik duvarı üzerinde uygulanan sıkı güvenlik kurallarını, Geo-IP coğrafi konum kısıtlamalarını ve ZTNA sıfır güven erişim politikalarını içerir.

---

## 1. Güvenlik Bölgeleri (Zones) ve Nesneler
* `Zone_LON_Trust`: VLAN 210 Kurumsal Çalışanlar (`10.30.10.0/24`)
* `Zone_LON_Mgmt`: VLAN 299 Lokal Ekipman Yönetimi (`10.30.99.0/24`)
* `Untrust_Internet`: Birleşik Krallık Colt DIA İnternet Hattı
* `Tunnel_To_Ankara`: Ankara Hub IPsec VPN Tüneli
* **Özel Dinamik Adres Nesnesi:** `Geo-Allowed-Countries` = [ `United-Kingdom (GB)`, `Turkey (TR)` ]

---

## 2. Üretim Kural Seti Tablosu

| Rule ID | Kural Adı | Kaynak Bölge | Kaynak IP/Ülke | Hedef Bölge | Hedef IP/Ülke | Servis / Port | Uygulama (App-ID) | Eylem (Action) | Loglama | Güvenlik Profili / ZTNA Koşulu |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **LON-01** | `GEO_IP_BLOCK_NON_UK_TR`| `any` | Non-UK / Non-TR Ülkeler | `any` | `any` | `any` | `any` | **DROP** | Alert / Log | Geo-IP-Violation-Alarm (UK ve TR dışındaki tüm trafik anında engellenir) |
| **LON-02** | `ZTNA_POSTURE_CHECK_INFRA`| `Zone_LON_Trust` | `10.30.10.0/24` (Tag: `Posture_Compliant`) | `Tunnel_To_Ankara` | `10.10.100.10`, `10.10.100.11` (AD/DNS) | UDP/53, TCP/88, TCP/389, TCP/445 | `dns`, `kerberos`, `ldap`, `ms-ds-smb` | **ALLOW** | Session End | Device-Posture: EDR-Active + BitLocker-Encrypted |
| **LON-03** | `ZTNA_VIP_TO_ANK_SAP` | `Zone_LON_Trust` | `10.30.10.0/24` (Tag: `ZTNA_Finance_Legal`) | `Tunnel_To_Ankara` | `10.10.105.10` - `10.10.105.20` (SAP HANA) | TCP/3200, TCP/443 | `sap-gui`, `sap-fiori`, `ssl` | **ALLOW** | Session Start & End | HIP-Check: OS-Up-to-Date, Strict-DLP-Sensor |
| **LON-04** | `BLOOMBERG_DATA_FEED` | `Zone_LON_Trust` | `10.30.10.15`, `10.30.10.16` | `Untrust_Internet` | Bloomberg B-PIPE / Server IPs (UK) | TCP/8194-8198, TCP/443 | `bloomberg`, `ssl` | **ALLOW** | Session End | High-Priority-QoS, Anti-Spyware-Strict |
| **LON-05** | `CORP_SECURE_WEB_UK` | `Zone_LON_Trust` | `10.30.10.0/24` | `Untrust_Internet` | UK Web Siteleri (`Geo-GB`) | TCP/80, TCP/443 | `web-browsing`, `ssl` | **ALLOW** | Session End | SSL-Forward-Proxy (Decryption), AV-Strict, URL-Filtering |
| **LON-06** | `M365_TEAMS_COLLAB` | `Zone_LON_Trust` | `10.30.10.0/24` | `Untrust_Internet` | Microsoft 365 Cloud (UK Datacenters) | TCP/80, TCP/443, UDP/3478-3481 | `ms-office365`, `ms-teams`, `zoom` | **ALLOW** | Session End | Decryption-Bypass, QoS-AF41 Marking |
| **LON-07** | `MGMT_ACCESS_HQ_ONLY` | `Tunnel_To_Ankara` | `10.10.30.5` (Ankara BT Jumpbox) | `Zone_LON_Mgmt` | `10.30.99.0/24` | TCP/22, TCP/443 | `ssh`, `ssl` | **ALLOW** | Session Start & End | MFA-Required, Vuln-Protect-Strict |
| **LON-08** | `MGMT_OUTBOUND_DENY` | `Zone_LON_Mgmt` | `10.30.99.0/24` | `any` | `any` | `any` | `any` | **DROP** | Alert / Log | Mgmt-Leak-Alarm |
| **LON-99** | `DEFAULT_EXPLICIT_DENY`| `any` | `any` | `any` | `any` | `any` | `any` | **DROP** | Session Start & End | SIEM Syslog Forward (TLS 6514) |

---

## 3. Coğrafi Konum (Geo-IP) Filtreleme ve ZTNA HIP Politikası Detayları

### 3.1. Katı Geo-IP Filtreleme Mantığı (LON-01)
Londra şubesindeki PA-440 cihazında kural zincirinin en üstünde (Rule 1) Geo-IP engelleme yer alır:
* Kaynak veya Hedef IP adresi **United Kingdom (`GB`)** veya **Turkey (`TR`)** veri tabanına kayıtlı değilse, paket hiçbir teftiş aşamasına girmeden doğrudan donanım seviyesinde (`Hardware Packet Buffer Drop`) imha edilir.
* Bu kural; Rusya, Çin, İran, Kuzey Kore veya diğer yüksek riskli coğrafyalardan gelen tünel tarama, brute-force veya botnet aktivitelerini %99.8 oranında sınırlar.

### 3.2. Sıfır Güven (ZTNA) Host Information Profile (HIP) Kontrolü
Kullanıcıların Ankara merkezdeki SAP ERP ve Hukuk veri tabanlarına erişebilmesi için Palo Alto Cortex XDR / GlobalProtect HIP kontrolünden tam not alması şarttır:
1. **EDR Durumu:** Cortex XDR ajanının servisleri çalışır durumda ve son 24 saat içinde güncellenmiş olmalıdır.
2. **Disk Şifreleme:** Apple FileVault veya Windows BitLocker TPM 2.0 ile aktif şifreli olmalıdır.
3. **OS Seviyesi:** İşletim sisteminde kritik güvenlik yamaları (son 14 günlük Windows/macOS Security Patches) eksiksiz uygulanmış olmalıdır.
4. **Sertifika Doğrulaması:** İstemci makine sertifika deposunda holding PKI sertifikası doğrulanmalıdır (mTLS).

Bu dört kriterden herhangi biri başarısız olduğunda, kullanıcıya dinamik olarak `Posture_Non_Compliant` etiketi atanır ve Rule LON-02/LON-03 tarafından erişimi derhal bloke edilir.

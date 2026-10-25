# Yazılım Ekibi - Güvenlik Duvarı Kural Seti ve Mikro-Segmentasyon Matrisi

Bu belge, Yazılım Geliştirme ve DevOps ekibinin bağlı olduğu güvenlik duvarı üzerinde uygulanan sıkı kuralları tanımlar. Staging ve Production ortamlarının mutlak ayrımı, Bastion Host şartı ve dışarıya kontrolsüz kod sızıntısını engelleyen Egress kısıtlamaları yapılandırılmıştır.

---

## 1. Güvenlik Bölgeleri (Zones) ve Arabirimler
* `Zone_Dev_Workstation`: VLAN 410 Geliştirici Bilgisayarları (`10.40.10.0/24`)
* `Zone_Staging`: VLAN 420 Test ve Sahneleme Ortamı (`10.40.20.0/24`)
* `Zone_Prod_Mgmt`: VLAN 430 Üretim Yönetim ve Bastion Ağı (`10.40.30.0/24`)
* `Zone_DevOps_Services`: VLAN 440 GitLab, Harbor, Nexus (`10.40.40.0/24`)
* `Zone_Production_Data`: VLAN 105 / Harici Veri Merkezi Canlı Sunucuları (`10.10.105.0/24`)
* `Untrust_Internet`: Dış Ağ / Genel Web

---

## 2. Üretim Kural Seti Tablosu

| Rule ID | Kural Adı | Kaynak Bölge | Kaynak IP/CIDR | Hedef Bölge | Hedef IP/CIDR | Servis / Port | Uygulama (App-ID) | Eylem (Action) | Loglama | Güvenlik Profili / Koşul |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **DEV-01** | `DEV_TO_DEVOPS_CORE` | `Zone_Dev_Workstation`| `10.40.10.0/24` | `Zone_DevOps_Services`| `10.40.40.10` (GitLab), `10.40.40.20` (Harbor) | TCP/22 (Git SSH), TCP/443 (HTTPS), TCP/5000 | `git-ssh`, `ssl`, `docker-registry` | **ALLOW** | Session Close | Threat-Protection-Standard, Anti-Virus |
| **DEV-02** | `DEV_TO_STAGING_WEB` | `Zone_Dev_Workstation`| `10.40.10.0/24` | `Zone_Staging` | `10.40.20.30` (Staging Ingress VIP) | TCP/80, TCP/443, TCP/8080 | `web-browsing`, `ssl` | **ALLOW** | Session Close | Threat-Protection-Standard |
| **DEV-03** | `DEV_TO_STAGING_SSH_DENY`| `Zone_Dev_Workstation`| `10.40.10.0/24` | `Zone_Staging` | `10.40.20.0/24` | TCP/22 | `ssh` | **DENY** | Alert / Log | Dev-Direct-SSH-Violation (Doğrudan SSH yasaktır) |
| **DEV-04** | `DEV_TO_PROD_DIRECT_DENY`| `Zone_Dev_Workstation`| `10.40.10.0/24` | `Zone_Prod_Mgmt`, `Zone_Production_Data`| `10.40.30.0/24`, `10.10.105.0/24` | `any` | `any` | **DENY** | Alert / Log | Critical-Prod-Direct-Access-Alarm (Canlıya doğrudan erişim imkansızdır) |
| **DEV-05** | `DEV_TO_BASTION_MFA` | `Zone_Dev_Workstation`| `10.40.10.0/24` | `Zone_Prod_Mgmt` | `10.40.30.5` (Bastion Host) | TCP/443 (Guacamole Web), TCP/2222 | `ssl`, `ssh` | **ALLOW** | Session Start & End | MFA-Enforced (Duo/Azure MFA), Keystroke-Logging |
| **DEV-06** | `BASTION_TO_PROD_ACCESS`| `Zone_Prod_Mgmt` | `10.40.30.5` (Bastion Host) | `Zone_Production_Data` | `10.10.105.0/24` | TCP/22, TCP/443 | `ssh`, `ssl` | **ALLOW** | Session Start & End | Threat-Protect-Strict, Session-Video-Record |
| **DEV-07** | `CI_RUNNER_TO_STAGING` | `Zone_DevOps_Services`| `10.40.40.30` - `10.40.40.35` (Runners) | `Zone_Staging` | `10.40.20.10` (K8s API) | TCP/6443 | `kubernetes-api`, `ssl` | **ALLOW** | Session Close | mTLS-Certificate-Auth-Only |
| **DEV-08** | `ALLOW_APPROVED_REPOS` | `Zone_Dev_Workstation`, `Zone_DevOps_Services`| `10.40.10.0/24`, `10.40.40.0/24` | `Untrust_Internet` | FQDN: `github.com`, `registry-1.docker.io`, `pypi.org`, `npmjs.org` | TCP/443 | `ssl`, `github-base` | **ALLOW** | Session Close | SSL-Forward-Proxy (Decryption), URL-Whitelist-Strict |
| **DEV-09** | `DROP_DIRECT_SSH_RDP_OUT`| `Zone_Dev_Workstation`, `Zone_DevOps_Services`| `10.40.10.0/24`, `10.40.40.0/24` | `Untrust_Internet` | `any` | TCP/22, TCP/3389, TCP/23, TCP/445 | `ssh`, `ms-rdp`, `telnet`, `ms-ds-smb` | **DENY** | Alert / Log | Data-Exfiltration-Alert (İnternetteki doğrudan IP'lere SSH/RDP yasak) |
| **DEV-10** | `DROP_UNAPPROVED_FILESHARE`| `Zone_Dev_Workstation`| `10.40.10.0/24` | `Untrust_Internet` | Wetransfer, Mega, Anonfiles, Pastebin | TCP/80, TCP/443 | `file-sharing`, `pastebin` | **DENY** | Alert / Log | Source-Code-Leak-Alarm (Kod sızdırma siteleri bloklu) |
| **DEV-99** | `DEFAULT_DENY_ALL` | `any` | `any` | `any` | `any` | `any` | `any` | **DENY** | All Dropped | Syslog to SIEM (TLS 6514) |

---

## 3. Mikro-Segmentasyon ve Güvenlik Mekanizmaları Açıklaması

1. **Geliştirici - Production Tam İzolasyonu (DEV-04 & DEV-05):**
   * Geliştirici iş istasyonları ağından (`10.40.10.0/24`) doğrudan canlı sunuculara (`10.10.105.0/24`) gitmeye çalışan tüm paketler güvenlik duvarında engellenir.
   * Canlı ortamda bakım yapması gereken DevOps mühendisleri, önce kurumsal donanımsal anahtarla (YubiKey) MFA doğrulamasını `10.40.30.5` Bastion Host üzerinden tamamlar. Bastion host üzerindeki her SSH tuş vuruşu ve RDP ekran oturumu bağımsız bir log sunucusunda video/metin olarak kayıt altına alınır.
2. **Onaylı Repolar ve Kod Sızıntısı Engelleme (DEV-08 & DEV-09):**
   * Yazılımcıların harici kontrolsüz sunuculara veri kaçırmasını engellemek için dış internete doğru IP bazlı doğrudan SSH (TCP 22) ve RDP (TCP 3389) portları tamamen kapatılmıştır.
   * Dışarıya yalnızca GitHub, Docker Hub ve NPM gibi FQDN bazlı onaylı depolar üzerinden kod/kütüphane alışverişine izin verilir.

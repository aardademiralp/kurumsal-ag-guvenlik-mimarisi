# Yazılım Ekibi - IP Adresleme ve Segmentasyon Planı

## 1. Mimari Segmentasyon Modeli
Yazılım ekibi, holding bünyesinde `10.40.0.0/16` süpernet bloğunda konumlandırılmıştır. Geliştirme iş istasyonları, ara test ortamı (Staging) ve canlı üretim yönetim ortamı (Production Management) birbirinden bağımsız Layer 3 alt ağlarına ve ayrı Firewall Zone'larına ayrılmıştır.

---

## 2. Detaylı IP ve VLAN Tablosu

| VLAN ID | VLAN Adı | Güvenlik Bölgesi (Zone) | Ağ Adresi (CIDR) | Alt Ağ Maskesi | Varsayılan Ağ Geçidi (GW) | Kullanılabilir IP Aralığı | DHCP Dağıtım Havuzu | Statik Rezerve Alan (Sunucu/Cihaz) |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **410** | `VLAN_DEV_WORKSTATIONS`| `Zone_Dev_Workstation`| `10.40.10.0/24` | `255.255.255.0` | `10.40.10.1` | `10.40.10.2 - 10.40.10.254` | `10.40.10.50 - 10.40.10.200` | `10.40.10.2 - 10.40.10.49` (Lokal Test Cihazları, Mobil Emülatörler) |
| **420** | `VLAN_STAGE_ENV` | `Zone_Staging` | `10.40.20.0/24` | `255.255.255.0` | `10.40.20.1` | `10.40.20.2 - 10.40.20.254` | *DHCP Kapalı* | `10.40.20.2 - 10.40.20.254` (Staging K8s Node'ları, Test DB'leri) |
| **430** | `VLAN_PROD_MGMT` | `Zone_Prod_Mgmt` | `10.40.30.0/24` | `255.255.255.0` | `10.40.30.1` | `10.40.30.2 - 10.40.30.254` | *DHCP Kapalı* | `10.40.30.2 - 10.40.30.254` (Bastion Host, Jumpbox, Vault) |
| **440** | `VLAN_DEVOPS_CORE_SERVICES`| `Zone_DevOps_Services`| `10.40.40.0/24`| `255.255.255.0` | `10.40.40.1` | `10.40.40.2 - 10.40.40.254` | *DHCP Kapalı* | `10.40.40.2 - 10.40.40.254` (GitLab, Harbor Registry, CI Runners)|

---

## 3. Kritik Sunucu ve Servis IP Rezervasyonları

### VLAN 420 - Staging Ortamı (10.40.20.0/24)
* `10.40.20.10`: Staging Kubernetes API Server VIP (K8s Control Plane)
* `10.40.20.11 - 10.40.20.15`: Staging Worker Node 01 - 05
* `10.40.20.20`: Staging PostgreSQL Veri Tabanı Kümesi (Sentinels VIP)
* `10.40.20.25`: Staging Redis Cache Cluster VIP
* `10.40.20.30`: Staging Ingress NGINX / Envoy Load Balancer VIP

### VLAN 430 - Production Management (10.40.30.0/24)
* **Önemli Kural:** Bu ağa geliştirici bilgisayarlarından doğrudan IP yönlendirmesi yoktur. Yalnızca kimlik denetimli Bastion üzerinden erişilebilir.
* `10.40.30.5`: Güvenli SSH/RDP Bastion Host (Apache Guacamole / Teleport Enterprise)
* `10.40.30.10`: HashiCorp Vault Kurumsal Gizli Anahtar Yönetimi (Secrets Management)
* `10.40.30.15`: ArgoCD GitOps Production Controller Sunucusu

### VLAN 440 - DevOps Çekirdek Hizmetleri (10.40.40.0/24)
* `10.40.40.10`: Şirket İçi Git Kaynak Deposu (GitLab Enterprise Server)
* `10.40.40.20`: Konteyner İmaj Deposu (Harbor Private Docker Registry)
* `10.40.40.30 - 10.40.40.35`: Özel GitLab CI/CD Dedicated Runner Sunucuları
* `10.40.40.40`: SonarQube Statik Kod Analiz Sunucusu
* `10.40.40.50`: Nexus OSS Paket Deposu (Maven, NPM, PyPI Yerel Proxy Aynası)

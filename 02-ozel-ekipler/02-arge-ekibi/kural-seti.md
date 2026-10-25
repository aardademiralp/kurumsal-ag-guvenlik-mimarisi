# AR-GE Ekibi - Güvenlik Duvarı Kural Seti ve Egress Filtreleme Matrisi

Bu belge, AR-GE Laboratuvarı ve GPU kümesi önündeki güvenlik duvarında uygulanan teftiş ve engelleme kurallarını içerir. Kurallar, dış dünyaya veri sızıntısını sıfıra indirmek ve bulut depolama servislerini mutlak surette engellemek üzere yapılandırılmıştır.

---

## 1. Güvenlik Bölgeleri (Zones) ve Arabirimler
* `Zone_RnD_Enclave`: VLAN 510 Araştırmacı İş İstasyonları (`10.50.10.0/24`)
* `Zone_RnD_Compute`: VLAN 520 HPC DGX GPU Sunucuları (`10.50.20.0/24`)
* `Zone_RnD_Storage`: VLAN 530 NVMe Depolama Dizisi (`10.50.30.0/24`)
* `Untrust_Internet`: Dış Dünya / Genel Ağ
* `Zone_Corp_Transit`: Kurumsal Merkez Transit Ağı

---

## 2. Üretim Kural Seti Tablosu

| Rule ID | Kural Adı | Kaynak Bölge | Kaynak IP/CIDR | Hedef Bölge | Hedef IP/CIDR | Servis / Port | Uygulama (App-ID) | Eylem (Action) | Loglama | Güvenlik Profili / DLP Kuralı |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **RND-01** | `BLOCK_CLOUD_STORAGE_OUT`| `Zone_RnD_Enclave`, `Zone_RnD_Compute` | `10.50.0.0/16` | `Untrust_Internet` | FQDN: Google Drive, Dropbox, OneDrive, Mega, Box, iCloud | TCP/80, TCP/443 | `google-drive`, `dropbox`, `onedrive`, `box-net`, `mega-upload` | **DENY** | Alert / Log | Critical-Exfiltration-Alarm (Bulut depolamaya yükleme girişimi) |
| **RND-02** | `BLOCK_PUBLIC_GIT_PUSH` | `Zone_RnD_Enclave`, `Zone_RnD_Compute` | `10.50.0.0/16` | `Untrust_Internet` | GitHub, GitLab.com, Bitbucket | TCP/22, TCP/443 | `github-upload`, `git-push` | **DENY** | Alert / Log | IP-Theft-Prevention (Dış repolara push yapılamaz) |
| **RND-03** | `BLOCK_PASTEBINS_AND_AI` | `Zone_RnD_Enclave` | `10.50.10.0/24` | `Untrust_Internet` | ChatGPT, Claude, Pastebin, Ghostbin | TCP/443 | `openai-chatgpt`, `pastebin`, `anthropic-claude` | **DENY** | Alert / Log | Unsanctioned-AI-Drop (Harici AI araçlarına veri aktarımı engelli) |
| **RND-04** | `BLOCK_ALL_DIRECT_EGRESS`| `Zone_RnD_Compute`, `Zone_RnD_Storage` | `10.50.20.0/24`, `10.50.30.0/24` | `Untrust_Internet` | `any` | `any` | `any` | **DENY** | Alert / Log | Air-Gap-Violation (GPU ve Storage dış internete tamamen kapalıdır) |
| **RND-05** | `ALLOW_INTERNAL_HPC_JOBS`| `Zone_RnD_Enclave` | `10.50.10.0/24` | `Zone_RnD_Compute` | `10.50.20.10` (Slurm Master), `10.50.20.20` (MLflow) | TCP/6817-6818, TCP/5000 | `slurm`, `ssl` | **ALLOW** | Session Close | Threat-Protection-Standard |
| **RND-06** | `GPU_TO_STORAGE_ROCE` | `Zone_RnD_Compute` | `10.50.20.0/24` | `Zone_RnD_Storage` | `10.50.30.0/24` | RoCE v2 (UDP/4791), TCP/2049 (NFSv4.2), TCP/6789 (Ceph) | `roce-v2`, `nfs`, `ceph` | **ALLOW** | No Log (Ultra-High-Speed)| Jumbo-Frames-Enabled, Wire-Speed |
| **RND-07** | `WORKSTATION_TO_STORAGE` | `Zone_RnD_Enclave` | `10.50.10.0/24` | `Zone_RnD_Storage` | `10.50.30.10` (MDS / File Gateway) | TCP/2049, TCP/443 | `nfs`, `ssl` | **ALLOW** | Session Close | DLP-Model-Weights-Monitor, Kerberos-Auth |
| **RND-08** | `AIRLOCK_INGRESS_ONLY` | `Zone_Corp_Transit` | `10.10.30.50` (Onaylı Veri Aktarım) | `Zone_RnD_Enclave` | `10.50.10.5` (Air-Lock Sunucu) | TCP/443 | `ssl` | **ALLOW** | Session Start & End | Deep-AV, File-Blocking, Sandbox-Inspection |
| **RND-09** | `RESTRICTED_RESEARCH_WEB`| `Zone_RnD_Enclave` | `10.50.10.0/24` | `Untrust_Internet` | FQDN Whitelist: `arxiv.org`, `paperswithcode.com`, `huggingface.co` | TCP/443 | `web-browsing`, `ssl` | **ALLOW** | Session Close | SSL-Decryption-Strict, File-Blocking-Upload (Sadece indirme, dosya yükleme drop) |
| **RND-99** | `DEFAULT_DENY_ALL` | `any` | `any` | `any` | `any` | `any` | `any` | **DENY** | All Dropped | SIEM Alert (P1 Security Incident) |

---

## 3. Katı Güvenlik ve Egress Teftiş Mekanizmaları

1. **Upload / Yükleme Blokajı (HTTP POST Denetimi - RND-09):**
   * Araştırmacıların akademik makaleleri okuması için `arxiv.org` veya `huggingface.co` adreslerine erişim izni verilir.
   * Ancak Palo Alto / FortiGate üzerinde derin SSL Decryption ile HTTP method teftişi yapılır: `GET` isteklerine (indirme) izin verilirken, `POST / PUT` (veri yükleme) istekleri engellenir. Böylece tescilli kod parçacıkları bu sitelere dahi aktarılamaz.
2. **GPU ve Depolama Donanımsal İzolasyonu (RND-04 & RND-06):**
   * DGX GPU kümesi ve NVMe depolama alanı Layer 3 yönlendirme seviyesinde sıfır internet (No Default Gateway to Outside) kuralıyla çalışır.
   * GPU'lar ile Depolama üniteleri arasında RoCE v2 (RDMA over Converged Ethernet) protokolü kayıpsız (PFC - Priority Flow Control) olarak 100 Gbps omurgada çalışır.

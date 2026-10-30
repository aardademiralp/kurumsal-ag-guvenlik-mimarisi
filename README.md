# Kurumsal Ağ ve Siber Güvenlik Mimarisi Projesi (Holding & Üniversite)

**Mimar:** Kıdemli Kurumsal Ağ ve Siber Güvenlik Mimarı (Senior Enterprise Network & Security Architect)  
**Tarih:** 2026  
**Sürüm:** 1.0 (Enterprise Production-Ready Release)  
**Kapsam:** Çok Şubeli Holding, Uluslararası Ofisler, Ar-Ge Laboratuvarları ve 10.000 Öğrencili Üniversite Kampüsü  

---

## 1. Yönetici Özeti (Executive Summary)

Bu proje; çok şubeli, yüksek kapasiteli, akademik ve AR-GE birimlerine sahip bir holding/üniversite yapısı için tasarlanmış uçtan uca kurumsal ağ ve güvenlik mimarisi mühendislik çalışmasıdır.

Tasarım; **Zero-Trust (NIST SP 800-207)**, **Mikro-Segmentasyon**, **Yüksek Erişilebilirlik (HA - 99.999% Uptime)** ve **Katman 7 Derin Paket İnceleme (L7 Full DPI)** prensiplerine tam uyumlu olarak inşa edilmiştir.

### Temel Mimari İlkeler:
1. **Klasörleme İlkesi:** Projedeki her şube, ekip, firewall analizi, kurulum adımı ve izleme başlığı istisnasız ayrı bir klasörde yer almaktadır.
2. **Teknik Derinlik İlkesi:** Asla yer tutucu (placeholder) veya özet ifadeler kullanılmamış; tüm IP adresleri somut CIDR bloklarıyla (`10.x.x.x`), VLAN ID'leriyle, protokol ve portlarıyla tam tablolar halinde belgelenmiştir.
3. **Gerçekçi Donanım:** Seçilen güvenlik duvarları için piyasada aktif kullanılan gerçek kurumsal modeller (Palo Alto PA Serisi, Fortinet FortiGate) ve gerçek throughput/SSL inspection kapasiteleri baz alınmıştır.

---

## 2. Global Ağ ve Güvenlik Topolojisi (Mermaid)

```mermaid
graph TD
    subgraph WAN_CLOUD["Global WAN ve İnternet Katmanı"]
        ISP_TT["Türk Telekom Metro Ethernet"]
        ISP_TURKCELL["Turkcell Superonline Metro"]
        ISP_ULAKBIM["ULAKBİM 10G Ulusal Akademik Ağ"]
        ISP_COLT["Colt Technology Services UK (300M)"]
    end

    subgraph ANKARA_HQ["01-Ankara Genel Merkez (Hub / Core Datacenter)"]
        FW_HQ["Palo Alto PA-3410 HA Cluster (Active/Passive)"]
        CORE_HQ["Cisco Catalyst 9500 StackWise-Virtual Core"]
        DC_SERVERS["Active Directory, DNS, PKI, SAP HANA (VLAN 100/105)"]
        HQ_USERS["Yönetim (VLAN 10), Finans (VLAN 20), Operasyon (VLAN 30)"]
    end

    subgraph ISTANBUL_BRANCH["02-İstanbul Maslak Şubesi (Spoke DIA)"]
        FW_IST["Fortinet FortiGate 100F (SOC4 SD-WAN)"]
        IST_USERS["Kurumsal Çalışanlar (VLAN 110)"]
        IST_GUEST["Misafir Wi-Fi (VLAN 120 - 172.16.20.0/24)"]
    end

    subgraph LONDON_BRANCH["03-Londra Canary Wharf Şubesi (Secure Spoke)"]
        FW_LON["Palo Alto PA-440 (Fansız - 0 dB Akustik)"]
        LON_USERS["Uluslararası Ticaret, Hukuk, VIP ZTNA (VLAN 210)"]
    end

    subgraph CAMPUS_BRANCH["04-Akademik Şube & Kampüs (10k Öğrenci)"]
        FW_CMP["Fortinet FortiGate 1800F HA Cluster (NP7 ASIC)"]
        CORE_CMP["Cisco Catalyst 9600 10G/40G Core Chassis"]
        CMP_STUDENTS["10.000 Öğrenci Eduroam (VLAN 300-305: 10.100.0.0/16)"]
        CMP_ACADEMIC["Akademisyenler (VLAN 310), İdari (VLAN 320), LMS (VLAN 330)"]
    end

    subgraph SPECIAL_TEAMS["02-Özel Ekipler (Yüksek Güvenlik)"]
        DEV_TEAM["Yazılım Ekibi: Workstations (VLAN 410), Staging (420), Prod Mgmt (430)"]
        RND_TEAM["AR-GE Ekibi: Air-Gapped Lab (VLAN 510), DGX GPU (520), NVMe (530)"]
    end

    %% Bağlantılar
    ISP_TT <==>|1G Metro| FW_HQ
    ISP_TURKCELL <==>|1G Metro| FW_HQ
    FW_HQ <==>|10G LACP ae1| CORE_HQ
    CORE_HQ --- DC_SERVERS
    CORE_HQ --- HQ_USERS
    CORE_HQ --- SPECIAL_TEAMS

    FW_IST <==>|500M DIA| ISP_TT
    FW_IST <==>|IPsec Tünel (RFC 1918 Trafiği)| FW_HQ
    FW_IST --- IST_USERS
    FW_IST --- IST_GUEST

    FW_LON <==>|300M DIA| ISP_COLT
    FW_LON <==>|IPsec Tünel & ZTNA| FW_HQ
    FW_LON --- LON_USERS

    ISP_ULAKBIM <==>|10G Fiber| FW_CMP
    ISP_TT <==>|10G Fiber| FW_CMP
    FW_CMP <==>|20G LACP Trunk| CORE_CMP
    CORE_CMP --- CMP_STUDENTS
    CORE_CMP --- CMP_ACADEMIC
```

---

## 3. Global IP Süpernet ve VLAN Özet Planı (Summarization)

| Lokasyon / Birim | Süpernet Bloğu (CIDR) | Alt Ağlar (Subnets) | Gateway / L3 Sınırı | Güvenlik Bölgesi (Zone) |
| :--- | :--- | :--- | :--- | :--- |
| **Ankara Genel Merkez** | `10.10.0.0/16` | VLAN 10 (10.10.10.0/24), VLAN 20 (10.10.20.0/24), VLAN 30 (10.10.30.0/24), VLAN 99 (10.10.99.0/24), VLAN 100/105 | Palo Alto PA-3410 | `Trust_Executive`, `Trust_Finance`, `Trust_Corporate`, `Zone_DC` |
| **İstanbul Şubesi** | `10.20.0.0/16` & `172.16.20.0/24` | VLAN 110 (10.20.10.0/24), VLAN 120 (172.16.20.0/24 - Guest), VLAN 199 (10.20.99.0/24) | FortiGate 100F | `Zone_IST_Trust`, `Zone_IST_Guest`, `Zone_IST_Mgmt` |
| **Londra Şubesi** | `10.30.0.0/16` | VLAN 210 (10.30.10.0/24), VLAN 299 (10.30.99.0/24 - OOBM) | Palo Alto PA-440 | `Zone_LON_Trust`, `Zone_LON_Mgmt` |
| **Yazılım ve DevOps**| `10.40.0.0/16` | VLAN 410 (10.40.10.0/24 - Dev), VLAN 420 (Staging), VLAN 430 (Prod Mgmt), VLAN 440 (DevOps) | L3 Core / FW | `Zone_Dev_Workstation`, `Zone_Staging`, `Zone_Prod_Mgmt` |
| **AR-GE ve Yapay Zeka**| `10.50.0.0/16` | VLAN 510 (10.50.10.0/24 - Lab), VLAN 520 (DGX GPU), VLAN 530 (NVMe Storage) | Air-Lock FW | `Zone_RnD_Enclave`, `Zone_RnD_Compute`, `Zone_RnD_Storage` |
| **Akademik Kampüs** | `10.100.0.0/16` & `10.101.0.0/16` | VLAN 300-305 (10.100.0.0/16 Pool), VLAN 310 (Akademik), VLAN 320 (İdari), VLAN 330 (LMS) | FortiGate 1800F | `Zone_Campus_Student`, `Zone_Campus_Academic`, `Zone_Campus_Admin` |

---

## 4. Dizin Yapısı ve Belge Kütüphanesi

Tüm proje belgeleri, şartnamede belirtilen hiyerarşide tam içerikle oluşturulmuştur:

```
kurumsal-ag-guvenlik-mimarisi/
├── 01-subeler/
│   ├── 01-ankara-genel-merkez/
│   │   ├── profil.md                  # 300 personel organizasyon şeması ve kritik roller
│   │   ├── ip-ve-vlan-plani.md        # VLAN 10, 20, 30, 99 detaylı CIDR tablosu
│   │   ├── bant-genisligi.md          # %90 eşzamanlılık, 1.2G peak hesabı, 2x 1G SD-WAN
│   │   ├── guvenlik-duvari-secimi.md  # Palo Alto PA-3410 ve Check Point 6600 analizi
│   │   ├── kurulum-adimlari.md        # OOBM, Active/Passive HA, LACP, BGP, Cutover
│   │   └── kural-seti.md              # Finans/Yönetim katı mikro-segmentasyon tablosu
│   ├── 02-istanbul-subesi/
│   │   ├── profil.md                  # 150 personel (Satış, Pazarlama, Saha ekipleri)
│   │   ├── ip-ve-vlan-plani.md        # VLAN 110 (Kurumsal) & VLAN 120 (Misafir)
│   │   ├── bant-genisligi.md          # 500M DIA, M365 yerel çıkış ve Hub IPsec tünel
│   │   ├── guvenlik-duvari-secimi.md  # Fortinet FortiGate 100F SOC4 ASIC analizi
│   │   ├── kurulum-adimlari.md        # WAN provisioning, SD-WAN policy, IPsec CLI
│   │   └── kural-seti.md              # Misafir izolasyonu, M365 ve Merkez intranet kuralları
│   ├── 03-londra-subesi/
│   │   ├── profil.md                  # 50 personel (Uluslararası Ticaret, Hukuk, C-Level)
│   │   ├── ip-ve-vlan-plani.md        # VLAN 210 (Kurumsal) & VLAN 299 (OOBM)
│   │   ├── bant-genisligi.md          # 300M Simetrik, RTT < 48ms BDP hesabı ve ZTNA
│   │   ├── guvenlik-duvari-secimi.md  # Palo Alto PA-440 (0 dB Fansız akustik tasarım)
│   │   ├── kurulum-adimlari.md        # Cloud Zero-Touch Provisioning (ZTP) ve Panorama
│   │   └── kural-seti.md              # Katı Geo-IP (Sadece UK ve TR) ve ZTNA HIP kuralları
│   └── 04-akademik-sube-kampus/
│       ├── profil.md                  # 10.000 Öğrenci, 500 Akademisyen, 200 İdari Personel
│       ├── ip-ve-vlan-plani.md        # VLAN 300-305 (Eduroam /16 pool), 310, 320, 330
│       ├── bant-genisligi.md          # 4.000 Peak cihaz, overbooking formülü, 10G LACP
│       ├── guvenlik-duvari-secimi.md  # Fortinet FortiGate 1800F (NP7 ASIC 120M Oturum)
│       ├── kurulum-adimlari.md        # 10G SFP+ Core trunk, FGCP HA, Eduroam RADIUS
│       └── kural-seti.md              # P2P/Torrent engelleme, DNS tünelleme, LMS izolasyonu
├── 02-ozel-ekipler/
│   ├── 01-yazilim-ekibi/
│   │   ├── profil.md                  # 80 Developer, DevOps ve QA mühendisi
│   │   ├── ip-ve-vlan-plani.md        # VLAN 410 (Dev), 420 (Stage), 430 (Prod Mgmt), 440
│   │   ├── ag-gereksinimleri.md       # CI/CD Runner, Harbor Registry 1G omurga throughput
│   │   └── kural-seti.md              # Staging/Prod izolasyonu, Bastion MFA, onaylı repolar
│   └── 02-arge-ekibi/
│       ├── profil.md                  # 40 Veri Bilimci, AI/ML Araştırmacısı
│       ├── ip-ve-vlan-plani.md        # VLAN 510 (Lab), 520 (DGX GPU), 530 (NVMe Storage)
│       ├── izolasyon-politikasi.md    # IP koruma, DLP, Hava Kilidi (Data Air-Lock)
│       └── kural-seti.md              # Sıfır Egress, Bulut depolama ve Git push blokajı
├── 03-guvenlik-duvarlari/
│   ├── 01-top5-ngfw-karsilastirma/
│   │   └── karsilastirma.md           # Palo Alto, Fortinet, Check Point, Cisco, Netgate
│   ├── 02-neden-tercih-etmedik-analizi/
│   │   └── opsiyonel-analiz.md        # L4 Stateful, KOBİ UTM, Salt Cloud WAF risk analizi
│   ├── 03-kural-setleri-ve-politikalar/
│   │   └── genel-politika.md          # Default-Deny, Least Privilege, Zone Hiyerarşisi
│   └── 04-adim-adim-kurulum-rehberi/
│       └── standart-devreye-alma.md   # Tüm şubeler için 8 aşamalı devreye alma metodolojisi
└── 04-izleme-ve-yonetim/
    ├── 01-sistematik-izleme-teknolojileri/
    │   └── teknik-mimari.md           # NetFlow v9/IPFIX, TLS Syslog 6514, Zeek & Suricata
    ├── 02-insani-faktor-ve-soc-operasyonu/
    │   └── soc-yapisi.md              # L1/L2/L3 Hiyerarşisi, 7/24 Vardiya, SLA ve Playbook
    └── 03-bant-genisligi-ve-qos-yonetimi/
        └── qos-politikasi.md          # DSCP Matrisi (EF, AF41, AF21, CS1), Shaping vs Policing
tools/
├── 01-kural-dogrulayici-ve-analiz/
│   ├── rules_schema.json              # Güvenlik duvarı kural JSON şeması
│   ├── sample_network_rules.json      # 19 adet gerçekçi kurumsal kural veri seti
│   └── policy_validator.py            # Mikro-segmentasyon, shadowing ve default-deny denetçisi
├── 02-vendor-cli-donusturucu/
│   └── vendor_exporter.py             # FortiOS (.cfg) ve PAN-OS (.set) CLI derleyicisi
├── 03-kapasite-ve-qos-hesaplayici/
│   └── bandwidth_engine.py            # 10k Kampüs peak/overbooking ve 10G LACP hesaplayıcısı
├── 04-soc-telemetri-simulatoru/
│   └── syslog_generator.py            # ArcSight CEF ve RFC 5424 sentetik SOC log üreteci
└── 05-otomasyon-test-merkezi/
    ├── run_all_checks.py              # Tüm suite'i tek komutla koşturan DevSecOps orkestratörü
    └── build/                         # Otomatik derlenen Fortinet/PaloAlto/SOC artifact'ları
```

---

## 5. Ağ Otomasyonu ve DevSecOps Araç Seti (Network Automation & Tools)

Tüm araçlar harici hiçbir üçüncü parti kütüphaneye ihtiyaç duymadan, yalnızca standart Python 3 kütüphaneleri (`json`, `ipaddress`, `argparse`, `sys`, `datetime`, `random`, `subprocess`) ile yazılmıştır.

### 5.1. Kural Doğrulayıcı ve Mikro-Segmentasyon Denetçisi
```bash
# Standart kural denetimi
python tools/01-kural-dogrulayici-ve-analiz/policy_validator.py

# Yapay güvenlik ihlali enjeksiyonu ile test (Öğrenci -> İdari Sistemler ihlal yakalama)
python tools/01-kural-dogrulayici-ve-analiz/policy_validator.py --test-violation
```

### 5.2. Vendor CLI Derleyicisi (Fortinet & Palo Alto)
```bash
# FortiOS formatına derle
python tools/02-vendor-cli-donusturucu/vendor_exporter.py --target fortinet

# PAN-OS set formatına derle ve kaydet
python tools/02-vendor-cli-donusturucu/vendor_exporter.py --target paloalto --output build/paloalto_rules.set
```

### 5.3. Kampüs Bant Genişliği ve QoS Kapasite Motoru
```bash
python tools/03-kapasite-ve-qos-hesaplayici/bandwidth_engine.py --students 10000 --concurrency 0.40 --student-mbps 8 --staff 700 --staff-mbps 15 --overbooking 4
```

### 5.4. SOC Sentetik Telemetri Simülatörü
```bash
python tools/04-soc-telemetri-simulatoru/syslog_generator.py --scenario all --count 10 --format both --output tools/05-otomasyon-test-merkezi/build/soc_events.log
```

### 5.5. Bütünsel Test Orkestratörü
```bash
# Tek komutla tüm kuralları doğrula, CLI'ları derle, kapasiteyi hesapla ve SOC loglarını test et:
python tools/05-otomasyon-test-merkezi/run_all_checks.py
```

---

## 6. Doğrulama ve İnceleme

Tüm dokümantasyon ve otomasyon scriptleri fiziksel dosya sisteminde `C:\Users\Aydın\.gemini\antigravity\scratch\kurumsal-ag-guvenlik-mimarisi` kök dizini altında eksiksiz yer almaktadır.

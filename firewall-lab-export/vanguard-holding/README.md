# Vanguard Holding & Academy — Kurumsal Ağ ve Güvenlik Mimarisi Kataloğu

[![PR Status](https://img.shields.io/badge/PR-Ready_for_Review-success.svg)](https://github.com/vanguard-holding/firewall-lab)
[![Zero-Trust Architecture](https://img.shields.io/badge/Architecture-NIST_SP_800--207_Zero--Trust-blue.svg)](#4-güvenlik-politikası-ve-mimari-analiz)
[![Core Firewalls](https://img.shields.io/badge/NGFW-Palo_Alto_PA--3410_%7C_FortiGate_1800F-orange.svg)](#2-mimari-ve-donanım-seçim-gerekçeleri)
[![Total Rules](https://img.shields.io/badge/Verified_Rules-28_Policies_in_company.json-blueviolet.svg)](#5-birleşik-kural-seti-ve-companyjson-özeti)
[![Bandwidth Capacity](https://img.shields.io/badge/Campus_WAN-4x_10G_LACP_Metro_Ethernet-red.svg)](#3-kapasite-planlaması-ve-bant-genişliği-mühendisliği)

---

## Yönetici Özeti (Executive Summary)

Bu doküman, **Vanguard Holding & Academy** kurumsal yapısının çok şubeli, yüksek kapasiteli, akademik ve AR-GE birimlerini kapsayan uçtan uca yeni nesil ağ ve güvenlik mimarisi (NGFW) projesinin vitrin dokümanıdır. 

Hocanın GitHub üzerindeki `firewall-lab` kataloğuna Pull Request (PR) olarak sunulmak üzere hazırlanmış olup; **NIST SP 800-207 Zero-Trust** prensiplerine tam uyumlu mikro-segmentasyon stratejisini, **10.000 öğrenci ve 1.000+ çalışan** için matematiksel olarak kanıtlanmış kapasite ve donanım boyutlandırma hesaplarını ve `company.json` içerisinde yer alan **28 adet kurumsal güvenlik politikasının** teknik gerekçelerini eksiksiz sunmaktadır.

---

## 1. Şirket Profili ve Organizasyon Yapısı

Vanguard Holding & Academy; uluslararası finans, yazılım geliştirme, ileri seviye yapay zeka araştırmaları ve yükseköğretim faaliyetlerini tek bir kurumsal çatı altında birleştiren hibrit bir holding ve üniversite ekosistemidir.

```
                              ┌──────────────────────────────────────┐
                              │     VANGUARD HOLDING & ACADEMY       │
                              │           Yönetim Kurulu             │
                              └──────────────────┬───────────────────┘
                                                 │
         ┌───────────────────────┬───────────────┴───────────────┬───────────────────────┐
         │                       │                               │                       │
┌────────┴────────┐     ┌────────┴────────┐             ┌────────┴────────┐     ┌────────┴────────┐
│  Ankara Genel   │     │ İstanbul Satış  │             │ Londra İrtibat  │     │    Vanguard     │
│  Merkez (HQ)    │     │ & Operasyon     │             │ & Hukuk Ofisi   │     │    Academy      │
│  (300 Personel) │     │ (150 Personel)  │             │ (50 Personel)   │     │ (10.000 Öğrenci)│
└────────┬────────┘     └─────────────────┘             └─────────────────┘     └────────┬────────┘
         │                                                                               │
         ├─ Finans & Hazine                                                              ├─ 700 Personel
         ├─ İK & Operasyon                                                               ├─ Eduroam Wi-Fi
         ├─ Active Directory DC                                                          ├─ ÖBS & LMS Portal
         └─ SAP S/4HANA ERP                                                              └─ HPC Kümeleri
                                 ┌───────────────────────────────┐
                                 │   Özel İhtisas Birimleri      │
                                 ├───────────────────────────────┤
                                 │ 1. Yazılım Geliştirme (80 Dev)│
                                 │ 2. Ar-Ge AI Enclave (20 Ar-Ge)│
                                 └───────────────────────────────┘
```

### Kurumsal Birimler ve Ağ Rolleri

| Birim | Personel / Kullanıcı | Temel Fonksiyon ve Sistemler | Güvenlik İhtiyacı |
| :--- | :--- | :--- | :--- |
| **Ankara Genel Merkez (HQ)** | 300 Personel | Yönetim, İK, Operasyon, Hazine; Active Directory, SAP S/4HANA ERP, Kurumsal SIEM. | Finansal veri koruması, PCI-DSS / KVKK uyumu, katı mikro-segmentasyon. |
| **İstanbul Şubesi** | 150 Personel | Saha ekipleri, Satış ve Pazarlama; Microsoft 365, Salesforce, Zoom. | Direct Internet Access (DIA), SD-WAN dinamik SLA yönlendirmesi, misafir izolasyonu. |
| **Londra İrtibat Ofisi** | 50 Personel | Uluslararası Ticaret, Hukuk, Fon Yönetimi; Cloud ERP, Uluslararası Bankacılık. | GDPR uyumu, ofis içi 0 dB fansız (sessiz) donanım, tam tünel IPsec. |
| **Akademik Kampüs (Academy)** | 10.000 Öğrenci + 700 Personel | Yükseköğretim, Eduroam Wi-Fi 6, Öğrenci Bilgi Sistemi (ÖBS), LMS Veri Tabanı, HPC. | 120M oturum yönetimi, SYN/UDP flood savunması, akademik ve idari ağ izolasyonu. |
| **Yazılım & Ar-Ge Merkezi** | 80 Dev/DevOps Mühendisi | CI/CD Pipeline (GitLab, Harbor), Kubernetes Staging ve Prod Kümeleri. | Zero-Trust Egress kontrolü, supply chain teftişi, kod sızıntısı önleme. |
| **Ar-Ge AI & Kripto Laboratuvarı** | 20 Kıdemli Araştırmacı | NVIDIA DGX H100 GPU Kümeleri, NVMe RoCE v2 Depolama, Model Ağırlıkları. | **Air-Gapped benzeri katı yalıtım**, %100 internet blokajı, donanımsal DLP. |

---

## 2. Mimari ve Donanım Seçim Gerekçeleri

Kurumsal mimarimizde **"Her birim için doğru donanım ve çoklu üretici (multi-vendor) hibrit güvenlik stratejisi"** benimsenmiştir. Tek bir üreticiye bağımlı kalmak (vendor lock-in) yerine; derin katman 7 uygulama teftişi gerektiren yönetim/finans merkezinde **Palo Alto Networks**, devasa oturum ve hat hızında paket işleme gerektiren akademik kampüs omurgasında **Fortinet NP7 ASIC** mimarisi tercih edilmiştir.

### 2.1. Palo Alto Networks PA-3410 — Ankara Genel Merkez (HQ)

Ankara HQ, grubun finansal kalbidir (SAP S/4HANA, SWIFT işlemleri, kurumsal Active Directory). Burada **Palo Alto PA-3410** seçilmesinin teknik gerekçeleri:

1. **Single-Pass Architecture (SP3 Engine):** Geleneksel güvenlik duvarları paketi önce güvenlik duvarı motoruna, sonra IPS motoruna, ardından antivirüs motoruna ayrı ayrı kopyalarak işlem kuyruğu gecikmesi (pipeline delay) üretir. Palo Alto SP3 mimarisi, ağ işleme, donanım ayrıştırma, App-ID, User-ID ve Content-ID (IPS/DLP/AV) işlemlerini **tek bir donanımsal geçişte** gerçekleştirir.
2. **Kayıpsız SSL/TLS 1.3 Teftişi (4.3 Gbps Full Threat Throughput):** Finans departmanının dış dünya ve ERP ile yaptığı tüm trafik TLS 1.3 ile şifrelidir. PA-3410, donanımsal kriptografik hızlandırıcıları sayesinde 4.3 Gbps tehdit önleme ve SSL decryption kapasitesi sunarak teftiş esnasında CPU darboğazı yaşanmasını önler.
3. **App-ID ve Dinamik User-ID Entegrasyonu:** Port bazlı kurallar yerine uygulamanın gerçek kimliğini (örn. TCP 443 içinden akan trafiğin Salesforce mu, TeamViewer mı, yoksa şifreli bir C2 tüneli mi olduğunu) analiz eder. Active Directory entegrasyonu ile IP adresi yerine kullanıcı rollerine dayalı kural işletir.
4. **Active/Passive HA (High Availability):** Dedicated HA1 (Control/Sync) ve HA2 (Data plane session sync) portları üzerinden milisaniyenin altında failover garantisi verilir.

### 2.2. Fortinet FortiGate 1800F — Akademik Kampüs Çekirdeği

10.000 öğrenci ve 700 personelin bulunduğu devasa kampüs omurgasında **Fortinet FortiGate 1800F** seçilmesinin teknik gerekçeleri:

1. **7. Nesil Ağ İşlemcisi (NP7 ASIC) Donanımsal Hızlandırma:** Genel amaçlı x86 CPU'lar yüksek paket sayılarında (PPS) kesme (interrupt) fırtınasına girer. Fortinet'in özel geliştirilmiş **NP7 ASIC** çipi; IPv4/IPv6 yönlendirme, NAT, IPsec şifreleme ve DoS/DDoS korumasını doğrudan donanım silikonunda gerçekleştirir.
2. **Eşzamanlı Oturum Kapasitesi (120 Milyon Concurrent Sessions):** 10.000 öğrencinin aynı anda telefon, tablet ve dizüstü bilgisayarlarından açtığı arka plan mobil uygulamaları, anlık mesajlaşma ve eşzamanlı web soketleri olağanüstü bir oturum sayısı üretir. FortiGate 1800F, 120 milyon eşzamanlı oturum ve **saniyede 500.000 yeni oturum açma (CPS)** kapasitesiyle oturum tablosunun (session exhaustion) taşmasını kesin olarak engeller.
3. **Yüksek IPS ve Tehdit Önleme Kapasitesi (17 Gbps Threat / 36 Gbps IPS):** Eduroam açık Wi-Fi ağından gelebilecek kötü amaçlı yazılım yayılımlarını ve akademik sistemlere yönelik saldırıları hat hızında süzer.
4. **40G QSFP+ / 10G SFP+ Port Zenginliği:** 4x 10G LACP Metro Ethernet uplink bağlantısını doğrudan karşılayacak yerleşik yüksek hızlı arayüzlere sahiptir.

### 2.3. Şube ve Özel Laboratuvar Donanımları

* **İstanbul Şubesi — Fortinet FortiGate 100F:** Yerleşik SOC4 (System on a Chip 4) işlemcisiyle düşük güç tüketimi, 1 Gbps Threat Protection ve yerleşik SD-WAN motoru sunar. M365 DIA trafiğini yerel ISP'ye, Ankara ERP trafiğini ise IPsec VPN'e gecikme/jitter metriklerine göre milisaniyeler içinde yönlendirir.
* **Londra İrtibat Ofisi — Palo Alto Networks PA-440:** Yönetim ve fon yetkililerinin bulunduğu ofis ortamında kabin gürültüsünü engellemek için **0 dB Fanless (tamamen sessiz)** tasarıma sahiptir. Küçük kasasına rağmen kurumsal PAN-OS işletim sistemiyle tam uygulama teftişi ve DNS Security sağlar.
* **Yazılım & Ar-Ge Merkezi — Check Point Quantum 6600:** SandBlast Zero-Day Protection motoru, Threat Emulation ve Threat Extraction özellikleri ile CI/CD geliştirme süreçlerinde indirilen açık kaynak paketleri ve bağımlılıkları sanal kum havuzunda (sandbox) teftiş eder.

---

## 3. Kapasite Planlaması ve Bant Genişliği Mühendisliği

Kampüs ve şube bant genişlikleri tahmini varsayımlarla değil, **istatistiksel ağ teorisi, peak concurrency modelleri ve QoS rezervasyon formülleriyle** hesaplanmıştır.

### 3.1. 10.000 Öğrenci Peak Concurrency Matematiksel Formülü

Kurumsal Wi-Fi ve kampüs geniş alan ağlarında (WAN) eşzamanlı bant genişliği talebi şu formülle modellenir:

$$BW_{kampus} = (N_{ogrenci} \times C_{katilim}) \times R_{kullanici} \times C_{overbooking}$$

#### Formül Parametreleri ve Sayısal Değerler:

1. **Toplam Kayıtlı Öğrenci Sayısı ($N_{ogrenci}$):** $10.000$ öğrenci.
2. **Tepe Eşzamanlılık / Katılım Oranı ($C_{katilim}$):** Kampüs genelinde ders, kütüphane ve sosyal alanlardaki öğrencilerin tepe saatte aynı anda ağa bağlı olma oranı $\%40$ olarak ölçülmüştür.
   $$N_{aktif} = 10.000 \times 0.40 = 4.000\text{ anlık aktif cihaz}$$
3. **Kullanıcı Başına Pik Tüketim Hızı ($R_{kullanici}$):** Eşzamanlı video akışı (Full HD konferans, LMS video, web seminerleri) ve akademik araştırma tepe gereksinimi:
   $$R_{kullanici} = 8\text{ Mbps}$$
4. **Ham Tepe Trafiği (Raw Peak Demand):**
   $$BW_{raw} = 4.000 \times 8\text{ Mbps} = 32.000\text{ Mbps} = 32.0\text{ Gbps}$$
5. **İstatistiksel Çoklama / Aşırı Tahsisat Faktörü ($C_{overbooking}$):** Paket anahtarlamalı (packet-switched) IP ağlarında kullanıcılar sürekli hat tüketmez; web sayfalarının yüklenmesi, duraklamalar ve asenkron trafik nedeniyle $1:4$ oranında istatistiksel çoklama ($C_{overbooking} = 0.25$) uygulanır:
   $$BW_{ogrenci} = 32.0\text{ Gbps} \times 0.25 = 8.0\text{ Gbps}$$

### 3.2. Personel Yükü ve Kritik Hizmet (QoS) Rezervasyonları

1. **Akademik & İdari Personel Bant Genişliği:**
   * $700$ personel $\times 90\%$ eşzamanlılık ($N = 630$ aktif personel).
   * İdari işlemler, SAP S/4HANA, bulut dosya aktarımları için kullanıcı başı $15\text{ Mbps}$ ayrılmıştır:
     $$BW_{personel} = 630 \times 15\text{ Mbps} = 9.450\text{ Mbps} = 9.45\text{ Gbps}$$
2. **Hizmet Kalitesi (QoS) Donanımsal Kuyruk Rezervasyonları:**
   * **VoIP & Video Konferans (DSCP EF - Expedited Forwarding):** Jitter ve gecikmeye sıfır toleranslı ses omurgası için ayrılmış bant:
     $$BW_{VoIP} = 500\text{ Mbps}$$
   * **Öğrenci Bilgi Sistemi & LMS DB Sınav Dönemi Trafiği (DSCP AF21):** Sınav dönemlerinde darboğazı önlemek için garantili bant:
     $$BW_{LMS} = 1.500\text{ Mbps} = 1.50\text{ Gbps}$$

### 3.3. Toplam Kapasite ve 4x 10G LACP Metro Ethernet Boyutlandırması

$$\begin{aligned}
BW_{alt\_toplam} &= BW_{ogrenci} + BW_{personel} + BW_{VoIP} + BW_{LMS} \\
&= 8.00\text{ Gbps} + 9.45\text{ Gbps} + 0.50\text{ Gbps} + 1.50\text{ Gbps} \\
&= \mathbf{19.45\text{ Gbps}}
\end{aligned}$$

Ani trafik patlamaları, rektörlük canlı yayınları ve akademik veri seti indirmeleri için $\%20$ dinamik güvenlik payı (headroom buffer) eklenir:

$$BW_{buffer} = 19.45\text{ Gbps} \times 0.20 = 3.89\text{ Gbps}$$
$$BW_{toplam\_gerekli} = 19.45 + 3.89 = \mathbf{23.34\text{ Gbps}}$$

#### Neden 4x 10G LACP Metro Ethernet?

* $23.34\text{ Gbps}$ tepe yük, $2 \times 10\text{ Gbps} = 20\text{ Gbps}$ kapasiteyi aştığı için minimum **3 adet 10G link** ($30\text{ Gbps}$) gereklidir.
* **N+1 Link ve Servis Sağlayıcı Yedekliliği (Carrier Diversity):** Herhangi bir fiber hattın fiziksel kopması veya arayüz arızasında trafiğin kesilmemesi için **4 adet 10G SFP+ portu IEEE 802.3ad LACP altında birleştirilmiştir:**
  * Toplam Trunk Bant Genişliği: **$40\text{ Gbps}$**
  * Taşıyıcı Ayrımı: **2x 10G ULAKBİM** (Ulusal Akademik Ağ) + **2x 10G Türk Telekom Kurumsal Metro Ethernet**.
  * Bir servis sağlayıcı tamamen çökse dahi kalan 20-30 Gbps kapasite tüm kampüsün $23.34\text{ Gbps}$ yükünü sıfır paket kaybıyla taşımaya devam eder.

---

## 4. Güvenlik Politikası ve Mimari Analiz

### 4.1. Neden Eski Tip Stateful L4 Firewall ve Temel UTM'ler Tercih Edilmedi?

Kurumsal mimarimiz tasarlanırken klasik Port/IP bazlı Stateful L4 güvenlik duvarları ve giriş seviyesi UTM (Unified Threat Management) cihazları incelenmiş ve aşağıdaki teknik gerekçelerle reddedilmiştir:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      GELENEKSEL L4 vs. YENİ NESİL NGFW                      │
├──────────────────────────────────────┬──────────────────────────────────────┤
│    Geleneksel L4 Stateful Firewall   │       Palo Alto / Fortinet NGFW      │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ ❌ Port Körlüğü (Port 443 açık ise   │ ✔️ Katman 7 App-ID (Şifreli tünel    │
│    içinden akan zararlıyı göremez)   │    içindeki gerçek servisi tanır)    │
│ ❌ TLS 1.3 Teftişinde CPU Çökmesi    │ ✔️ Donanımsal Kriptografik Hızlandırıcı│
│    (Seri proxy kuyrukları %99 CPU)   │    ve SP3 / CP9 ile hat hızında teftiş│
│ ❌ Doğu-Batı (East-West) Körlüğü     │ ✔️ İç Ağ Mikro-Segmentasyonu ve       │
│    (Şube ve VLAN arası yayılım serbest) Zero-Trust L3/L7 İzolasyonu          │
│ ❌ Yalnızca IP Adresine Güven        │ ✔️ Kimlik Bazlı (User-ID/RBAC) ve     │
│    (IP spoofing saldırılarına açık)  │    Cihaz Sağlığı (Host Posture) Şartı│
└──────────────────────────────────────┴──────────────────────────────────────┘
```

1. **Port Körlüğü ve TLS 1.3 Gizlemesi:** Günümüz internet trafiğinin $\%95$'inden fazlası TLS ile şifrelidir. Geleneksel L4 güvenlik duvarı yalnızca TCP SYN-ACK durumunu ve port numarasını doğrular. Bir saldırgan `Port 443` üzerinden bir C2 (Command & Control) tüneli açtığında, veri sızdırdığında veya Cobalt Strike beacon çalıştırdığında L4 güvenlik duvarı bu trafiği "standart HTTPS" olarak algılayıp izin verir. PA-3410 ve FortiGate 1800F, App-ID ve Content-ID motorlarıyla paket içeriğini açıp teftiş eder.
2. **Klasik UTM'lerin "Proxy Chaining" Performans Darboğazı:** Geleneksel UTM cihazları mimari olarak bağımsız açık kaynak araçların (Snort, ClamAV, Squid vb.) bir araya getirilmesiyle çalışır. Paket her bir motora sırayla kopyalanır. 10.000 kullanıcılı bir ağda TLS teftişi açıldığında cihaz CPU'su dakikalar içinde $\%100$'e kilitlenir; cihaz ya trafiği kontrolsüz geçirir (fail-open) ya da tüm ağ trafiğini durdurur (fail-close). Fortinet'in CP9/NP7 donanımsal işlemcileri ve Palo Alto'nun Single-Pass motoru bu darboğazı ortadan kaldırır.
3. **Bulut WAF (Cloudflare vb.) Çözümlerinin Doğu-Batı Körlüğü:** Bulut WAF'lar yalnızca internetten kamuya açık sunuculara gelen (North-South) HTTP trafiğini süzer. Ancak bir üniversite veya holding yapısında en büyük tehdit; kampüsteki bir öğrenci cihazının ele geçirilerek idari işler veri tabanına, Ar-Ge GPU kümesine veya finans sunucusuna içeriden (East-West) saldırmasıdır. Bulut WAF bu iç trafiği kesinlikle göremez. Bu tehdit ancak ağ çekirdeğindeki dahili mikro-segmentasyon NGFW'leri ile engellenebilir.

### 4.2. Mikro-Segmentasyon ve Sıfır Güven (Zero-Trust) İlkeleri

Mimarimiz **NIST SP 800-207 Zero-Trust Architecture** standartları üzerine kurulmuştur:

* **Asla Güvenme, Her Zaman Doğrula (Never Trust, Always Verify):** Şirket veya kampüs ağı içinde olmak kimseye ayrıcalık tanımaz. Bir öğrencinin veya çalışanın fiziksel olarak kampüste bulunması, veri tabanlarına doğrudan erişebileceği anlamına gelmez.
* **Varsayılan Olarak Reddet (Default-Deny All):** Güvenlik duvarlarımızda açıkça tanımlanmamış her paket, kural tabanının en sonundaki `DENY ALL` kuralı tarafından sessizce düşürülür (drop) ve güvenlik operasyon merkezine (SOC) telemetri üretilir.
* **En Az Ayrıcalık İlkesi (Least Privilege Access):** Servis portları asla `any` olarak açılamaz; yalnızca işlevin gerektirdiği minimal portlar (örn. SQL için yalnızca 3306 veya 1433, web için 443) tanımlanır.
* **Ar-Ge AI Laboratuvarı Mutlak İzolasyonu (Air-Gapped Enclave):** NVIDIA DGX H100 GPU kümesinin ve fikri mülkiyet içeren model ağırlıklarının bulunduğu `10.50.0.0/16` bloğunun dış internetle (`0.0.0.0/0`) hiçbir fiziksel veya mantıksal çıkış kapısı yoktur. Veri aktarımı yalnızca atlama sunucusu (Jump Host) ve çift taraflı antivirüs teftişi altındaki SFTP DMZ üzerinden yürütülür.

---

## 5. Birleşik Kural Seti ve `company.json` Özeti

Projemizde yer alan tüm şubelerin (Ankara HQ, İstanbul, Londra, Kampüs, Yazılım, Ar-Ge) `kural-seti.md` dosyalarındaki kurallar derlenerek `firewall-lab-export/vanguard-holding/company.json` dosyasında birleştirilmiştir. 

Hocanın **"Her kuralın bir gerekçesi olmalı"** kuralına istinaden her bir kural nesnesi; `id`, `name`, `source`, `destination`, `ports`, `action` ve detaylı teknik `rationale` alanlarını içermektedir.

### Birleşik Güvenlik Politikaları Özeti (28 Kural)

| ID | Kural Adı | Kaynak CIDR | Hedef CIDR | Portlar | Eylem | Güvenlik Gerekçesi (Rationale) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **rule-01** | `ANK_HQ_DNS_NTP_CORE` | `10.10.30.0/24` | `10.10.100.10/32` | 53, 123 | PERMIT | Merkez çalışanlarının AD entegre güvenli DNS sorgulaması ve Kerberos kimlik doğrulaması için NTP zaman eşitlemesi. |
| **rule-02** | `ANK_FIN_TO_SWIFT_NET` | `10.10.20.10/32` | `194.107.240.0/24` | 443, 10000 | PERMIT | Finans biriminin uluslararası bankacılık ve fon transferlerini izole HSM terminali üzerinden güvenle yürütmesi. |
| **rule-03** | `ANK_FIN_TO_SAP_HANA` | `10.10.20.0/24` | `10.10.105.10/32` | 3200, 3300, 443, 30015 | PERMIT | Finans departmanının kritik ERP modüllerine ve Fiori arayüzüne finansal DLP teftişi altında kontrollü erişimi. |
| **rule-04** | `ANK_FIN_DIRECT_INET_BLOCK` | `10.10.20.0/24` | `0.0.0.0/0` | 0 | DENY | Finans iş istasyonlarının doğrudan kontrolsüz internete çıkışını engelleyerek veri sızıntısını ve fidye yazılımlarını önlemek. |
| **rule-05** | `ANK_MGMT_OOBM_RESTRICTED` | `10.10.10.0/24` | `10.10.99.0/24` | 22, 443 | PERMIT | Ağ ve sistem yöneticilerinin kritik ağ donanımlarının yönetim konsollarına yalnızca güvenli yönetim VLAN'ından erişmesi. |
| **rule-06** | `ANK_DEFAULT_DENY_ALL` | `0.0.0.0/0` | `0.0.0.0/0` | 0 | DENY | Ankara Genel Merkez omurgasında tanımlanmamış tüm doğu-batı ve kuzey-güney trafiği sıfır toleransla engellemek. |
| **rule-07** | `IST_BRANCH_M365_DIA_OUT` | `10.20.10.0/24` | `0.0.0.0/0` | 80, 443 | PERMIT | İstanbul satış ekiplerinin bulut SaaS uygulamalarına merkez VPN hattını boğmadan yerel ISP üzerinden doğrudan erişmesi. |
| **rule-08** | `IST_TO_ANK_INTRANET_VPN` | `10.20.10.0/24` | `10.10.100.0/24` | 80, 443, 445 | PERMIT | İstanbul şubesinin genel merkez intranet portalına ve kurumsal dosya sunucusuna şifreli IPsec VPN üzerinden erişimi. |
| **rule-09** | `IST_GUEST_ISOLATION_BLOCK`| `172.16.20.0/24` | `10.0.0.0/8` | 0 | DENY | İstanbul ofisindeki misafir kablosuz ağının şirket içi kurumsal ağlara, sunuculara ve yönetim arayüzlerine erişimini engellemek. |
| **rule-10** | `IST_GUEST_INTERNET_ACCESS`| `172.16.20.0/24` | `0.0.0.0/0` | 53, 80, 443 | PERMIT | Misafir kullanıcıların DNS ve web trafiğini kurumsal ağdan tamamen izole şekilde yerel fiber çıkışından yönlendirmek. |
| **rule-11** | `IST_DEFAULT_DENY_ALL` | `0.0.0.0/0` | `0.0.0.0/0` | 0 | DENY | İstanbul şube güvenlik duvarında eşleşmeyen tüm yetkisiz trafiği engellemek ve merkezi SOC'a raporlamak. |
| **rule-12** | `LON_LEGAL_CLOUD_AUDIT_OUT`| `10.30.10.0/24` | `0.0.0.0/0` | 443 | PERMIT | Londra hukuk ve fon yönetimi biriminin uluslararası denetim ve mevzuat portallarına TLS 1.3 DLP teftişiyle erişimi. |
| **rule-13** | `LON_TO_HQ_CORE_ERP_VPN` | `10.30.10.0/24` | `10.10.105.10/32` | 443, 30015 | PERMIT | Londra ofisinden Ankara merkezdeki SAP finans sunucusuna özel IPsec tüneli ve çift faktörlü doğrulama ile güvenli erişim. |
| **rule-14** | `LON_OOBM_REMOTE_ADMIN` | `10.30.99.0/24` | `10.10.99.10/32` | 22, 443 | PERMIT | Londra ağ ekipmanlarının Ankara merkez OOBM Jump Server üzerinden yedekli ve güvenli bant dışı yönetimi. |
| **rule-15** | `LON_DEFAULT_DENY_ALL` | `0.0.0.0/0` | `0.0.0.0/0` | 0 | DENY | Londra ofis ağında kural dışı kalan yetkisiz paketleri GDPR uyumluluğu gereği sessizce düşürmek. |
| **rule-16** | `CAMPUS_STUDENT_EDUROAM_NET`| `10.100.0.0/16` | `0.0.0.0/0` | 80, 443, 53 | PERMIT | 10.000 kampüs öğrencisinin yüksek hızlı internet, web gezintisi ve uzaktan eğitim kaynaklarına güvenli erişimini sağlamak. |
| **rule-17** | `CAMPUS_BLOCK_STUDENT_TO_ADMIN`| `10.100.0.0/16` | `10.101.20.0/24` | 0 | DENY | **[CRITICAL ZERO-TRUST]** Öğrenci ağından üniversite idari ve personel sistemlerine yetkisiz yatay geçişi kesin olarak engellemek. |
| **rule-18** | `CAMPUS_BLOCK_STUDENT_TO_LMS_DB`| `10.100.0.0/16`| `10.101.30.0/24` | 0 | DENY | **[CRITICAL ZERO-TRUST]** Öğrenci ağından LMS sınav ve not veri tabanı sunucularına doğrudan veri tabanı portu erişimini engellemek. |
| **rule-19** | `CAMPUS_STUDENT_TO_LMS_WEB` | `10.100.0.0/16` | `10.101.30.10/32`| 443 | PERMIT | Öğrencilerin sınav ve ders içeriklerine yalnızca DMZ üzerindeki WAF korumalı LMS Web arayüzü üzerinden erişmesini sağlamak. |
| **rule-20** | `CAMPUS_ACADEMIC_HPC_ACCESS`| `10.101.10.0/24`| `10.101.40.0/24` | 22, 8080, 8443 | PERMIT | Akademik personelin bilimsel araştırmalar ve simülasyonlar için HPC hesaplama kümesine güvenli erişimini sağlamak. |
| **rule-21** | `CAMPUS_DEFAULT_DENY_ALL` | `0.0.0.0/0` | `0.0.0.0/0` | 0 | DENY | Kampüs omurgasında tanımlanmamış tüm yetkisiz paketleri düşürmek ve DDoS/Botnet telemetrisini SIEM'e iletmek. |
| **rule-22** | `DEV_WORKSTATION_GITLAB_HARBOR`| `10.40.10.0/24`| `10.40.40.0/24` | 22, 443 | PERMIT | Yazılım mühendislerinin kaynak kod depolarına (GitLab) ve konteyner kayıt defterine (Harbor) SSH/HTTPS ile güvenli erişimi. |
| **rule-23** | `DEV_STAGING_TO_PROD_BLOCK` | `10.40.20.0/24` | `10.40.30.0/24` | 0 | DENY | **[SUPPLY-CHAIN ISOLATION]** Staging ve test ortamlarından canlı üretim (Prod) ortamına doğrudan ağ geçişini engellemek. |
| **rule-24** | `DEV_EGRESS_PACKAGE_INSPECT`| `10.40.40.0/24` | `0.0.0.0/0` | 443 | PERMIT | CI/CD yapım sunucularının npm/pip/maven bağımlılıklarını SandBlast tehdit emülasyonu altında indirmesini sağlamak. |
| **rule-25** | `RD_AI_ENCLAVE_NO_INTERNET` | `10.50.0.0/16` | `0.0.0.0/0` | 0 | DENY | **[AIR-GAPPED DEFENSE]** İleri seviye yapay zeka ve LLM ağırlıklarının bulunduğu araştırma kümesinin internet çıkışını mutlak olarak engellemek. |
| **rule-26** | `RD_RESEARCHER_TO_GPU_CLUSTER`| `10.50.10.0/24`| `10.50.20.0/24` | 22, 8888, 9090 | PERMIT | Araştırmacıların NVIDIA DGX H100 kümesinde derin öğrenme eğitimi için JupyterLab ve Slurm denetleyicisine erişimi. |
| **rule-27** | `RD_GPU_CLUSTER_TO_NVME_ROCE`| `10.50.20.0/24` | `10.50.30.0/24` | 2049, 4420 | PERMIT | H100 GPU kümesinin eğitim veri setlerini ultra düşük gecikmeyle okuması için NVMe-over-Fabrics depolama erişimi. |
| **rule-28** | `CORP_UNIVERSAL_DEFAULT_DENY`| `0.0.0.0/0` | `0.0.0.0/0` | 0 | DENY | Holding ve akademi genelinde eşleşmeyen tüm doğu-batı ve kuzey-güney trafiği için küresel Default-Deny bariyeri. |

---

## 6. Proje Doğrulama ve Otomasyon Entegrasyonu

Mimarideki tüm kurallar ve topoloji, projenin `tools/` katmanında yer alan yerel Python otomasyon motorlarıyla doğrulanmıştır:

* **Kural Doğrulayıcı (`tools/01-kural-dogrulayici-ve-analiz/policy_validator.py`):**
  * `rules_schema.json` üzerinden şema denetimi.
  * Öğrenci ağından idari sistemlere ve LMS DB'ye mikro-segmentasyon ihlallerini tespit eden denetim.
  * Any-to-Any ve Shadowing kural taraması.
  * Kural tabanının Default-Deny ile sonlandığının doğrulanması.
* **Vendor CLI Dönüştürücü (`tools/02-vendor-cli-donusturucu/vendor_exporter.py`):**
  * Kuralları tek tuşla **Fortinet FortiOS** (`config firewall policy`) veya **Palo Alto PAN-OS** (`set rulebase security rules`) CLI sözdizimine dönüştürme.
* **Kapasite ve QoS Motoru (`tools/03-kapasite-ve-qos-hesaplayici/bandwidth_engine.py`):**
  * $BW = N_{aktif} \times R_{limit} \times C_{overbooking}$ formülünü çalıştırarak 23.34 Gbps ve 4x 10G LACP çıktısını matematiksel olarak üreten simülasyon.
* **SOC Telemetri Simülatörü (`tools/04-soc-telemetri-simulatoru/syslog_generator.py`):**
  * RFC 5424 ve CEF standartlarında canlı syslog üretimi.
* **Merkezi Test Orkestratörü (`tools/05-otomasyon-test-merkezi/run_all_checks.py`):**
  * Tüm modülleri tek komutla test eden ve 6/6 başarı skoru üreten test süiti.

### Testleri Çalıştırma:

```powershell
# Kural doğrulaması ve güvenlik skor kartı:
python tools/01-kural-dogrulayici-ve-analiz/policy_validator.py --rules firewall-lab-export/vanguard-holding/company.json

# FortiOS CLI çıktılarını üretme:
python tools/02-vendor-cli-donusturucu/vendor_exporter.py --rules firewall-lab-export/vanguard-holding/company.json --target fortinet

# Palo Alto PAN-OS CLI çıktılarını üretme:
python tools/02-vendor-cli-donusturucu/vendor_exporter.py --rules firewall-lab-export/vanguard-holding/company.json --target paloalto

# 6 Adımlı tam entegrasyon testi:
python tools/05-otomasyon-test-merkezi/run_all_checks.py
```

---

> [!NOTE]
> Bu doküman ve beraberindeki `company.json`, Vanguard Holding & Academy kurumsal ağ ve güvenlik mimarisi projesinin hocanın `firewall-lab` kataloğuna doğrudan entegre edilebilmesi için tüm standartlara tam uyumlu olarak hazırlanmıştır.

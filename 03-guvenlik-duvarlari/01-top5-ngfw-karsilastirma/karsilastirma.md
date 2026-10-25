# Top 5 Kurumsal NGFW Kıyaslama ve Mimari Karar Matrisi

## 1. Yönetici Özeti ve Değerlendirilen Platformlar
Kurumsal holding ve üniversite mimarisinde uçtan uca ağ güvenliğini sağlamak amacıyla siber güvenlik pazarında lider 5 yeni nesil güvenlik duvarı (NGFW) ve kurumsal açık kaynak mimari derinlemesine incelenmiştir:
1. **Palo Alto Networks (PAN-OS / ML-Powered NGFW)**
2. **Fortinet (FortiOS / FortiGate)**
3. **Check Point Software Technologies (Quantum Security Gateway / Gaia OS)**
4. **Cisco Systems (Cisco Secure Firewall - Firepower / FPR Serisi)**
5. **Netgate (pfSense Plus & TNSR Enterprise)**

---

## 2. Kapsamlı Teknik ve Mimari Karşılaştırma Matrisi

| Karşılaştırma Kriteri | Palo Alto Networks (PA Serisi) | Fortinet (FortiGate) | Check Point (Quantum Serisi) | Cisco Secure Firewall (FPR) | Netgate (pfSense+ / TNSR) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Donanım Mimarisi** | Dedicated Dual-Plane (Control + Data Plane), FPGA + Multicore | Donanımsal Özel ASIC (Network NP7 + Content CP9 / SOC4) | Standart x86 Çok Çekirdekli Intel Mimarisi (CPUSE) | x86 Çok Çekirdekli + Donanımsal Kripto Hızlandırıcı | Standart x86 Intel/AMD İşlemciler (VPP / DPDK Hızlandırmalı) |
| **L4 Firewall Throughput** | 9.7 - 120+ Gbps | 20 - 198+ Gbps (ASIC Wire-Speed) | 7.4 - 100+ Gbps | 15 - 90+ Gbps | 10 - 40 Gbps (TNSR ile Yüksek Hız) |
| **Threat Prevention (Full DPI)**| **Mükemmel (Single-Pass SP3)** Sabit Düşük Gecikme | **Çok Yüksek (Düşük Maliyetli Gbps)** | **Yüksek (SandBlast & R81 Titan)** | Orta/İyi (Snort 3 Motoru) | Temel/Orta (Suricata / Snort Paketleri) |
| **SSL/TLS Decryption Gücü** | **Pazar Lideri** (Hardware Offload, TLS 1.3 tam destek) | **Çok Güçlü** (CP9 ASIC ile donanımsal el sıkışma) | Güçlü (Ancak CPU yükü artar) | Orta (Yüksek trafikte darboğaz riski) | Düşük/Orta (İşlemciye bağımlı, yazılımsal) |
| **Uygulama Tanıma (App-ID)** | **Pazar Standardı / Referans** (Porttan bağımsız, dinamik) | Çok Başarılı (FortiGuard ISDB & App Engine) | Başarılı (Application Control Blade) | Başarılı (OpenAppID / Cisco App Visibility) | Temel (Port/IP bazlı + L7 OpenAppID paketi) |
| **Zero-Day Tehdit Yakalama** | **WildFire ML Inline** (Sıfır gecikmeli bulut sandbox) | **FortiSandbox & AI Guard** | **SandBlast Zero-Day Protection** | Cisco Talos Threat Intelligence | Sınırlı (Harici Sandbox entegrasyonu gerekir) |
| **Merkezi Yönetim Konsolu** | **Panorama** (Hiyerarşik, Şablon ve Cihaz Grubu) | **FortiManager** (Tek Panel, Geniş Ekosistem) | **SmartConsole** (Nesne yönetiminde çok gelişmiş) | Cisco Security Cloud Control / FMC | pfSense WebGUI / TNSR CLI / REST API |
| **TCO ve Lisanslama Maliyeti**| **Yüksek (Premium Enterprise)** | **Düşük / Orta (En İyi Fiyat/Performans)** | **Orta / Yüksek** | **Orta / Yüksek** | **Çok Düşük (Düşük Lisans Maliyeti)** |

---

## 3. Platformların Detaylı Mimari İncelemesi

### 3.1. Palo Alto Networks (PAN-OS)
* **Güçlü Yönleri:** Patentli Single-Pass Parallel Processing (SP3) mimarisi sayesinde bir paket tek bir geçişte çözümlenir, imzalanır ve filtrelenir. Uygulama tanıma (App-ID), kullanıcı kimliği eşleme (User-ID) ve içerik teftişi (Content-ID) ayrıştırılamaz bir bütündür. Finansal veri teftişi, DLP ve Zero Trust HIP (Host Information Profile) doğrulamalarında rakipsizdir.
* **Kısıtları:** Satın alma (Capex) ve yıllık destek/lisans yenileme (Opex) maliyetleri oldukça yüksektir.

### 3.2. Fortinet (FortiGate)
* **Güçlü Yönleri:** Kendi geliştirdiği özel ASIC yongaları (NP7 ağ işlemcisi ve CP9 içerik işlemcisi) sayesinde gigabit başına en düşük maliyeti sunar. Çok yüksek oturum sayılarını (120M+) ve yeni bağlantı patlamalarını (CPS) ana CPU'yu hiç yormadan karşılar. Yerleşik SD-WAN motoru sektör lideridir.
* **Kısıtları:** GUI arayüzündeki konfigürasyon derinliği bazı karmaşık nesne hiyerarşilerinde Palo Alto ve Check Point kadar esnek olmayabilir; gelişmiş özellikler için CLI kullanımı şarttır.

### 3.3. Check Point Software (Quantum)
* **Güçlü Yönleri:** Güvenlik politikası nesne yönetiminde ve kural denetiminde (SmartConsole) altın standarttır. Gelişmiş tehdit istihbaratı (ThreatCloud) ve tersine mühendislik sandbox motoru (SandBlast) çok başarılıdır.
* **Kısıtları:** Özel ASIC yerine standart x86 sunucu mimarisine dayandığından, yoğun SSL/TLS trafiği altında CPU kullanımı hızla yükselebilir.

### 3.4. Cisco Secure Firewall (Firepower)
* **Güçlü Yönleri:** Dünyanın en büyük siber tehdit istihbarat ağı olan Cisco Talos tarafından beslenir. Snort 3 derin paket teftiş motoru ve Cisco Identity Services Engine (ISE) ile tam entegrasyon sağlar.
* **Kısıtları:** FMC (Firewall Management Center) hantal bir yapıya sahiptir; kural uygulama (policy deploy) süreleri diğer üreticilere kıyasla daha uzundur.

### 3.5. Netgate (pfSense Plus & TNSR)
* **Güçlü Yönleri:** Açık kaynak temelli (FreeBSD / Linux DPDK), donanım bağımsız ve lisans maliyeti yok denecek kadar düşüktür. TNSR, FD.io VPP mimarisi ile 40 Gbps yönlendirme yapabilir.
* **Kısıtları:** Kurumsal seviyede yerleşik L7 App-ID, merkezi kurumsal şablon yönetimi ve otomatik sıfırıncı gün sandboxing motorundan yoksundur; büyük ölçekli holding/üniversite yapısında bakım eforu aşırı yüksektir.

---

## 4. Hangi Şubeye Neden Atandığının Gerekçeli Matrisi

| Lokasyon / Birim | Seçilen Donanım Modeli | Atanma Nedeni ve Mimari Uyumu |
| :--- | :--- | :--- |
| **Ankara Genel Merkez** | **Palo Alto Networks PA-3410** | Finans, Hazine ve C-Level yöneticilerin kritik verilerini korumak için en gelişmiş L7 SP3 mimarisi, 4.3 Gbps SSL Decryption gücü ve merkezi Panorama orkestrasyonu. |
| **İstanbul Şubesi** | **Fortinet FortiGate 100F** | 150 personelin 500 Mbps DIA internet çıkışı için mükemmel Fiyat/Performans; SOC4 ASIC ile yerleşik SD-WAN dinamik yönlendirmesi ve donanımsal IPsec VPN hızlandırması. |
| **Londra Şubesi** | **Palo Alto Networks PA-440** | Akustik ofis gereksinimi için 0 dB tamamen fansız (fanless) kompakt gövde; Ankara PA-3410 ile %100 aynı nesne/politika mimarisi ve katı ZTNA / Geo-IP desteği. |
| **Akademik Kampüs** | **Fortinet FortiGate 1800F** | 10.000 öğrenci ve 20 Gbps hat için NP7 ASIC ile 120 Milyon eşzamanlı oturum desteği; 1.2 Milyon CPS yeni oturum oluşturma gücü ve 11 Gbps Threat Protection kapasitesi. |

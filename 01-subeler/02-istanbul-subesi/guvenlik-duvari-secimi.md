# İstanbul Şubesi - Güvenlik Duvarı (NGFW) Seçimi ve Mimari Analizi

## 1. Lokasyon Gereksinimleri ve Donanım Segmentasyonu
İstanbul Şubesi, 150 kurumsal kullanıcının yanı sıra yüksek hacimli SaaS trafiği (M365, Salesforce), Direct Internet Access (DIA) ve Ankara Hub merkezine 7/24 kesintisiz IPsec VPN tüneli gereksinimine sahiptir. Şubenin toplam bant genişliği 500 Mbps simetriktir.

Bu gereksinimler doğrultusunda **Fortinet FortiGate 100F** yeni nesil kurumsal güvenlik duvarı seçilmiştir.

---

## 2. Fortinet FortiGate 100F Teknik Özellikler ve Performans Parametreleri

| Teknik Parametre / Metrik | FortiGate 100F Değeri | Şube İhtiyacı (500 Mbps WAN / 150 Kullanıcı) | Yeterlilik & Güvenlik Marjı |
| :--- | :--- | :--- | :--- |
| **Firewall Throughput (L4 Enterprise)** | **20 Gbps** (1518 / 512 / 64 byte paketler) | 500 Mbps Peak | 40 Katı Kapasite (Sıfır Darboğaz) |
| **IPS Throughput (Kurumsal İmzalar)** | **2.6 Gbps** | 500 Mbps Peak | 5.2 Katı Kapasite |
| **NGFW Throughput (Firewall + App-ID + IPS)**| **1.6 Gbps** | 500 Mbps Peak | 3.2 Katı Kapasite |
| **Threat Protection (Tehdit Önleme - AV+IPS+App)**| **1.0 Gbps** (Full DPI) | 500 Mbps Peak | 2 Katı Güvenlik Marjı |
| **SSL/TLS Inspection (Derin Şifre Çözme)** | **1.0 Gbps** | 500 Mbps Peak | Tam Hat Hızında TLS 1.3 Teftişi |
| **IPsec VPN Throughput (512 Byte AES-256)** | **11.5 Gbps** | 100-200 Mbps Hub Tüneli | 50 Katı Donanımsal Kripto Gücü |
| **Eşzamanlı Oturum Kapasitesi (Concurrent Sessions)**| **1.500.000 (1.5 Milyon)** | ~30.000 Oturum Peak | 50 Katı Oturum Havuzu |
| **Yeni Oturum Hızı (New Sessions/sec)** | **56.000 CPS** | ~1.500 CPS Peak | Ani Bağlantı Artışlarına Tam Dayanım |
| **Fiziksel Port Yapısı** | 2x 10GE SFP+ Yuvası, 8x GE SFP, 12x GE RJ45, 2x GE WAN | 2x WAN RJ45, 2x SFP Trunk Switch | Yüksek Esneklik ve 10G Omurga Hazırlığı |
| **İşlemci Mimarisi** | **FortiASIC SOC4 (System-on-a-Chip 4)** | Donanımsal Hızlandırma | CP9 (Kripto) + NP6XLite (Ağ) Birleşik Çip |

---

## 3. Seçilme Nedenleri ve Mimari Gerekçeler

### 3.1. Yerleşik SD-WAN ASIC (FortiASIC SOC4) Mimarisi
Geleneksel x86 işlemcili güvenlik duvarları, SD-WAN rota hesaplamalarını, paket sağlığı (jitter/loss) ölçümlerini ve IPsec şifrelemeyi genel işlemci (CPU) üzerinde gerçekleştirir. Bu durum hat kullanımının %70'in üzerine çıktığı anlarda CPU darboğazına ve paket gecikmelerine yol açar.
FortiGate 100F üzerindeki patentli **SOC4 ASIC çipi**, SD-WAN tünel yönlendirmesini ve IPsec kriptografisini doğrudan donanım seviyesinde (wire-speed) icra eder. Bu sayede 500 Mbps hat hızında dahi gecikme 1 milisaniyenin altında kalır.

### 3.2. Yüksek SSL/TLS Decryption Throughput (1.0 Gbps)
Pazarlama ve satış ekiplerinin tüm trafiği HTTPS üzerindedir. FortiGate 100F'in içerisindeki CP9 kripto işlemcisi, SSL el sıkışmalarını ve asimetrik şifre çözme işlemlerini ana CPU'ya yük bindirmeden çözer. 1.0 Gbps SSL inspection kapasitesi, 500 Mbps WAN hattının tamamını derinlemesine incelemek için tam uyumludur.

### 3.3. Fiyat / Performans ve Fortinet Güvenlik Ekosistemi (Security Fabric)
İstanbul ofisinde konumlandırılan FortiSwitch ve FortiAP cihazları, FortiLink protokolü ile doğrudan FortiGate 100F arayüzünden tek bir cam panel (Single Pane of Glass) üzerinden yönetilir. İlave kablosuz kontrolcü (WLC) veya switch lisansı gerektirmeden tam entegre bir şube çözümü sağlar.

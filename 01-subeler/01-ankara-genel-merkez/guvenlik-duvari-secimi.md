# Ankara Genel Merkez - Güvenlik Duvarı (NGFW) Seçimi ve Mimari Analizi

## 1. Değerlendirilen Modeller ve Lokasyon İhtiyacı
Ankara Genel Merkezi, toplamda 2 Gbps agregasyon kapasitesine sahip çift aktif Metro Ethernet hattını sonlandırmakta, 300 personelin yanı sıra İstanbul, Londra ve Kampüs şubelerinden gelen IPsec VPN tünellerine Hub görevi yapmaktadır. Bu merkezde hassas finansal verilerin işlenmesi, SWIFT bağlantıları ve ERP omurgası yer aldığından; L7 uygulama denetimi, SSL/TLS şifre çözme (decryption) ve sıfırıncı gün (Zero-Day) tehdit önleme motorlarının tam kapasitede devreye alınması şarttır.

Bu doğrultuda kurumsal seviyede iki öncü model kıyaslanmıştır:
1. **Palo Alto Networks PA-3410**
2. **Check Point Quantum 6600**

---

## 2. Teknik ve Performans Karşılaştırma Matrisi

| Parametre / Metrik | Palo Alto Networks PA-3410 | Check Point Quantum 6600 Security Gateway | Değerlendirme & Gereksinim Uyumu |
| :--- | :--- | :--- | :--- |
| **Ham Güvenlik Duvarı Throughput (App-ID)**| **9.7 Gbps** (HTTP/App-ID açık) | **7.4 Gbps** (Firewall test paketi) | PA-3410, L7 kurallarda %31 daha yüksek verim sunar. |
| **Tehdit Önleme (Threat Prevention) Throughput**| **6.1 Gbps** (AV, IPS, WildFire, DNS) | **3.7 Gbps** (Enterprise Threat Prevention paketi) | Ankara peak yükü (1.2G) için her ikisi de yeterli; PA-3410 daha geniş tepe boşluğu sağlar. |
| **SSL/TLS Decryption Throughput** | **4.3 Gbps** (TLS 1.3 / AES-256-GCM) | **2.5 Gbps** (HTTPS Inspection) | Finansal veri teftişi için PA-3410 belirgin şekilde üstündür. |
| **IPsec VPN Throughput** | **5.5 Gbps** (AES-256, SHA-256) | **3.3 Gbps** (AES-GCM-128) | Şubeler arası Hub tünel trafiğinde PA-3410 daha dayanıklıdır. |
| **Eşzamanlı Oturum Kapasitesi (Concurrent Sessions)** | **1.600.000 (1.6 Milyon)** | **1.500.000 (1.5 Milyon)** | Her iki model de merkez için fazlasıyla yeterlidir. |
| **Yeni Oturum Hızı (New Sessions/sec)** | **93.000 CPS** | **85.000 CPS** | PA-3410 ani bağlantı patlamalarını daha rahat yönetir. |
| **İşlemci / Donanım Mimarisi** | SP3 Donanım: Dedicated Control Plane + Data Plane multi-core işlemciler | Çok çekirdekli x86 Intel platformu (CPUSE tabanlı Gaia OS) | PA tek-geçişli mimari gecikmeyi sabit tutar (Zero-Buffer latency). |
| **Fiziksel Port Yapısı** | 12x 10/100/1000 RJ45, 4x 1G/10G SFP+ | 10x 10/100/1000 RJ45, 4x 1G/10G SFP+ | Fiber Metro WAN ve 10G Core LACP için eşit esneklik. |
| **Merkezi Yönetim Konsolu** | **Panorama** (Hiyerarşik Device-Group & Template) | **SmartConsole / Smart-1 Cloud** | Her iki çözüm de kurumsal düzeyde mükemmel yönetim sağlar. |

---

## 3. Nihai Tercih ve Mimari Seçilme Gerekçeleri

Yapılan detaylı kıyaslama sonucunda **Ankara Genel Merkezi için Palo Alto Networks PA-3410** modeli seçilmiştir (Active/Passive HA Kümesi - 2 Adet).

### 3.1. Single-Pass Parallel Processing (SP3) Mimarisi
Palo Alto'nun patentli SP3 mimarisi, ağ paketini yalnızca bir defa açıp inceler. Paket hafızaya alındığında eşzamanlı olarak:
* App-ID (Uygulama tanımlama),
* User-ID (Active Directory kullanıcı kimliği eşleştirme),
* Content-ID (IPS, Anti-Virüs, DLP ve WildFire analizi)
tek bir operasyonda gerçekleştirilir. Check Point mimarisinde paketlerin farklı yazılımsal blade'lerden (Software Blades) sıralı geçmesi, derin şifre çözme (SSL Inspection) altında gecikmeyi (jitter) artırabilmektedir.

### 3.2. Yüksek SSL/TLS Decryption Gücü (4.3 Gbps)
Kurumsal finans ve operasyon trafiğinin %90'ından fazlası TLS 1.2 ve TLS 1.3 ile şifrelidir. Finans departmanından çıkan verilerde veri sızıntısını (DLP) denetlemek ve kötü amaçlı yazılımların şifreli tüneller üzerinden içeri sızmasını önlemek için PA-3410'un 4.3 Gbps SSL Decryption gücü, hat doygunluğu anında dahi hiçbir donanımsal darboğaza izin vermez.

### 3.3. Merkezi Kural Yönetimi ve Panorama Entegrasyonu
İstanbul, Londra ve Kampüs şubeleri ile birlikte tüm holding ağı tek bir **Panorama M-200** sanal/fiziksel konsolu üzerinden yönetilecektir. PA-3410, şube politikalarının merkezden devralınması (`Device-Group hierarchy`), kuralların etiketlenmesi (`Tag-based dynamic address groups`) ve kural denetiminde endüstri standardı olan Zero Trust visibility sağlamaktadır.

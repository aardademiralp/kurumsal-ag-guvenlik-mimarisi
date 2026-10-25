# Londra Şubesi - Güvenlik Duvarı (NGFW) Seçimi ve Donanım Analizi

## 1. Lokasyon Kısıtları ve Değerlendirilen Modeller
Londra ofisinde dedicated büyük bir veri merkezi bulunmamaktadır; kabinet açık ofis ve üst düzey toplantı odalarına yakın bir alanda yer almaktadır. Bu sebeple donanım seçimi iki temel kritere dayanır:
1. **Akustik ve Fiziksel Standart:** Fansız (Fanless), tamamen sessiz (0 dB gürültü seviyesi), kompakt form faktörü ve düşük ısı yayılımı.
2. **Kurumsal Güvenlik Yeteneği:** Ankara Genel Merkezi ile tam kural/politika uyumu (Panorama entegrasyonu), gelişmiş SSL decryption, katı Geo-IP ve ZTNA motoru.

Bu segmentte iki kurumsal model kıyaslanmıştır:
1. **Palo Alto Networks PA-440**
2. **Fortinet FortiGate 70F**

---

## 2. Teknik ve Performans Karşılaştırma Matrisi

| Parametre / Metrik | Palo Alto Networks PA-440 | Fortinet FortiGate 70F | Londra Lokasyon İhtiyacı |
| :--- | :--- | :--- | :--- |
| **Gürültü Seviyesi (Akustik)** | **0 dBA (Tamamen Fansız - Sessiz)** | **0 dBA (Tamamen Fansız - Sessiz)** | Kritik (Ofis içi kabinet için sıfır gürültü şartı) |
| **Güvenlik Duvarı Throughput** | **3.0 Gbps** | **10.0 Gbps** | 300 Mbps hat için her ikisi de aşırı yeterli |
| **Threat Prevention Throughput** | **1.9 Gbps** (Tam DPI / WildFire) | **800 Mbps** | PA-440, tehdit önleme altında daha yüksek headroom sunar |
| **SSL/TLS Decryption Throughput** | **1.2 Gbps** | **520 Mbps** | PA-440 derin şifre çözmede belirgin avantajlı |
| **IPsec VPN Throughput** | **1.6 Gbps** | **6.4 Gbps** | Şube tüneli (100-300M) için her ikisi fazlasıyla yeterli |
| **Eşzamanlı Oturum Kapasitesi** | **200.000 Oturum** | **700.000 Oturum** | 50 kullanıcı için 200k oturum fazlasıyla geniştir |
| **Yeni Oturum Hızı (CPS)** | **39.000 CPS** | **35.000 CPS** | Eşit seviyede yüksek performans |
| **Merkezi Yönetim Ekosistemi** | **Panorama M-200** (Ankara ile %100 aynı nesne ve kural mimarisi) | **FortiManager** (Ankara Palo Alto olduğu için ek konsol gerektirir) | PA-440 operasyonel homojenlik sağlar |
| **Sıfır Dokunuşla Kurulum (ZTP)**| **Palo Alto Cloud ZTP** | **FortiDeploy / FortiCloud ZTP** | Her iki cihaz da uzaktan sıfır dokunuş destekler |

---

## 3. Nihai Tercih ve Mimari Seçilme Gerekçeleri

Yapılan değerlendirme neticesinde **Londra Şubesi için Palo Alto Networks PA-440** seçilmiştir.

### 3.1. Ankara Hub ile Kusursuz Mimari Homojenlik
Ankara Genel Merkezinde Palo Alto PA-3410 kullanıldığından, Londra'da PA-440 tercih edilmesi merkezi güvenlik yönetimini (**Panorama**) olağanüstü basitleştirir. 
* Aynı Güvenlik Nesneleri (Security Objects),
* Aynı Dinamik Kullanıcı Grupları (User-ID Tagging),
* Tek tıkla Ankara ve Londra kurallarının teftiş edilmesi ve tek noktadan uyum denetimi sağlanır.

### 3.2. Fansız (Fanless) Termal Tasarım ve Dayanıklılık
PA-440, gövdesinin tamamını pasif soğutucu (heatsink) olarak kullanan fansız bir endüstriyel tasarıma sahiptir. Hareketli parça (fan) bulunmadığından:
* Mekanik fan arızası riski sıfırdır (Mean Time Between Failures - MTBF son derece yüksektir).
* Canary Wharf ofisinde sıfır desibel gürültü ile çalışır, toplantı odalarına hiçbir akustik parazit yaymaz.

### 3.3. 1.2 Gbps SSL Decryption ve Gelişmiş ZTNA Motoru
Hukuk ve ticaret ekibinin tüm doküman akışı TLS 1.3 şifreli portallar üzerinden gerçekleşir. PA-440'ın 1.2 Gbps SSL inceleme gücü, 300 Mbps hattın tamamını donanım gecikmesi yaşamadan teftiş etmesini sağlar.

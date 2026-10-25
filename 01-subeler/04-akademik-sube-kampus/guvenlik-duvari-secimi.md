# Akademik Şube ve Kampüs - Güvenlik Duvarı (NGFW) Seçimi ve Mimari Analizi

## 1. Kampüs Boyutlandırma Kriterleri ve Donanım İhtiyacı
Üniversite kampüsü 4.000 eşzamanlı aktif cihaz, 10.000 kayıtlı öğrenci ve 20 Gbps fiziksel hat kapasitesi (2x 10G LACP) barındırmaktadır. Bu ölçekteki bir yapıda güvenlik duvarının aşağıdaki teknik eşikleri kayıpsız karşılaması şarttır:
1. **Tehdit Önleme (Full DPI / Threat Prevention) Throughput:** En az 10 Gbps gerçek hat hızında (Full IPS + AV + App-ID aktifken).
2. **Eşzamanlı Oturum Kapasitesi (Concurrent Sessions):** Öğrenci mobil cihazları arka planda yüzlerce eşzamanlı TCP/UDP bağlantısı açtığından en az 5-10 milyon aktif oturum desteği.
3. **Yeni Oturum Hızı (Connections Per Second - CPS):** Teneffüs ve ders başlangıçlarında anlık yüz binlerce oturum açılışını yönetebilme.

Bu doğrultuda kurumsal pazarın en güçlü iki çözümü kıyaslanmıştır:
1. **Fortinet FortiGate 1800F**
2. **Palo Alto Networks PA-5450 (Modüler Kasa Mimarisi)**

---

## 2. Teknik ve Performans Karşılaştırma Matrisi

| Parametre / Metrik | Fortinet FortiGate 1800F | Palo Alto Networks PA-5450 (1x DPC + 1x NPC) | Kampüs Gereksinimi (10 Gbps Full Load) |
| :--- | :--- | :--- | :--- |
| **Firewall Throughput (L4)** | **198 Gbps** (1518 byte UDP/TCP) | **120 Gbps** | Her ikisi de hat hızının çok ötesindedir |
| **IPS Throughput (Kurumsal İmzalar)** | **19 Gbps** | **55 Gbps** | Her ikisi de 10 Gbps hedefini rahatlıkla aşar |
| **NGFW Throughput (FW + App + IPS)**| **17 Gbps** | **45 Gbps** | 10 Gbps kampüs trafiği için her ikisi tam yeterli |
| **Threat Prevention Throughput (Full DPI)**| **11 Gbps** (AV + IPS + App + Sandbox) | **38 Gbps** | FortiGate sınırda (%10 marj), Palo Alto yüksek tepe payı sunar |
| **SSL/TLS Decryption Throughput** | **8.0 Gbps** | **20 Gbps** | Palo Alto şifre çözmede belirgin üstündür |
| **Eşzamanlı Oturum Kapasitesi** | **120 Milyon Oturum** | **20 Milyon Oturum** | FortiGate Hyperscale oturum havuzunda liderdir |
| **Yeni Oturum Hızı (CPS)** | **1.200.000 CPS (1.2 Milyon)** | **520.000 CPS** | FortiGate öğrenci yoğunluğunda üstündür |
| **Donanım ve İşlemci Mimarisi** | **NP7 (Network Processor 7) + CP9 (Content Processor 9)** Dedicated ASIC | Modüler Şasi (DPC Veri İşlem Kartı + NPC Ağ Kartı + MPC Yönetim) | FortiGate sabit 2U, Palo Alto 5U modüler şasi |
| **Fiziksel Port Yapısı** | 4x 40GE QSFP+, 24x 25GE/10GE SFP28, 8x GE RJ45 | 4x 100G/40G QSFP28, 12x 10G/25G SFP28 | Her iki cihaz da 10G ve 40G/100G uplink destekler |
| **TCO ve Lisanslama Maliyeti** | **Ekonomik / Yüksek Fiyat-Performans** | **Yüksek Kurumsal Yatırım (High Capex)** | FortiGate akademik bütçe için %45 daha avantajlıdır |

---

## 3. Nihai Tercih ve Mimari Gerekçeler

Yapılan kapsamlı değerlendirme sonucunda **Akademik Kampüs Omurgası için Fortinet FortiGate 1800F** modeli seçilmiştir (Active/Passive HA Kümesi - 2 Adet).

### 3.1. NP7 Network Processor ASIC ile 120 Milyon Eşzamanlı Oturum
Kampüslerdeki en büyük tehdit, öğrencilerin torrent, P2P veya mobil uygulamalarla güvenlik duvarının durum tablosunu (State Table) tüketmesidir. FortiGate 1800F'in içerisindeki 7. Nesil Ağ İşlemcisi (**NP7 ASIC**), oturum oluşturma ve durum izlemeyi doğrudan donanıma alarak 120 milyon oturumu ana CPU'yu hiç yormadan yönetir.

### 3.2. 1.2 Milyon CPS (Yeni Oturum Hızı)
Ders bitiminde 10.000 öğrencinin aynı anda telefonlarını açması durumunda meydana gelen anlık oturum patlamaları (Session Spikes), geleneksel x86 mimarili sistemleri kilitlerken, NP7 ASIC donanımsal session-setup motoru ile sıfır paket kaybı sağlar.

### 3.3. 11 Gbps Full Threat Protection ve 8 Gbps SSL Teftişi
10 Gbps'lik kampüs internet çıkışının tamamı antivirüs, saldırı engelleme (IPS) ve botnet filtrelemesinden hat hızında geçirilir.

### 3.4. Yüksek Yoğunluklu 25G/40G Uplink Desteği
Cihaz üzerinde yer alan 40GE QSFP+ ve 25GE SFP28 portları, Cisco Catalyst 9600 kampüs omurga anahtarlarına 40G agregasyonla doğrudan bağlanmaya olanak tanır.

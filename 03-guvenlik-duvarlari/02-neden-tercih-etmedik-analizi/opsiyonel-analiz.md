# Neden Tercih Etmedik? - Mimari Risk ve Alternatif Değerlendirme Analizi

Bu analiz, kurumsal holding ve 10.000 öğrencili üniversite ağ ve güvenlik altyapısı projesinde değerlendirilen ancak güvenlik açığı, donanımsal yetersizlik veya mimari kapsamsızlık sebebiyle **tercih edilmeyen** yaklaşımların teknik ve operasyonel nedenlerini açıklar.

---

## 1. Geleneksel Durum Korumalı (Stateful L4) Güvenlik Duvarları

### 1.1. Teknik Yetersizlik ve Riskler
Geleneksel stateful güvenlik duvarları (Legacy L4 Firewalls - örn: Cisco ASA 5500 eski nesil, standart iptables), kararlarını yalnızca OSI Katman 3 (IP adresleri) ve Katman 4 (TCP/UDP portları ve TCP bayrakları) seviyesinde verir.

* **Port Tabanlı Filtrelemenin Çöküşü:** Günümüz siber saldırıları ve modern uygulamaları standart portlar (özellikle TCP 80 ve TCP 443) üzerinden tünelleme yapar. Örneğin bir saldırgan, komuta kontrol (C2) trafiğini veya veri sızıntısını (exfiltration) TCP 443 (HTTPS) üzerinden dışarı taşırken, L4 firewall bunu "yasal HTTPS trafiği" olarak kabul edip geçirir.
* **Protokol Atlatma (Evasion Techniques):** BitTorrent, Tor veya DNS tünelleme yazılımları, engellenen portlar yerine dinamik rastgele portlar veya standart HTTP/DNS portları kullanarak L4 kurallarını kolaylıkla atlatır.
* **10.000 Öğrencili Kampüste Körlük:** L4 bir güvenlik duvarı amfideki bir öğrencinin port 443 üzerinden bilimsel bir makale mi okuduğunu, yoksa telif hakkı ihlali yapan bir torrent istemcisi mi çalıştırdığını ayırt edemez. Katman 7 Derin Paket İnceleme (DPI) ve App-ID olmadan 10 Gbps kampüs trafiğini yönetmek imkansızdır.

---

## 2. Düşük Segment / KOBİ Tipi UTM Cihazları

### 2.1. "Hepsi-Bir-Arada" (All-in-One) CPU Mimarisinin Çöküşü
Piyasada küçük işletmeler (KOBİ) için üretilmiş düşük segment Birleşik Tehdit Yönetimi (UTM) cihazları, tüm güvenlik özelliklerini (Antivirüs, IPS, İçerik Filtreleme, VPN) tek bir düşük maliyetli genel amaçlı x86/ARM işlemci üzerinde yazılımsal olarak yürütür.

* **SSL/TLS Decryption Felaketi:** Modern web trafiğinin %90'ından fazlası TLS 1.3 ile şifrelidir. Düşük segment bir UTM cihazında "Derin SSL Şifre Çözme (Deep SSL Inspection)" fonksiyonu açıldığı anda:
  1. Asimetrik RSA/ECC kriptografik anahtar çözme işlemleri genel CPU'yu saniyeler içinde %100 doygunluğa (CPU starvation) ulaştırır.
  2. Cihazın veri aktarım hızı nominal 1 Gbps'den 40-50 Mbps seviyelerine çakılır.
  3. Cihaz bellek yetersizliğinden oturumları düşürür (Kernel Panic / Fail-Open veya Fail-Close) ve tüm şube interneti kilitlenir.
* **Özel Hızlandırma Yongalarının (ASIC) Bulunmaması:** Palo Alto'nun dedicated kontrol/veri mimarisi veya Fortinet'in donanımsal NP7/CP9 ASIC çipleri bulunmayan sistemler, kurumsal peak yükleri ve anlık CPS patlamalarını karşılayamaz.

---

## 3. Salt Bulut Tabanlı WAF (Cloud-Only WAF / CDN Çözümleri)

### 3.1. Kapsam ve Koruma Alanı Kısıtı
Cloudflare WAF, AWS WAF veya Akamai gibi bulut Web Uygulama Güvenlik Duvarları (Cloud WAF), web sunucularına gelen HTTP/HTTPS (L7 Web) isteklerini filtrelemede son derece başarılıdır. Ancak tek başına bir kurumsal güvenlik mimarisinin yerini tutamazlar:

* **Sadece Web Katmanı (HTTP/S) Koruması:** Cloud WAF, kurumsal ağın ihtiyaç duyduğu diğer kritik protokolleri koruyamaz:
  - Active Directory Kerberos/LDAP iletişimi,
  - SAP RFC ve HANA veri tabanı replikasyonları,
  - VoIP SIP/RTP ses trafiği,
  - Şubeler arası IPsec/BGP yönlendirme protokolleri.
* **İç Ağ Tehditleri ve Yanal İlerleme (Lateral Movement) Körlüğü:**
  - Bir çalışan, taşınabilir cihazına bulaşan bir fidye yazılımı (Ransomware) ile kampüs içindeki bir laboratuvara veya finans VLAN'ına sızdığında, bu trafik buluta hiç çıkmaz; yerel anahtarlar ve yönlendiriciler üzerinden akar.
  - Salt Bulut WAF, yerel ağ segmentasyonunu, VLAN izolasyonunu ve Doğu-Batı (East-West) trafiğini denetleyemez. Bir saldırgan kampüs ağına ayak bastığı anda tüm sunuculara iç ağdan savunmasızca yayılabilir.
* **Zero Trust ve Kampüs Sınır Güvenliği:** Kampüs ve şube sınırlarında fiziksel kabloyu terminasyon eden, 802.1X/RADIUS kontrolü yapan ve donanımsal şifreleme sunan yerel bir NGFW kümesi kurumsal yapılar için vazgeçilmez bir zorunluluktur.

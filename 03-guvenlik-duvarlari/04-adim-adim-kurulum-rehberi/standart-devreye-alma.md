# Standart Kurumsal NGFW Devreye Alma ve Kurulum Metodolojisi

Bu rehber, holding bünyesindeki tüm şubelerde (Ankara HQ, İstanbul, Londra, Kampüs) konumlandırılan tüm Palo Alto Networks ve Fortinet güvenlik duvarları için geçerli olan standart 8 aşamalı kurulum metodolojisini tanımlar.

---

## Aşama 1: Fabrika Ayarları ve Üretim Firmware Baseline Güncellemesi
Kutudan yeni çıkan cihazlar doğrudan üretim ağına bağlanamaz.
1. Cihaz izole bir test laboratuvarında konsol portu ile başlatılır.
2. Fabrika ön tanımlı sertifikaları ve varsayılan parolalar (admin/admin vb.) sıfırlanır.
3. Cihazın işletim sistemi holding standart baseline sürümüne yükseltilir:
   - **Palo Alto Networks:** PAN-OS 11.1.x Target Preferred Release (TAC Onaylı LTS Sürümü).
   - **Fortinet:** FortiOS 7.4.x Mature Enterprise Branch.
4. Dinamik içerik güncelleme paketleri (App-ID imzaları, Antivirüs ve IPS veritabanı) en son sürüme güncellenir.

---

## Aşama 2: Out-of-Band Management (OOBM) ve Cihaz Sıkılaştırma (Hardening)
1. Cihazın `MGT` arabirimi şubenin izole OOBM VLAN'ına (VLAN 99 / 199 / 299 / 399) atanır.
2. Güvenli Yönetim Protokolleri:
   - Yalnızca TLS 1.3 destekli HTTPS ve SSHv2 (AES-256-CTR, Ed25519) aktif edilir.
   - Telnet, HTTP ve zayıf şifreleme algoritmaları global olarak kapatılır.
3. Yönetici Erişim Kısıtlaması (Permitted IPs):
   - Yönetim paneline yalnızca Ankara BT Bastion Host IP'si (`10.10.30.5`) ve OOBM jumpbox'ından erişilebilecek şekilde IP erişim listesi (ACL) tanımlanır.
4. Merkezi Kimlik Doğrulama:
   - RADIUS / TACACS+ ve SAML 2.0 (Azure AD / Okta MFA) entegrasyonu tamamlanır.

---

## Aşama 3: Güvenlik Bölgeleri (Zones) ve Arabirimlerin (LACP/Routed) Tanımlanması
1. Fiziksel uplink ve downlink arayüzleri IEEE 802.3ad LACP Port-Channel olarak yapılandırılır (`lacp-mode active`, `lacp-rate fast`).
2. 802.1Q alt-arayüzleri (Sub-interfaces) açılarak ilgili VLAN ID'leri etiketlenir.
3. Her alt-arayüz, kurumsal zone mimarisine uygun olarak ilgili Güvenlik Bölgesine (`Trust`, `Untrust`, `DMZ`, `Student`, `Mgmt`) bağlanır.

---

## Aşama 4: Yüksek Erişilebilirlik (HA - Active/Passive) Kümeleme
1. Birincil ve ikincil cihazlar arasında dedike `HA1` (Kontrol/Heartbeat) ve `HA2` (State Sync/Oturum Eşleme) kabloları takılır.
2. HA parametreleri işlenir:
   - Primary Node Priority: `90` (Öncelikli Aktif), Secondary Node Priority: `100`.
   - Preemption: `Disabled` (Trafiğin gereksiz yere geri dönerek mikro kesinti yaşatmasını önlemek için).
   - Link ve Path İzleme: Dış WAN ve iç omurga linkleri izlemeye alınır (`Interface Monitoring`).

---

## Aşama 5: Statik ve Dinamik (BGP / OSPF) Yönlendirme Yapılandırması
1. **İç Ağ Yönlendirmesi (OSPFv2):** Core switch kümesi ile Point-to-Point L3 transit subnet üzerinde OSPF Area 0 komşuluğu kurulur.
2. **Dış Ağ Yönlendirmesi (eBGP):** Servis sağlayıcılar (ISP) ile eBGP peering oturumları açılır; holdinge ait IP blokları duyurulur.
3. **SD-WAN Sağlık Kontrolleri:** Harici DNS sunucularına (`1.1.1.1`, `8.8.8.8`) ve Ankara Hub IP'sine her 1000 ms'de bir ping/HTTP probu gönderilerek gecikme, jitter ve paket kaybı canlı izlenir.

---

## Aşama 6: Temel Tehdit Önleme ve Güvenlik Profillerinin Açılması
1. **Antivirüs / Anti-Malware Profili:** Tüm HTTP, FTP, SMB ve e-posta akışlarında gerçek zamanlı akış tabanlı virüs taraması devreye alınır.
2. **Saldırı Engelleme (IPS):** "Strict-High-Severity" kural profili seçilerek CVSS skoru $\ge 7.0$ olan bilinen zafiyet denemeleri doğrudan bloklanır (`reset-both`).
3. **Anti-Bot ve DNS Güvenliği:** Bilinen komuta kontrol (C2) sunucularına giden DNS sorguları ve DGA (Domain Generation Algorithm) alan adları engellenir.
4. **SSL/TLS Decryption:** Finans ve operasyon VLAN'ları için kurumsal CA sertifikası dağıtılarak gelen/giden web trafiğinde derin şifre çözme aktif edilir (Bankacılık ve sağlık hariç tutulur).

---

## Aşama 7: Loglama ve Merkezi SIEM Yönlendirmesi
1. Tüm kural setlerinde loglama `Log at Session End` olarak ayarlanır; düşen (drop) paketlerde alarm üretilir.
2. Güvenli Log İletimi:
   - Syslog mesajları TLS şifreli olarak Port 6514 üzerinden merkezi SIEM (Splunk / Elastic Security) kümesine yönlendirilir.
   - NetFlow v9 / IPFIX akışları akış toplayıcılarına (Flow Collectors) gönderilir.

---

## Aşama 8: Kullanıcı Kabul Testleri (UAT) ve Canlıya Geçiş (Cutover)
1. **İkili Doğrulama (Sign-Off):** Bakım penceresinde canlı trafik yeni firewall'a aktarılır.
2. **UAT Test Senaryoları:**
   - [ ] ERP / SAP veritabanı bağlantısı başarılı mı?
   - [ ] 802.1X sertifikalı istemciler doğru VLAN'a düşüyor mu?
   - [ ] Misafir ağından şirket içi sunuculara ping atıldığında engelleniyor mu?
   - [ ] HA failover testi: Birincil cihazın fişi çekildiğinde oturumlar kesilmeden yedek cihaza aktarılıyor mu? (Kayıp $\le 1$ paket).
3. Testler onaylandıktan sonra canlıya geçiş tamamlanır; 24 saatlik izleme fazına geçilir.

# Kurumsal Güvenlik Politikası, Zone Hiyerarşisi ve Sıfır Güven Standartları

## 1. Temel Güvenlik Felsefesi ve Mimari Standartlar
Kurumsal holding ve üniversite ağ altyapısının tüm bileşenlerinde üç temel güvenlik ilkesi istisnasız olarak uygulanır:

1. **Varsayılan Olarak Engelle (Default-Deny):**
   * Açıkça izin verilmemiş olan her protokol, port, IP ve uygulama akışı güvenlik duvarı kurallarının en altında yer alan nihai kural (`Rule 999: EXPLICIT_DENY_ALL`) ile sessizce veya loglanarak engellenir.
2. **En Az Ayrıcalık Prensibi (Least Privilege):**
   * Kullanıcılara ve sistem servislerine yalnızca görevlerini yerine getirebilmeleri için mutlak surette ihtiyaç duydukları kaynaklara, belirlenmiş zaman aralıklarında ve kısıtlı protokollerle erişim yetkisi verilir. Geniş `any-any` kuralları kesinlikle yasaktır.
3. **Sıfır Güven Mimarisi (Zero Trust Architecture - NIST SP 800-207):**
   * "Asla Güvenme, Her Zaman Doğrula (Never Trust, Always Verify)". Ağın içinde veya dışında olmak bir cihaza otomatik güven sağlamaz. Kimlik (User-ID), cihaz sağlık durumu (Device Posture) ve oturum davranışı sürekli olarak denetlenir.

---

## 2. Güvenlik Bölgeleri (Security Zones) ve Güvenilirlik Hiyerarşisi

Güvenlik duvarları üzerindeki tüm fiziksel ve mantıksal arayüzler, güvenlik seviyelerine göre derecelendirilmiş Zone hiyerarşisine dahil edilmiştir. Trafik her zaman yüksek güvenli bir bölgeden düşük güvenli bölgeye veya eşit bölgeler arasında katı denetime tabidir:

```mermaid
graph TD
    subgraph HIERARCHY["Kurumsal Güvenlik Zone Hiyerarşisi (Güven Düzeyi Sıralı)"]
        Z_RND["1. Seviye (En Yüksek): Zone_RnD (AR-GE ve Tescilli Model Deposu)"]
        Z_EXEC["2. Seviye: Zone_Executive & Zone_Finance (C-Level, SWIFT, SAP)"]
        Z_PROD["3. Seviye: Zone_DC_Services & Zone_Prod (Active Directory, DB'ler)"]
        Z_DEV["4. Seviye: Zone_DevOps & Zone_Staging (Yazılım Geliştirme)"]
        Z_CORP["5. Seviye: Zone_Corporate (Standart İdari Kullanıcılar, Satış, İK)"]
        Z_DMZ["6. Seviye: Zone_DMZ (LMS Web, Dışa Açık Web Portalları)"]
        Z_STUDENT["7. Seviye: Zone_Campus_Student (10k Öğrenci Wi-Fi / Eduroam)"]
        Z_GUEST["8. Seviye: Zone_Guest (Şube Misafir Ağları)"]
        Z_UNTRUST["9. Seviye (En Düşük): Untrust_WAN (Genel İnternet)"]
    end

    Z_RND --> Z_PROD
    Z_EXEC --> Z_PROD
    Z_DEV --> Z_PROD
    Z_CORP --> Z_DMZ
    Z_STUDENT --> Z_DMZ
    Z_GUEST --> Z_UNTRUST
    Z_DMZ --> Z_UNTRUST
```

---

## 3. Bölgeler Arası Geçiş (Inter-Zone Matrix) Kuralları

| Kaynak Bölge | Hedef Bölge | Standart Politika | Gerekli Denetim ve Güvenlik Profili |
| :--- | :--- | :---: | :--- |
| **Trust_Executive / Finance** | **Untrust_WAN** | Kontrollü İzin | Tam SSL Decryption + DLP + URL Filtering + WildFire |
| **Trust_Finance** | **Trust_Corporate** | **ENGELLE (DENY)** | Departmanlar arası yanal hareket (Lateral Movement) yasak |
| **Zone_Dev_Workstation** | **Zone_Production_Data** | **ENGELLE (DENY)** | Doğrudan erişim yasak; MFA Bastion Host zorunlu |
| **Zone_RnD_Enclave** | **Untrust_WAN** | **ENGELLE (DENY)** | Sadece onaylı akademik makale sitelerine tek yönlü indirme izni |
| **Zone_Campus_Student** | **Zone_Campus_Admin / DC**| **ENGELLE (DENY)** | Kampüs idari ve veritabanı ağlarına mutlak erişim engeli |
| **Zone_Campus_Student** | **Zone_DMZ (LMS)** | Kontrollü İzin | Web Application Firewall (WAF) + Rate Limiting |
| **Zone_Guest** | **Bütün İç Bölgeler** | **MUTLAK ENGELLE** | Yalnızca harici WAN DNS/Web çıkışı |
| **Untrust_WAN (Dış Dünya)**| **Bütün İç Bölgeler** | **ENGELLE (DENY)** | Dışarıdan içeriye başlatılan oturumlar donanımsal olarak kapatılır |

---

## 4. Kural Yaşam Döngüsü ve Değişiklik Yönetimi (Change Management)

1. **Talep ve İş Gerekçesi:** Açılması talep edilen her kural için JIRA ITSM üzerinden kural talep formu (Kaynak IP, Hedef IP, Port/Uygulama, Süre, İş Gerekçesi) doldurulur.
2. **Kıdemli Güvenlik Mimarı Onayı:** Kural açılmadan önce ağ mimarı ve CISO onayı alınır.
3. **Otomatik Süre Sonu (Shadow Rule Expiration):** Geçici test veya taşeron firma erişimleri için tanımlanan kurallara azami 30 günlük son kullanma tarihi (`Rule Expiration Date`) atanır. Süre bittiğinde kural otomatik pasife alınır.
4. **Yıllık Kural Temizliği (Rule Recertification):** Son 90 gün boyunca tek bir paket dahi geçmemiş olan kullanılmayan kurallar (`Zero-Hit Rules`), her çeyrek dönemde Panorama/FortiManager raporlarıyla tespit edilip sistemden temizlenir.

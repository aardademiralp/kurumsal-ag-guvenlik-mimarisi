# AR-GE Ekibi - İzolasyon Politikası ve Fikri Mülkiyet (IP) Koruma Mimarisi

## 1. Amaç ve Kapsam
Bu belge, holding ve üniversite bünyesinde geliştirilen tescilli yapay zeka modellerinin, algoritma kodlarının, patent hazırlıklarının ve hassas kurumsal veri setlerinin yetkisiz kişilerce dışarıya sızdırılmasını (Data Exfiltration) engellemek amacıyla uygulanan katı izolasyon kurallarını ve mimarisini tanımlar.

---

## 2. Sıfır Güvenli İzole Ada (Air-Gapped Enclave) Mimarisi

AR-GE laboratuvarı, genel kampüs ve şirket omurgasından mantıksal ve fiziksel bariyerlerle ayrılmış "Air-Lock" (Hava Kilidi) mimarisine sahiptir:

```mermaid
flowchart TD
    subgraph DIS_AG["Genel Ağ & Dış Dünya"]
        INET["Genel İnternet / Bulut"]
        CAMPUS["Kampüs / Merkez Ağı"]
    end

    subgraph AIR_LOCK["Veri Giriş Hava Kilidi (Data Air-Lock Gateway)"]
        DLP_IN["Gelen Veri Teftişi (AV + CDR + Format Doğrulama)"]
        QUARANTINE["Sandbox İnceleme Alanı"]
    end

    subgraph ARGE_ENCLAVE["İzole AR-GE Laboratuvarı (VLAN 510 / 520 / 530)"]
        WORKSTATION["Araştırmacı İş İstasyonları (VLAN 510)"]
        GPU["HPC DGX H100 GPU Kümesi (VLAN 520)"]
        STORAGE["İzole NVMe Veri Deposu (VLAN 530)"]
    end

    INET -.->|Doğrudan Bağlantı Kesinlikle Yasak| ARGE_ENCLAVE
    CAMPUS -->|Tek Yönlü Kontrollü Geçiş| DLP_IN
    DLP_IN --> QUARANTINE
    QUARANTINE -->|Onaylı Temiz Veri Seti| STORAGE
    WORKSTATION <--> GPU
    GPU <--> STORAGE
    
    ARGE_ENCLAVE -.->|Dışarıya Veri Çıkışı (Egress)| BLOCKED["MUTLAK BLOKAJ (0 Kbps Egress)"]
```

---

## 3. Donanımsal ve Uç Nokta Güvenlik Kontrolleri

### 3.1. USB ve Çevresel Birim Blokajı (Hardware USB Kill-Switch)
* Tüm AR-GE bilgisayarlarında BIOS seviyesinde USB veri aktarımı kapatılmıştır.
* Yalnızca donanımsal kimlikli (Vendor ID / Product ID kilitli) klavye ve farelere izin verilir.
* USB flash bellek, harici SSD/HDD veya akıllı telefon takıldığı anda CrowdStrike / Cortex XDR uç nokta ajanı portu kilitler, makinenin ağ bağlantısını karantinaya alır ve SOC ekibine P1 alarmı düşürür.

### 3.2. Ekran ve Pano Güvenliği (Clipboard & Screenshot Restrictions)
* Araştırma iş istasyonlarından harici ağa pano kopyalama (copy-paste) engellenmiştir.
* Ekranda görüntülenen tescilli modellerin ve kodların fotoğrafının çekilmesini caydırmak amacıyla ekranda kullanıcının sicil numarası, IP adresi ve anlık zaman damgasını içeren saydam dijital filigran (steganografik watermark) görüntülenir.

---

## 4. Veri Giriş ve Çıkış Prosedürleri (Data Air-Lock)

### 4.1. Laboratuvara Veri Girişi (Ingress Protocol)
Laboratuvarda eğitilecek açık kaynak veri kümeleri veya müşteri veri setleri içeriye şu adımlarla alınır:
1. Veri seti, Ankara Genel Merkez Veri Güvenliği Komitesine talep açılır.
2. Veri seti `10.50.10.5` numaralı Air-Lock sunucusuna indirilir.
3. Otomatik derin CDR (Content Disarm and Reconstruction) ve antivirüs taramasından geçirilir.
4. Dosyada gömülü makro, çalıştırılabilir kod (executable) veya şüpheli betik olmadığı teyit edildikten sonra izole depolama alanına aktarılır.

### 4.2. Laboratuvardan Çıkış Yasağı (Strict Egress Quarantine)
Laboratuvardan dışarıya hiçbir model ağırlığı (`.bin`, `.safetensors`, `.onnx`), Python betiği veya ham veri çıkartılamaz.
* Patent veya ürünleştirme amacıyla dışarıya çıkarılması gereken modeller, **Fikri Mülkiyet Değerlendirme Kurulu (IP Board)** ve Kıdemli Güvenlik Mimarı onayına sunulur.
* Onaylanan modellerin içine modelin kuruma ait olduğunu ispatlayan geri döndürülemez dijital filigran (Model Watermarking / Backdoor verification trigger) enjekte edildikten sonra şifreli olarak dışarı teslim edilir.

# AR-GE ve Yapay Zeka Ekibi - Profil ve Araştırma Ortamı

## 1. Genel Tanım ve Ekip Rolü
AR-GE (Araştırma ve Geliştirme) ve Yapay Zeka (AI/ML) ekibi, holding ve bağlı üniversitenin en kritik fikri mülkiyet (Intellectual Property - IP) varlıklarını, tescilli algoritmalarını, derin öğrenme modellerini, patent başvurusu aşamasındaki inovasyonları ve gizli kurumsal veri kümelerini (datasets) üreten stratejik araştırma birimidir.

* **Lokasyon:** Ankara Teknokent AR-GE Binası (Biyometrik Korumalı Özel Kat)
* **Personel Kapasitesi:** 40 Araştırmacı (Veri Bilimciler, AI/ML Mühendisleri, Doktoralı Araştırmacılar)
* **Ağ Rolü:** Hava Boşluklu / Yüksek İzolasyonlu Araştırma Laboratuvarı (Air-Gapped / Isolated Enclave)
* **Çalışma Modeli:** Yüksek Başarımlı Hesaplama (HPC GPU Cluster), Hassas Veri Modelleme

---

## 2. Personel Profili ve Rol Dağılımı

| Rol Grubu | Kişi Sayısı | Araştırma Alanı ve Sorumluluk | Erişilen Veri Tipi | Fikri Mülkiyet (IP) Riski |
| :--- | :---: | :--- | :--- | :--- |
| **Büyük Dil Modeli (LLM) Araştırmacıları** | 12 | Özel ağırlık modelleri (weights), yerel LLM eğitimi | Tescilli Kurumsal Veri Setleri | Çok Yüksek (Patent/Model Hırsızlığı) |
| **Bilgisayarlı Görü ve Robotik** | 10 | Görüntü işleme algoritmaları, otonom sistemler | Ham Sensör ve Kamera Kayıtları | Yüksek |
| **Biyoenformatik ve Sağlık AI** | 8 | Genomik veri analizi, klinik karar destek modelleri | Anonimleştirilmiş Sağlık/DNA Verisi | Kritik / KVKK Madde 6 (Özel Nitelikli) |
| **Veri Mühendisleri & MLOps** | 10 | GPU kümesi yönetimi, veri boru hatları (data pipelines) | Ham Veri Ambarı, Feature Store | Yüksek Altyapı Yetkisi |
| **Toplam** | **40** | - | - | - |

---

## 3. Güvenlik Prensipleri ve Tehdit Modeli

1. **Fikri Mülkiyet (IP) ve Model Kaçırma (Data Exfiltration) Tehdidi:**
   * Milyonlarca dolarlık GPU yatırımıyla eğitilen tescilli model ağırlıkları (weights/checkpoints) tek bir USB bellek veya kontrolsüz bulut yüklemesi ile çalınabilir.
2. **Sıfır Egress Toleransı (Zero-Exfiltration Tolerance):**
   * Laboratuvar ortamındaki sunuculardan ve iş istasyonlarından dış internete herhangi bir ham veri, model dosyası veya kaynak kodu aktarımı mutlak surette engellenmelidir.
3. **Fiziksel ve Mantıksal Bütünlük:**
   * Laboratuvar alanı biyometrik iris/parmak izi okuyucularla korunmakta olup, ağ erişimi yalnızca 802.1X sertifikalı laboratuvar terminalleri ile sınırlandırılmıştır.

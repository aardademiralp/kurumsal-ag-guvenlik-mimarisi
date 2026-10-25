# Yazılım ve DevOps Ekibi - Profil ve Mühendislik Mimarisi

## 1. Genel Tanım ve Ekip Rolü
Yazılım Geliştirme, DevOps ve Kalite Güvence (QA) ekipleri, holdingin dijital ürünlerini, kampüs LMS/ÖBS yazılımlarını, fintech/mobil bankacılık arayüzlerini ve şirket içi mikroservis mimarilerini geliştiren çekirdek mühendislik birimidir. Bu ekip yüksek hesaplama gücü, konteynerleştirme (Kubernetes/Docker), sürekli entegrasyon ve dağıtım (CI/CD) hatları ile çalışmaktadır.

* **Lokasyon:** Ankara Teknopark / AR-GE Binası (3. Kat)
* **Personel Kapasitesi:** 80 Mühendis
* **Ağ Rolü:** Yüksek Güvenlikli Geliştirme ve CI/CD Segmenti (Secure SDLC & DevSecOps Zone)
* **Çalışma Modeli:** Çevik (Agile / Scrum), Yoğun Kod Derleme ve Dağıtım Döngüleri

---

## 2. Mühendislik Rol Dağılımı

| Alt Ekip | Mühendis Sayısı | Temel Sorumluluklar | Kullandıkları Araçlar ve Platformlar | Ağ Erişim Seviyesi |
| :--- | :---: | :--- | :--- | :--- |
| **Backend & API Mühendisleri** | 30 | Mikroservis mimarisi, REST/gRPC servisleri, veritabanı tasarımı | Go, Java Spring Boot, Python, PostgreSQL, Redis | VLAN 410 (Workstations), Staging erişimi |
| **Frontend & Mobil Geliştirme**| 20 | Web ön yüzleri, iOS ve Android kurumsal uygulamalar | React, Next.js, Flutter, Swift, Kotlin, Figma | VLAN 410, Onaylı SaaS ve NPM/Gradle repoları |
| **DevOps & Platform Mühendisliği**| 15 | CI/CD boru hatları, Kubernetes yönetimi, altyapı kodlama (IaC) | GitLab CI, ArgoCD, Terraform, Kubernetes, Ansible | VLAN 410, Staging, Bastion üzerinden Prod |
| **QA & Test Otomasyonu** | 15 | Yük testleri, regresyon testleri, siber güvenlik testleri (DAST/SAST)| SonarQube, JMeter, Selenium, OWASP ZAP | VLAN 410, İzole QA/Staging ortamları |
| **Toplam** | **80** | - | - | - |

---

## 3. DevSecOps Prensipleri ve Güvenli Yaşam Döngüsü

1. **İki Kişi Kuralı (Four-Eyes Principle):**
   * Hiçbir geliştirici canlı (Production) ortama doğrudan müdahale edemez veya doğrudan kod push edemez.
   * Kodlar önce GitLab PR/MR onayından geçer, SonarQube statik kod analizinden ve Trivy konteyner güvenlik taramasından geçtikten sonra CI/CD runner ile canlıya taşınır.
2. **Ortam İzolasyonu (Zero-Trust Environment Separation):**
   * Development, Staging ve Production ortamları farklı Layer 3 güvenlik bölgelerindedir. Geliştirici bilgisayarlarından Production ortamına doğrudan IP düzeyinde erişim donanımsal olarak yasaktır.

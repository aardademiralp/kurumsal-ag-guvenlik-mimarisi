# AR-GE Ekibi - IP Adresleme ve Segmentasyon Planı

## 1. Mimari Segmentasyon Modeli
AR-GE ve Yapay Zeka ekibi, holding omurgasında `10.50.0.0/16` süpernet bloğunda konumlandırılmıştır. Laboratuvar ortamı, genel şirket ağından bağımsız bir "Güvenli İzole Ada (Secure Enclave)" şeklinde tasarlanmıştır.

Tüm IP adresleri DHCP üzerinden dinamik olarak değil, donanımsal MAC adresi eşleştirmeli statik rezervasyon (`DHCP Reservation with MAC Binding`) ile atanır. Ağda tanımlı olmayan yabancı bir donanım takıldığında switch portu donanımsal olarak kapatılır (`Port Security - Violation Shutdown`).

---

## 2. Detaylı IP ve VLAN Tablosu

| VLAN ID | VLAN Adı | Güvenlik Bölgesi (Zone) | Ağ Adresi (CIDR) | Alt Ağ Maskesi | Varsayılan Ağ Geçidi (GW) | Kullanılabilir IP Aralığı | IP Dağıtım Yöntemi | Statik Rezerve Cihaz / Sunucu |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **510** | `VLAN_RND_ISOLATED_LAB` | `Zone_RnD_Enclave` | `10.50.10.0/24` | `255.255.255.0` | `10.50.10.1` | `10.50.10.2 - 10.50.10.254` | Statik MAC Eşleştirmeli | `10.50.10.2 - 10.50.10.49` (Araştırmacı Masaüstü Terminalleri) |
| **520** | `VLAN_RND_HPC_GPU` | `Zone_RnD_Compute` | `10.50.20.0/24` | `255.255.255.0` | `10.50.20.1` | `10.50.20.2 - 10.50.20.254` | Tamamen Statik | `10.50.20.2 - 10.50.20.254` (NVIDIA DGX H100 GPU Sunucuları) |
| **530** | `VLAN_RND_SECURE_STORAGE`| `Zone_RnD_Storage` | `10.50.30.0/24` | `255.255.255.0` | `10.50.30.1` | `10.50.30.2 - 10.50.30.254` | Tamamen Statik | `10.50.30.2 - 10.50.30.254` (TrueNAS / Ceph All-Flash NVMe Array)|

---

## 3. Kritik Donanım ve IP Rezervasyon Listesi

### VLAN 510 - Araştırma İş İstasyonları (10.50.10.0/24)
* `10.50.10.10 - 10.50.10.49`: 40 Adet Linux (Ubuntu LTS) Veri Bilimci İş İstasyonu (Statik 802.1X Sertifikalı).
* `10.50.10.5`: AR-GE Güvenli Dosya Teftiş Geçidi (DLP Sanitization Gateway / Data Air-Lock).

### VLAN 520 - Yüksek Başarımlı Hesaplama (HPC) GPU Kümesi (10.50.20.0/24)
* `10.50.20.10`: HPC Slurm Master Scheduler & Resource Manager VIP
* `10.50.20.11`: NVIDIA DGX H100 Node 01 (8x H100 SXM5 80GB)
* `10.50.20.12`: NVIDIA DGX H100 Node 02 (8x H100 SXM5 80GB)
* `10.50.20.13`: NVIDIA DGX H100 Node 03 (8x H100 SXM5 80GB)
* `10.50.20.14`: NVIDIA DGX H100 Node 04 (8x H100 SXM5 80GB)
* `10.50.20.20`: Kubeflow / MLflow Model Yaşam Döngüsü Sunucusu

### VLAN 530 - Şifreli AR-GE Depolama Birimleri (10.50.30.0/24)
* **Özellik:** Dış dünyadan tamamen yalıtılmış, AES-XTS-256 donanımsal disk şifrelemeli yerel depolama.
* `10.50.30.10`: Ceph / Lustre Dağıtık Dosya Sistemi MDS (Metadata Server)
* `10.50.30.11 - 10.50.30.14`: NVMe-over-Fabrics (NVMe-oF) All-Flash Depolama Düğümleri (Hassas Veri Kümeleri)
* `10.50.30.20`: Yerel İçi Boş Model Registry (Tescilli .bin / .safetensors Model Ağırlıkları Deposu)

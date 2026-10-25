# Londra Şubesi - Zero-Touch Provisioning (ZTP) ve Kurulum Rehberi

Londra ofisinde yerleşik kıdemli ağ mühendisi bulunmadığından, Palo Alto Networks PA-440 cihazı **Zero-Touch Provisioning (ZTP)** mimarisiyle Ankara'daki merkezi mühendislik ekibi tarafından uzaktan sıfır müdahale ile devreye alınır.

---

## 1. Zero-Touch Provisioning (ZTP) İş Akışı (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor Tech as Londra Lokal Teknisyen
    participant Box as Fabrika Çıkışlı PA-440 (ZTP Port)
    participant DHCP as ISP Colt Router (DHCP)
    participant Cloud as Palo Alto ZTP Cloud Service
    participant Pano as Ankara Panorama Yönetim Sunucusu

    Tech->>Box: Güç Kablosu + WAN Portunu Colt Router'a Tak
    Box->>DHCP: WAN Portundan DHCP İsteği (Opt 43)
    DHCP-->>Box: IP, Gateway, DNS Bilgisi Ver
    Box->>Cloud: ZTP Cloud Servisine Seri No & Sertifika Gönder (HTTPS 443)
    Cloud->>Pano: "PA-440 (SN: 0182049102) Çevrimiçi Oldu" Bildirimi
    Pano-->>Cloud: Londra Şube Template & Device-Group Ata
    Cloud-->>Box: Panorama IP (195.175.10.10) & Bootstrap Konfigürasyonunu Yükle
    Box->>Pano: Güvenli Yönetim Tüneli Aç (TCP 3978)
    Pano->>Box: Ankara IPsec Tünelini ve Kural Setini Bas (Commit)
    Note over Box,Pano: Sistem Otomatik Olarak Devreye Girdi
```

---

## 2. Ankara Merkezde Ön-Hazırlık (Panorama Pre-Provisioning)

Cihaz Londra'ya kargolanmadan önce Ankara Panorama M-200 üzerinde cihaz seri numarası sisteme tanımlanır:

1. **Seri No Kaydı:** `Device > Zero Touch Provisioning > Add Device` -> Seri No: `0182049102`.
2. **Template Grubu Ataması:** `TMP-LON-BRANCH`
   - WAN Arayüzü: `ethernet1/1` (DHCP Client).
   - LAN Arayüzü: `ethernet1/2` (Sub-interfaces: `.210` IP `10.30.10.1/24`, `.299` IP `10.30.99.1/24`).
   - Tünel Arayüzü: `tunnel.2` (IP: `10.255.30.2/30`).
3. **Device-Group Ataması:** `DG-LON-BRANCH` (Tüm kurallar ve Geo-IP politikaları bu gruba önceden işlenir).

---

## 3. IPsec VPN Tünel Yapılandırması (Ankara Hub Entegrasyonu)

Panorama şablonu üzerinden PA-440 cihazına otomatik olarak indirilen tünel parametreleri:

### 3.1. IKE Kripto Profili (Phase 1)
```text
set network ike crypto-profile IKE-PRF-HQ-LON hash sha256
set network ike crypto-profile IKE-PRF-HQ-LON dh-group group14 group19
set network ike crypto-profile IKE-PRF-HQ-LON encryption aes-256-gcm
set network ike crypto-profile IKE-PRF-HQ-LON lifetime hours 8
```

### 3.2. IKE Gateway Tanımı
```text
set network ike gateway GW-TO-ANKARA-HUB version ikev2
set network ike gateway GW-TO-ANKARA-HUB local-address interface ethernet1/1
set network ike gateway GW-TO-ANKARA-HUB peer-address ip 195.175.10.2
set network ike gateway GW-TO-ANKARA-HUB authentication pre-shared-key key "HoldingSecKeyAnkLon2026!#UltraSecure"
set network ike gateway GW-TO-ANKARA-HUB protocol-common nat-traversal enable
set network ike gateway GW-TO-ANKARA-HUB protocol-common dead-peer-detection enable interval 5 retry 3
```

### 3.3. IPsec Kripto Profili ve Tünel (Phase 2)
```text
set network ipsec crypto-profile IPSEC-PRF-HQ-LON esp encryption aes-256-gcm
set network ipsec crypto-profile IPSEC-PRF-HQ-LON esp authentication none
set network ipsec crypto-profile IPSEC-PRF-HQ-LON lifetime hours 1
set network ipsec crypto-profile IPSEC-PRF-HQ-LON dh-group group14

set network tunnel ipsec IPSEC-TUN-TO-HQ-ANKARA auto-key ike-gateway GW-TO-ANKARA-HUB
set network tunnel ipsec IPSEC-TUN-TO-HQ-ANKARA auto-key ipsec-crypto-profile IPSEC-PRF-HQ-LON
set network tunnel ipsec IPSEC-TUN-TO-HQ-ANKARA tunnel-interface tunnel.2
```

---

## 4. Dinamik BGP Yönlendirme

```text
set network virtual-router default protocol bgp enable yes
set network virtual-router default protocol bgp router-id 10.30.99.10
set network virtual-router default protocol bgp as 64530
set network virtual-router default protocol bgp peer-group PG-ANKARA-HUB peer PEER-ANKARA-HQ peer-as 64512
set network virtual-router default protocol bgp peer-group PG-ANKARA-HUB peer PEER-ANKARA-HQ peer-address ip 10.255.30.1
set network virtual-router default protocol bgp peer-group PG-ANKARA-HUB peer PEER-ANKARA-HQ local-address interface tunnel.2
```

---

## 5. Doğrulama ve Canlı Test (Verification Checklist)

Teknisyen kabloyu taktıktan 7 dakika sonra Ankara SOC ekibi aşağıdaki kontrolleri yürütür:
1. `show panorama-status`: Durumun `Connected` olduğu doğrulanır.
2. `show vpn ike-sa`: Ankara tünelinde Phase-1 IKEv2 oturumunun `Up` olduğu kontrol edilir.
3. `show vpn ipsec-sa`: Phase-2 SPI eşleşmeleri ve şifrelenmiş paket sayaçları teyit edilir.
4. `show routing protocol bgp summary`: BGP komşuluğunun `Established` olduğu ve `10.10.0.0/16` rotasının alındığı doğrulanır.

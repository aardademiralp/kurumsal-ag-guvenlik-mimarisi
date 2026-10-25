# Akademik Şube ve Kampüs - FortiGate 1800F Kurulum ve Entegrasyon Rehberi

Bu belge, Kampüs omurgasında konumlandırılan **Fortinet FortiGate 1800F Active/Passive HA** kümesinin 10G omurga bağlantılarını, HA konfigürasyonunu ve 802.1X / Eduroam RADIUS entegrasyonunu eksiksiz teknik detaylarla sunar.

---

## 1. Fiziksel Kablolama ve 10G SFP+ Omurga Terminasyonu

* **WAN-1 (ULAKBİM 10G):** Port `port1` (10G SFP+ LR Single-Mode Fiber) -> ULAKBİM Fiber Patch Panel
* **WAN-2 (Türk Telekom 10G):** Port `port2` (10G SFP+ LR Single-Mode Fiber) -> Türk Telekom ODF
* **İç Ağ Omurga Bağlantısı (Core Trunk):** Port `port3` ve `port4` (10G SFP+ SR Multi-Mode Fiber), Cisco Catalyst 9600 Core Switch kümesine LACP (802.3ad) ile bağlanarak 20 Gbps agregasyon sağlanır.
* **HA Heartbeat:** Port `ha1` ve `ha2` (Dedicated 10G SFP+ DAC) doğrudan iki FG-1800F arasına çapraz bağlanır.

```text
# LACP Core Trunk Arayüzü (FortiOS CLI):
config system lacp
    set mode active
end

config system aggregate-interface
    edit "Campus-Core-Trunk"
        set member "port3" "port4"
        set lacp-mode active
        set lacp-speed fast
    next
end
```

---

## 2. FortiGate Cluster Protocol (FGCP) Active/Passive HA Yapılandırması

Kesintisiz hizmet için iki adet FortiGate 1800F cihazı FGCP protokolüyle kümelenir:

```text
# Birincil Cihaz (FG-1800F-Master):
config system ha
    set group-id 50
    set group-name "Campus-Security-Cluster"
    set mode a-p
    set password "CampusHaSecureSecretKey2026!"
    set hbdev "ha1" 50 "ha2" 50
    set session-pickup enable
    set session-pickup-connectionless enable
    set ha-uptime-diff-margin 300
    set priority 200
    set monitor "port1" "port2" "Campus-Core-Trunk"
end

# İkincil Cihaz (FG-1800F-Slave):
config system ha
    set group-id 50
    set group-name "Campus-Security-Cluster"
    set mode a-p
    set password "CampusHaSecureSecretKey2026!"
    set hbdev "ha1" 50 "ha2" 50
    set session-pickup enable
    set session-pickup-connectionless enable
    set ha-uptime-diff-margin 300
    set priority 100
    set monitor "port1" "port2" "Campus-Core-Trunk"
end
```

---

## 3. 802.1X / RADIUS ve Ulusal Eduroam Entegrasyonu

Kampüsteki Wi-Fi 6 AP'ler üzerinden gelen Eduroam oturumları, FortiGate ve kurumsal RADIUS (ULAKBİM Ulusal Proxy) sunucusu ile doğrulanır:

### 3.1. RADIUS Sunucu Tanımları
```text
config user radius
    edit "ULAKBIM-Eduroam-Primary"
        set server "10.101.30.50"
        set secret "EduroamRadiusSecretKey2026!#"
        set auth-type peap
        set nas-ip 10.101.99.10
        set acct-interim-interval 600
    next
    edit "ULAKBIM-Eduroam-Secondary"
        set server "193.140.83.15"
        set secret "EduroamRadiusSecretKey2026!#"
        set auth-type peap
        set nas-ip 10.101.99.10
    next
end

# Kullanıcı Grubu Oluşturulması:
config user group
    edit "Eduroam-Authenticated-Users"
        set member "ULAKBIM-Eduroam-Primary" "ULAKBIM-Eduroam-Secondary"
    next
end
```

### 3.2. WLC ve 802.1X VSA (Vendor-Specific Attribute) Doğrulaması
Öğrenci veya akademisyen cihazı kimlik doğruladığında, RADIUS sunucusu Fortinet-Group-Name niteliğini döndürür:
* Eğer kullanıcı `Eduroam-Student` ise -> Dinamik olarak VLAN 300-305 havuzuna atanır.
* Eğer kullanıcı `Eduroam-Academic` ise -> Dinamik olarak VLAN 310 atanır.

---

## 4. Dinamik BGP Yönlendirme (ULAKBİM & ISP)

```text
config router bgp
    set as 64540
    set router-id 10.101.99.10
    config neighbor
        edit "193.140.83.1"
            set remote-as 1005
            set description "ULAKBIM-National-Academic-Network"
            set route-map-in "RM-ULAKBIM-IN"
            set route-map-out "RM-CAMPUS-OUT"
        next
        edit "212.156.90.1"
            set remote-as 9121
            set description "Turk-Telekom-Commercial-10G"
        next
    end
end
```

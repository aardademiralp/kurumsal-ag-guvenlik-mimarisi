# İstanbul Şubesi - FortiGate 100F Kurulum ve Devreye Alma Rehberi

Bu belge, İstanbul Şubesinde konumlandırılan **Fortinet FortiGate 100F** cihazının WAN provisioning, SD-WAN yapılandırması ve Ankara Hub (Palo Alto PA-3410) ile IPsec VPN tünel entegrasyonu adımlarını üretim seviyesi CLI komutlarıyla içerir.

---

## 1. Fiziksel Bağlantılar ve WAN Arayüz Yapılandırması

* `wan1`: Türk Telekom Metro Ethernet Fiber Media Converter -> RJ45 WAN1 (Statik IP: `212.156.40.2/30`, GW: `212.156.40.1`)
* `wan2`: Vodafone Net Kurumsal Fiber -> RJ45 WAN2 (Statik IP: `88.255.80.2/30`, GW: `88.255.80.1`)
* `fortilink` (`a` ve `b` portları LACP): FortiSwitch 248E-FPOE bağlantısı.

```text
# WAN Arayüzlerinin Tanımlanması (FortiOS CLI):
config system interface
    edit "wan1"
        set vdom "root"
        set mode static
        set ip 212.156.40.2 255.255.255.252
        set allowaccess ping
        set description "Turk-Telekom-Metro-Primary-500M"
    next
    edit "wan2"
        set vdom "root"
        set mode static
        set ip 88.255.80.2 255.255.255.252
        set allowaccess ping
        set description "Vodafone-Fiber-Backup-100M"
    next
end
```

---

## 2. Ankara Hub ile IPsec VPN Tünel Yapılandırması

Ankara Genel Merkezindeki Palo Alto PA-3410 Hub cihazı ile IKEv2 ve route-based IPsec tüneli kurulur.

```text
# IPsec Phase-1 Yapılandırması:
config vpn ipsec phase1-interface
    edit "IPSec-To-Ankara"
        set interface "wan1"
        set ike-version 2
        set keylife 28800
        set peertype any
        set net-device disable
        set proposal aes256-sha256 aes256gcm
        set dhgrp 14 19
        set remote-gw 195.175.10.2
        set psksecret "HoldingSecKeyAnkIst2026!#StrongPreshared"
        set dpd-retryinterval 5
    next
end

# IPsec Phase-2 Yapılandırması:
config vpn ipsec phase2-interface
    edit "IPSec-To-Ankara-p2"
        set phase1name "IPSec-To-Ankara"
        set proposal aes256-sha256 aes256gcm
        set dhgrp 14 19
        set auto-negotiate enable
        set keylifeseconds 3600
        set src-subnet 10.20.0.0 255.255.0.0
        set dst-subnet 10.10.0.0 255.255.0.0
    next
end

# Tünel Mantıksal IP Ataması:
config system interface
    edit "IPSec-To-Ankara"
        set ip 10.255.10.2 255.255.255.255
        set remote-ip 10.255.10.1 255.255.255.255
        set allowaccess ping
    next
end
```

---

## 3. SD-WAN Zone ve Dinamik Performans SLA Yapılandırması

Tüm WAN arayüzleri ve IPsec tüneli tek bir mantıksal SD-WAN Zone altında birleştirilir.

```text
# SD-WAN Zone ve Üyelerin Eklenmesi:
config system sdwan
    set status enable
    config zone
        edit "SDWAN-Internet-Zone"
        next
        edit "SDWAN-Corporate-Zone"
        next
    end
    config members
        edit 1
            set interface "wan1"
            set zone "SDWAN-Internet-Zone"
            set gateway 212.156.40.1
        next
        edit 2
            set interface "wan2"
            set zone "SDWAN-Internet-Zone"
            set gateway 88.255.80.1
            set priority 10
        next
        edit 3
            set interface "IPSec-To-Ankara"
            set zone "SDWAN-Corporate-Zone"
            set cost 0
        next
    end
    
    # Canlı Performans Ölçümü (Health Check / SLA):
    config health-check
        edit "SLA-DNS-Ping"
            set server "1.1.1.1" "8.8.8.8"
            set members 1 2
            config sla
                edit 1
                    set latency-threshold 30
                    set jitter-threshold 10
                    set packetloss-threshold 1
                next
            end
        next
        edit "SLA-HQ-Hub"
            set server "10.10.100.10"
            set members 3
            config sla
                edit 1
                    set latency-threshold 20
                    set jitter-threshold 5
                    set packetloss-threshold 0.5
                next
            end
        next
    end
end
```

---

## 4. SD-WAN Kural Politikaları (Service Rules)

```text
# Kural 1: Kurumsal Şirket İçi Ağlara Ankara Tüneli Üzerinden Erişim:
config system sdwan
    config service
        edit 10
            set name "Internal-Corporate-Traffic"
            set mode priority
            config dst
                edit 1
                    set name "10.10.0.0/16"
                next
                edit 2
                    set name "10.40.0.0/16"
                next
            end
            set priority-members 3
        next
        
        # Kural 20: Microsoft 365 Doğrudan WAN-1 Çıkışı (DIA):
        edit 20
            set name "M365-Direct-Internet-Access"
            set mode sla
            config sla
                edit 1
                    set health-check "SLA-DNS-Ping"
                    set id 1
                next
            end
            set internet-service enable
            set internet-service-name "Microsoft-Office365"
            set priority-members 1 2
        next
    end
end
```

---

## 5. BGP Yönlendirme ve Rota Yayınlama

Ankara Hub ile dinamik rota paylaşımı için BGP komşuluğu tesis edilir:

```text
config router bgp
    set as 64520
    set router-id 10.20.99.10
    config neighbor
        edit "10.255.10.1"
            set remote-as 64512
            set keep-alive-timer 10
            set holdtime-timer 30
            set connect-timer 10
        next
    end
    config network
        edit 1
            set prefix 10.20.10.0 255.255.255.0
        next
    end
end
```

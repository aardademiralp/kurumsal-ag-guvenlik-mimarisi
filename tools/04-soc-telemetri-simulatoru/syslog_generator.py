#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kurumsal Ağ ve Siber Güvenlik Mimarisi - SOC Telemetri ve Olay Simülatörü
(Enterprise SOC Telemetry & Synthetic Event Simulator - RFC 5424 & ArcSight CEF)

Bu araç, kurulan Güvenlik Operasyon Merkezi (SOC) personelinin ve SIEM sisteminin
(Splunk / Elastic Security / Zeek / NDR) alarm senaryolarını test etmek amacıyla
sentetik ağ güvenliği telemetrisi üretir.

Senaryolar:
  1. portscan: Öğrenci VLAN'ından Core Gateway'e TCP SYN taraması
  2. exfiltration: AR-GE enklavından bilinmeyen dış IP'ye 5 GB veri kaçırma (DLP)
  3. brute-force: Londra PA-440 VPN ağ geçidine Çin/Rusya Geo-IP kaynaklı başarısız oturum denemeleri
  4. all: Tüm senaryoların dengeli dağılımı

Standart Kütüphaneler: datetime, random, argparse, sys, pathlib, typing
Harici bağımlılık gerektirmez.
"""

import argparse
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Windows konsol UTF-8 uyumluluğu
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class TerminalColors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


def print_banner() -> None:
    """SOC simülatörü başlığını basar."""
    banner = f"""{TerminalColors.CYAN}{TerminalColors.BOLD}
================================================================================
     ENTERPRISE SOC TELEMETRY & SYSLOG SIMULATOR (RFC 5424 & ArcSight CEF)
================================================================================{TerminalColors.RESET}"""
    print(banner)


class SOCTelemetryGenerator:
    """Sentetik SOC güvenlik olayları ve telemetri kayıtları üreten sınıf."""

    def __init__(self, hostname: str = "core-soc-collector.holding.corp") -> None:
        self.hostname = hostname

    @staticmethod
    def get_timestamps() -> Tuple[str, str]:
        """ISO 8601 ve RFC 5424 için geçerli zaman damgası döndürür."""
        now = datetime.now(timezone.utc)
        iso_ts = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        # CEF için milisaniye cinsinden epoch
        epoch_ms = int(now.timestamp() * 1000)
        return iso_ts, str(epoch_ms)

    def generate_portscan_events(self, count: int) -> List[Dict[str, Any]]:
        """
        Senaryo 1: Öğrenci VLAN'ından (10.100.x.x) Core Gateway'e (10.101.30.1)
        TCP SYN port tarama logları.
        """
        events = []
        target_ports = [21, 22, 23, 25, 53, 80, 110, 139, 443, 445, 1433, 3306, 3389, 8080, 8443]
        src_ip = f"10.100.{random.randint(1, 30)}.{random.randint(10, 250)}"
        dst_ip = "10.101.30.1"

        for i in range(count):
            port = target_ports[i % len(target_ports)]
            src_port = random.randint(49152, 65535)
            iso_ts, epoch_ms = self.get_timestamps()

            cef = (
                f"CEF:0|Fortinet|FortiGate-1800F|7.4.2|TRAFFIC-SCAN|TCP SYN Reconnaissance Scan|7|"
                f"rt={epoch_ms} src={src_ip} spt={src_port} dst={dst_ip} dpt={port} proto=TCP "
                f"act=deny cs1=Zone_Campus_Student cs2=Zone_Campus_DC_LMS "
                f"msg=\"Reconnaissance port scan detected from Student Wi-Fi towards Core Gateway\" "
                f"deviceSeverity=High"
            )

            rfc5424 = (
                f"<131>1 {iso_ts} campus-fg-1800f.campus.local ftgFirewall 1042 SCAN-ALERT "
                f"[trafficAudit@12356 srcIP=\"{src_ip}\" dstIP=\"{dst_ip}\" dstPort=\"{port}\" "
                f"action=\"blocked\" rule=\"CMP_BLOCK_INTERNAL_RECON\"] "
                f"TCP SYN stealth scan activity intercepted on port {port}"
            )

            events.append(
                {
                    "scenario": "portscan",
                    "severity": "HIGH",
                    "cef": cef,
                    "rfc5424": rfc5424,
                    "summary": f"SYN Scan from {src_ip} -> {dst_ip}:{port} (BLOCKED)",
                }
            )
        return events

    def generate_exfiltration_events(self, count: int) -> List[Dict[str, Any]]:
        """
        Senaryo 2: AR-GE Enklavından bilinmeyen dış IP'ye 5 GB veri transferi (DLP Alarmı).
        """
        events = []
        src_ip = "10.50.10.15"  # AR-GE AI Laboratuvarı GPU İş İstasyonu
        suspicious_dst_ip = "198.51.100.89"  # Bilinmeyen harici şüpheli IP

        for _ in range(count):
            iso_ts, epoch_ms = self.get_timestamps()
            src_port = random.randint(51000, 58000)
            # 5 GB = ~5.368.709.120 byte
            bytes_out = random.randint(4800000000, 5500000000)

            cef = (
                f"CEF:0|PaloAltoNetworks|PAN-OS|11.1.2|DLP-EXFILTRATION|Massive Data Exfiltration Blocked|10|"
                f"rt={epoch_ms} src={src_ip} spt={src_port} dst={suspicious_dst_ip} dpt=443 proto=TCP "
                f"act=reset-both cs1=Zone_RnD_Enclave cs2=Untrust_WAN "
                f"out={bytes_out} app=ssl deviceSeverity=Critical "
                f"fname=proprietary_llm_weights_v4.safetensors "
                f"msg=\"CRITICAL P1 ALERT: 5GB model weights exfiltration attempt blocked by DLP Engine\""
            )

            rfc5424 = (
                f"<129>1 {iso_ts} hq-pa3410.holding.corp PAN-OS 8920 THREAT-DLP "
                f"[dlpEvent@25411 srcIP=\"{src_ip}\" dstIP=\"{suspicious_dst_ip}\" bytesSent=\"{bytes_out}\" "
                f"signature=\"DLP-Model-Weights-Heuristic\" action=\"quarantine-both\"] "
                f"Critical Unauthorized High-Volume Egress Blocked: 5.2GB data transfer attempt to non-whitelisted external IP"
            )

            events.append(
                {
                    "scenario": "exfiltration",
                    "severity": "CRITICAL",
                    "cef": cef,
                    "rfc5424": rfc5424,
                    "summary": f"DLP P1: 5.2GB Model Exfiltration {src_ip} -> {suspicious_dst_ip}:443 (RESET-BOTH)",
                }
            )
        return events

    def generate_bruteforce_events(self, count: int) -> List[Dict[str, Any]]:
        """
        Senaryo 3: Londra PA-440 VPN gateway'ine Çin/Rusya Geo-IP kaynaklı
        ardışık başarısız SSH / IKEv2 oturum açma logları (Geo-IP & Brute-Force).
        """
        events = []
        threat_actors = [
            ("202.108.22.5", "China (CN)", "SSH-BruteForce-Tool"),
            ("185.220.101.4", "Russia (RU)", "IKEv2-Aggressive-Probe"),
            ("103.251.167.20", "China (CN)", "Dict-Attack-Botnet"),
            ("194.26.29.112", "Russia (RU)", "VPN-Credential-Stuffer"),
        ]
        gateway_ip = "195.175.10.2"  # Londra PA-440 Dış IP

        for i in range(count):
            attacker_ip, geo_country, tool_name = threat_actors[i % len(threat_actors)]
            iso_ts, epoch_ms = self.get_timestamps()
            src_port = random.randint(40000, 62000)
            dst_port = 22 if (i % 2 == 0) else 500

            cef = (
                f"CEF:0|PaloAltoNetworks|PA-440-London|11.1.2|AUTH-BRUTEFORCE|Failed Authentication & Geo-IP Block|8|"
                f"rt={epoch_ms} src={attacker_ip} spt={src_port} dst={gateway_ip} dpt={dst_port} proto=TCP "
                f"act=drop cs1=Untrust_WAN cs2=Zone_LON_Trust "
                f"cn1=FailedAttempts cn1Label=Counter val1={random.randint(15, 60)} "
                f"suser=admin deviceSeverity=High c6a2={geo_country} "
                f"msg=\"Geo-IP Violation & Repeated Authentication Failure from prohibited country ({geo_country})\""
            )

            rfc5424 = (
                f"<130>1 {iso_ts} lon-pa440.london.corp PAN-OS 4401 GEOIP-AUTH-FAIL "
                f"[authFailure@19283 srcIP=\"{attacker_ip}\" country=\"{geo_country}\" dstPort=\"{dst_port}\" "
                f"reason=\"Geo-IP Policy Rejection: Non-UK/Non-TR Origin\" targetUser=\"root\"] "
                f"Consecutive Brute-Force login failures detected from {attacker_ip} ({geo_country})"
            )

            events.append(
                {
                    "scenario": "brute-force",
                    "severity": "HIGH",
                    "cef": cef,
                    "rfc5424": rfc5424,
                    "summary": f"Geo-IP / Brute-Force: {attacker_ip} ({geo_country}) -> {gateway_ip}:{dst_port} (DROP)",
                }
            )
        return events


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Kurumsal SOC Telemetri ve Sentetik Syslog Olay Simülatörü"
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="all",
        choices=["portscan", "exfiltration", "brute-force", "all"],
        help="Simüle edilecek saldırı senaryosu: portscan, exfiltration, brute-force veya all",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Üretilecek olay/log sayısı (varsayılan: 10)",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="cef",
        choices=["cef", "rfc5424", "both"],
        help="Log çıktı formatı: cef (ArcSight CEF), rfc5424 veya both",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Logların ekleneceği (append) yerel dosya yolu (örn: soc_events.log)",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Logları terminal ekranına yazdırır",
    )

    args = parser.parse_args()

    # Varsayılan: Eğer output dosyası verilmemişse stdout'u otomatik aç
    show_stdout = args.stdout or (args.output is None)

    if show_stdout:
        print_banner()

    generator = SOCTelemetryGenerator()
    generated_events: List[Dict[str, Any]] = []

    if args.scenario == "portscan":
        generated_events.extend(generator.generate_portscan_events(args.count))
    elif args.scenario == "exfiltration":
        generated_events.extend(generator.generate_exfiltration_events(args.count))
    elif args.scenario == "brute-force":
        generated_events.extend(generator.generate_bruteforce_events(args.count))
    elif args.scenario == "all":
        # Dağıtık üretim
        c_scan = max(1, args.count // 3)
        c_exfil = max(1, args.count // 3)
        c_brute = max(1, args.count - c_scan - c_exfil)
        generated_events.extend(generator.generate_portscan_events(c_scan))
        generated_events.extend(generator.generate_exfiltration_events(c_exfil))
        generated_events.extend(generator.generate_bruteforce_events(c_brute))

    # Log formatlama
    raw_lines: List[str] = []
    for ev in generated_events:
        if args.format == "cef":
            raw_lines.append(ev["cef"])
        elif args.format == "rfc5424":
            raw_lines.append(ev["rfc5424"])
        elif args.format == "both":
            raw_lines.append(f"[CEF] {ev['cef']}")
            raw_lines.append(f"[RFC5424] {ev['rfc5424']}")

    # Dosyaya append etme
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "a", encoding="utf-8") as f:
            for line in raw_lines:
                f.write(line + "\n")
        print(f"{TerminalColors.GREEN}[BASARILI] {len(raw_lines)} adet sentetik SOC logu kaydedildi: {args.output}{TerminalColors.RESET}")

    # Ekrana basma
    if show_stdout:
        print(f"\n{TerminalColors.YELLOW}--- URETILEN SENTETIK SOC TELEMETRI LOGLARI ({len(generated_events)} Olay) ---{TerminalColors.RESET}")
        for ev in generated_events:
            sev_color = TerminalColors.RED if ev["severity"] == "CRITICAL" else TerminalColors.YELLOW
            print(f"{sev_color}[{ev['severity']}]{TerminalColors.RESET} {ev['summary']}")
            if args.format in ["cef", "both"]:
                print(f"  {TerminalColors.CYAN}CEF: {ev['cef']}{TerminalColors.RESET}")
            if args.format in ["rfc5424", "both"]:
                print(f"  {TerminalColors.WHITE}RFC5424: {ev['rfc5424']}{TerminalColors.RESET}")
            print("")

    return 0


if __name__ == "__main__":
    sys.exit(main())

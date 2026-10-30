#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kurumsal Ağ ve Siber Güvenlik Mimarisi - Güvenlik Duvarı Vendor CLI Dönüştürücüsü
(Firewall Policy to Vendor CLI Exporter - Fortinet FortiOS & Palo Alto PAN-OS)

Bu script, doğrulanmış kurumsal güvenlik politikası JSON dosyasını okuyarak
üreticiye özel (Fortinet FortiOS veya Palo Alto Networks PAN-OS) konfigürasyon
komutlarına derler ve çıktı dosyası (.cfg / .set) veya terminale aktarır.

Standart Kütüphaneler: json, argparse, sys, pathlib, typing
Harici bağımlılık gerektirmez.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    CYAN = "\033[96m"


def print_banner() -> None:
    """CLI dönüştürücü başlığını ekrana basar."""
    banner = f"""{TerminalColors.CYAN}{TerminalColors.BOLD}
================================================================================
     FIREWALL POLICY TO VENDOR CLI EXPORTER (Fortinet & Palo Alto)
================================================================================{TerminalColors.RESET}"""
    print(banner)


class VendorCLIExporter:
    """Güvenlik kurallarını FortiOS ve PAN-OS CLI sözdizimine dönüştüren motor."""

    def __init__(self, rules_path: Path) -> None:
        self.rules_path = rules_path
        self.rules: List[Dict[str, Any]] = []

    def load_rules(self) -> bool:
        """Kural JSON dosyasını okur ve doğrular."""
        if not self.rules_path.exists():
            print(f"{TerminalColors.RED}[HATA] Kural dosyasi bulunamadi: {self.rules_path}{TerminalColors.RESET}")
            return False

        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                self.rules = data
            elif isinstance(data, dict) and "rules" in data:
                self.rules = data["rules"]
            else:
                print(f"{TerminalColors.RED}[HATA] Gecersiz JSON yapisi. 'rules' alani bulunamadi.{TerminalColors.RESET}")
                return False

            return True
        except Exception as exc:
            print(f"{TerminalColors.RED}[HATA] JSON okuma hatasi: {exc}{TerminalColors.RESET}")
            return False

    def export_fortinet(self) -> str:
        """
        Kuralları Fortinet FortiOS CLI formatına dönüştürür.
        Çıktı formatı:
            config firewall policy
                edit <rule_id>
                    set name "<name>"
                    set srcintf "<source_zone>"
                    set dstintf "<dest_zone>"
                    set srcaddr "<source_cidr>"
                    set dstaddr "<dest_cidr>"
                    set action <accept/deny>
                    set schedule "always"
                    set service "ALL"
                    set utm-status enable
                next
            end
        """
        lines: List[str] = []
        lines.append("# ============================================================================")
        lines.append("# FORTINET FORTIOS FIREWALL POLICY EXPORT")
        lines.append(f"# Toplam Kural Sayisi: {len(self.rules)}")
        lines.append("# ============================================================================")
        lines.append("config firewall policy")

        for index, rule in enumerate(self.rules, start=1):
            rule_id = rule.get("rule_id", str(index))
            name = rule.get("name", f"RULE_{index}")
            src_zone = rule.get("source_zone", "any")
            dst_zone = rule.get("dest_zone", "any")
            src_cidr = rule.get("source_cidr", "0.0.0.0/0")
            dst_cidr = rule.get("dest_cidr", "0.0.0.0/0")
            action = "accept" if str(rule.get("action", "")).upper() == "PERMIT" else "deny"
            utm = "enable" if rule.get("threat_inspection", False) else "disable"

            # FortiOS Policy bloğu
            lines.append(f"    edit {rule_id}")
            lines.append(f'        set name "{name}"')
            lines.append(f'        set srcintf "{src_zone}"')
            lines.append(f'        set dstintf "{dst_zone}"')
            lines.append(f'        set srcaddr "{src_cidr}"')
            lines.append(f'        set dstaddr "{dst_cidr}"')
            lines.append(f"        set action {action}")
            lines.append('        set schedule "always"')
            lines.append('        set service "ALL"')
            lines.append(f"        set utm-status {utm}")
            if utm == "enable":
                lines.append('        set ssl-ssh-profile "deep-inspection"')
                lines.append('        set ips-sensor "Enterprise-IPS-Strict"')
                lines.append('        set av-profile "Enterprise-AV"')
            lines.append("    next")

        lines.append("end")
        lines.append("")
        return "\n".join(lines)

    def export_paloalto(self) -> str:
        """
        Kuralları Palo Alto Networks PAN-OS CLI set formatına dönüştürür.
        Çıktı formatı:
            set rulebase security rules "<name>" from <source_zone> to <dest_zone> source <source_cidr> destination <dest_cidr> service any application any action <allow/deny>
        """
        lines: List[str] = []
        lines.append("# ============================================================================")
        lines.append("# PALO ALTO NETWORKS PAN-OS SECURITY RULES EXPORT (SET FORMAT)")
        lines.append(f"# Toplam Kural Sayisi: {len(self.rules)}")
        lines.append("# ============================================================================")

        for index, rule in enumerate(self.rules, start=1):
            name = rule.get("name", f"RULE_{index}")
            src_zone = rule.get("source_zone", "any")
            dst_zone = rule.get("dest_zone", "any")
            src_cidr = rule.get("source_cidr", "any")
            dst_cidr = rule.get("dest_cidr", "any")
            action = "allow" if str(rule.get("action", "")).upper() == "PERMIT" else "deny"
            threat = rule.get("threat_inspection", False)

            # Temel Kural Satırı
            cmd = (
                f'set rulebase security rules "{name}" '
                f"from {src_zone} "
                f"to {dst_zone} "
                f"source {src_cidr} "
                f"destination {dst_cidr} "
                f"service any "
                f"application any "
                f"action {action}"
            )
            lines.append(cmd)

            # Tehdit denetimi açıksa güvenlik profili ekle
            if threat and action == "allow":
                lines.append(
                    f'set rulebase security rules "{name}" profile-setting group "Strict-Threat-Prevention"'
                )
                lines.append(f'set rulebase security rules "{name}" log-end yes')
            elif action == "deny":
                lines.append(f'set rulebase security rules "{name}" log-start yes')

        lines.append("")
        return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Firewall Kurallarını FortiOS ve PAN-OS CLI Konfigürasyonuna Dönüştürücü"
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=Path(__file__).parent.parent / "01-kural-dogrulayici-ve-analiz" / "sample_network_rules.json",
        help="Kaynak kurallar JSON dosyasının yolu",
    )
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        choices=["fortinet", "paloalto", "both"],
        help="Hedef güvenlik duvarı üreticisi: fortinet, paloalto veya both",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Oluşturulan komutların kaydedileceği dosya yolu (verilmezse ekrana basılır)",
    )

    args = parser.parse_args()

    print_banner()

    exporter = VendorCLIExporter(rules_path=args.rules)
    if not exporter.load_rules():
        return 2

    print(f"{TerminalColors.GREEN}[BILGI] {len(exporter.rules)} adet kural basariyla yuklendi.{TerminalColors.RESET}")
    print(f"{TerminalColors.CYAN}[BILGI] Hedef platform: {args.target.upper()}{TerminalColors.RESET}")

    output_texts: Dict[str, str] = {}

    if args.target in ["fortinet", "both"]:
        fortinet_cli = exporter.export_fortinet()
        output_texts["fortinet"] = fortinet_cli

    if args.target in ["paloalto", "both"]:
        paloalto_cli = exporter.export_paloalto()
        output_texts["paloalto"] = paloalto_cli

    # Çıktı yönetimi
    if args.output:
        if args.target == "both":
            out_base = args.output.parent
            fn_file = out_base / "fortinet_rules.cfg"
            pa_file = out_base / "paloalto_rules.set"
            fn_file.write_text(output_texts["fortinet"], encoding="utf-8")
            pa_file.write_text(output_texts["paloalto"], encoding="utf-8")
            print(f"{TerminalColors.GREEN}[BASARILI] Fortinet dosyasina yazildi: {fn_file}{TerminalColors.RESET}")
            print(f"{TerminalColors.GREEN}[BASARILI] Palo Alto dosyasina yazildi: {pa_file}{TerminalColors.RESET}")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            content = output_texts[args.target]
            args.output.write_text(content, encoding="utf-8")
            print(f"{TerminalColors.GREEN}[BASARILI] Yapilandirma dosyasina kaydedildi: {args.output}{TerminalColors.RESET}")
    else:
        # Ekrana bas
        for vendor, content in output_texts.items():
            print(f"\n{TerminalColors.YELLOW}--- {vendor.upper()} CLI CIKTISI ---{TerminalColors.RESET}")
            print(content)

    return 0


if __name__ == "__main__":
    sys.exit(main())

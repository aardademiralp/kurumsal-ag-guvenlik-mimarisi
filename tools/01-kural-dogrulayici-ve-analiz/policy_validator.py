#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kurumsal Ağ ve Siber Güvenlik Mimarisi - Güvenlik Duvarı Kural Doğrulayıcı ve Analiz Motoru
(Enterprise Firewall Policy Validator & Microsegmentation Security Engine)

Bu araç, tanımlanmış güvenlik duvarı kurallarını JSON şemasına, Zero-Trust ilkelerine,
mikro-segmentasyon kurallarına ve kural çakışma (shadowing) mantığına göre analiz eder.

Standart Kütüphaneler: json, ipaddress, argparse, sys, pathlib, typing
Harici bağımlılık gerektirmez.
"""

import argparse
import ipaddress
import json
import sys
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
    """Doğrulayıcı başlangıç başlığını yazdırır."""
    banner = f"""{TerminalColors.CYAN}{TerminalColors.BOLD}
================================================================================
    HOLDING & UNIVERSITE KURUMSAL AG GUVENLIK DUVARI KURAL DOGRULAYICI
           Enterprise Firewall Policy & Microsegmentation Validator
================================================================================{TerminalColors.RESET}"""
    print(banner)


class PolicyValidator:
    """
    Güvenlik duvarı kurallarını doğrulayan ve güvenlik analizlerini yürüten motor.
    """

    def __init__(self, rules_path: Path, schema_path: Optional[Path] = None) -> None:
        self.rules_path = rules_path
        self.schema_path = schema_path
        self.raw_data: Dict[str, Any] = {}
        self.rules: List[Dict[str, Any]] = []
        self.findings: List[Dict[str, Any]] = []
        self.stats = {
            "total_rules": 0,
            "permit_rules": 0,
            "deny_rules": 0,
            "inspected_rules": 0,
            "critical_alerts": 0,
            "warnings": 0,
            "shadowed_rules": 0,
            "default_deny_present": False,
            "score": 100,
        }

    def load_data(self) -> bool:
        """Kural dosyasını yükler ve JSON doğruluğunu kontrol eder."""
        try:
            if not self.rules_path.exists():
                print(f"{TerminalColors.RED}[HATA] Kural dosyasi bulunamadi: {self.rules_path}{TerminalColors.RESET}")
                return False

            with open(self.rules_path, "r", encoding="utf-8") as file:
                self.raw_data = json.load(file)

            if isinstance(self.raw_data, list):
                self.rules = self.raw_data
            elif isinstance(self.raw_data, dict) and "rules" in self.raw_data:
                self.rules = self.raw_data["rules"]
            else:
                print(f"{TerminalColors.RED}[HATA] Gecersiz JSON formati. 'rules' dizisi bulunamadi.{TerminalColors.RESET}")
                return False

            self.stats["total_rules"] = len(self.rules)
            return True

        except json.JSONDecodeError as exc:
            print(f"{TerminalColors.RED}[HATA] JSON ayristirma hatasi: {exc}{TerminalColors.RESET}")
            return False
        except Exception as exc:
            print(f"{TerminalColors.RED}[HATA] Beklenmeyen hata: {exc}{TerminalColors.RESET}")
            return False

    def validate_schema_structure(self) -> bool:
        """JSON şeması alanlarını ve veri tiplerini standart kütüphaneyle doğrular."""
        required_fields = [
            "rule_id",
            "name",
            "source_zone",
            "source_cidr",
            "dest_zone",
            "dest_cidr",
            "service_ports",
            "action",
            "threat_inspection",
        ]
        valid_actions = {"PERMIT", "DENY"}
        schema_valid = True

        for index, rule in enumerate(self.rules, start=1):
            rule_id = rule.get("rule_id", f"INDEX-{index}")

            # 1. Zorunlu alan kontrolü
            missing = [field for field in required_fields if field not in rule]
            if missing:
                self._add_finding(
                    level="ERROR",
                    rule_id=rule_id,
                    rule_name=rule.get("name", "Bilinmeyen"),
                    category="Schema",
                    message=f"Eksik zorunlu alanlar: {', '.join(missing)}",
                )
                schema_valid = False
                continue

            # 2. Action kontrolü
            action = str(rule.get("action", "")).upper()
            if action not in valid_actions:
                self._add_finding(
                    level="ERROR",
                    rule_id=rule_id,
                    rule_name=rule["name"],
                    category="Schema",
                    message=f"Gecersiz eylem '{action}'. Sadece 'PERMIT' veya 'DENY' kabul edilir.",
                )
                schema_valid = False

            # 3. CIDR geçerlilik kontrolü
            for cidr_key in ["source_cidr", "dest_cidr"]:
                cidr_val = rule[cidr_key]
                try:
                    ipaddress.ip_network(cidr_val, strict=False)
                except ValueError:
                    self._add_finding(
                        level="ERROR",
                        rule_id=rule_id,
                        rule_name=rule["name"],
                        category="Schema",
                        message=f"Gecersiz IPv4 CIDR formati '{cidr_key}': {cidr_val}",
                    )
                    schema_valid = False

            # 4. Port listesi kontrolü
            ports = rule.get("service_ports", [])
            if not isinstance(ports, list) or len(ports) == 0:
                self._add_finding(
                    level="WARNING",
                    rule_id=rule_id,
                    rule_name=rule["name"],
                    category="Schema",
                    message="'service_ports' bos veya liste formatinda degil.",
                )
                self.stats["warnings"] += 1

            # İstatistikleri güncelle
            if action == "PERMIT":
                self.stats["permit_rules"] += 1
            elif action == "DENY":
                self.stats["deny_rules"] += 1

            if rule.get("threat_inspection", False):
                self.stats["inspected_rules"] += 1

        return schema_valid

    def audit_microsegmentation(self) -> None:
        """
        Güvenlik Analizi 1: Mikro-Segmentasyon Denetimi
        Öğrenci ağı (10.100.0.0/16) kaynaklı olup Kampüs İdari Sistemlerine (10.101.20.0/24)
        veya LMS Veri Tabanı / İç Sunucu Ağına (10.101.30.0/24) giden ve action değeri PERMIT
        olan kuralları tespit eder ve CRITICAL ALERT üretir.
        """
        student_net = ipaddress.ip_network("10.100.0.0/16")
        admin_net = ipaddress.ip_network("10.101.20.0/24")
        lms_db_net = ipaddress.ip_network("10.101.30.0/24")
        lms_web_host = ipaddress.ip_network("10.101.30.20/32")
        any_network = ipaddress.ip_network("0.0.0.0/0")

        for rule in self.rules:
            try:
                src = ipaddress.ip_network(rule["source_cidr"], strict=False)
                dst = ipaddress.ip_network(rule["dest_cidr"], strict=False)
            except ValueError:
                continue

            action = str(rule.get("action", "")).upper()
            dest_zone = rule.get("dest_zone", "")

            # Kaynak öğrenci ağı veya alt ağı mı?
            if src.overlaps(student_net) or rule.get("source_zone") == "Zone_Campus_Student":
                # 1. Kampüs İdari Ağına PERMIT kuralı kontrolü
                is_admin_target = (
                    dest_zone == "Zone_Campus_Admin"
                    or (dst != any_network and dst.overlaps(admin_net))
                )
                if is_admin_target and action == "PERMIT":
                    self._add_finding(
                        level="CRITICAL",
                        rule_id=rule["rule_id"],
                        rule_name=rule["name"],
                        category="Microsegmentation",
                        message=(
                            f"[CRITICAL ALERT] Mikro-Segmentasyon Ihlali: Ogrenci agindan ({src}) "
                            f"Kampus Idari Sistemlerine ({dst} / {dest_zone}) PERMIT kurali tespit edildi!"
                        ),
                    )
                    self.stats["critical_alerts"] += 1
                    self.stats["score"] -= 35

                # 2. LMS Veritabanı ve Çekirdek Sunucularına PERMIT kuralı kontrolü
                is_lms_target = (
                    dest_zone == "Zone_Campus_DC_LMS"
                    or (dst != any_network and dst.overlaps(lms_db_net))
                )
                if is_lms_target and action == "PERMIT":
                    ports = rule.get("service_ports", [])
                    is_only_web_ports = len(ports) > 0 and all(p in [80, 443, "80", "443"] for p in ports)

                    # Yalnızca onaylı LMS Web Host (10.101.30.20/32) ve sadece web portları meşrudur
                    if dst == lms_web_host and is_only_web_ports:
                        pass
                    else:
                        self._add_finding(
                            level="CRITICAL",
                            rule_id=rule["rule_id"],
                            rule_name=rule["name"],
                            category="Microsegmentation",
                            message=(
                                f"[CRITICAL ALERT] Mikro-Segmentasyon Ihlali: Ogrenci agindan ({src}) "
                                f"LMS Veritabani/Iç Sunucu Ağına ({dst}) doğrudan PERMIT kurali tespit edildi! Portlar: {ports}."
                            ),
                        )
                        self.stats["critical_alerts"] += 1
                        self.stats["score"] -= 35

    def audit_any_to_any_and_shadowing(self) -> None:
        """
        Güvenlik Analizi 2: Aşırı Geniş Kurallar ve Kural Çakışması (Shadowing) Denetimi
        1. 0.0.0.0/0 -> 0.0.0.0/0 olan PERMIT kurallarını yakalar.
        2. Kendisinden önce gelen daha kapsayıcı bir kural tarafından gölgelenen kuralları tespit eder.
        """
        any_network = ipaddress.ip_network("0.0.0.0/0")
        processed_rules: List[Tuple[int, Dict[str, Any], ipaddress.IPv4Network, ipaddress.IPv4Network]] = []

        for index, rule in enumerate(self.rules, start=1):
            try:
                src_net = ipaddress.ip_network(rule["source_cidr"], strict=False)
                dst_net = ipaddress.ip_network(rule["dest_cidr"], strict=False)
            except ValueError:
                continue

            action = str(rule.get("action", "")).upper()
            ports = rule.get("service_ports", [])
            is_any_ports = "any" in ports or ["any"] == ports or len(ports) == 0

            # 1. Any-to-Any PERMIT kontrolü
            if src_net == any_network and dst_net == any_network and action == "PERMIT":
                self._add_finding(
                    level="CRITICAL",
                    rule_id=rule["rule_id"],
                    rule_name=rule["name"],
                    category="Any-to-Any",
                    message="0.0.0.0/0 -> 0.0.0.0/0 PERMIT kurali tespit edildi! Bu kural tum guvenlik duvarini atlatir.",
                )
                self.stats["critical_alerts"] += 1
                self.stats["score"] -= 40

            # 2. Shadowing (Gölgeleme) kontrolü
            for prev_idx, prev_rule, prev_src, prev_dst in processed_rules:
                prev_action = str(prev_rule.get("action", "")).upper()
                prev_ports = prev_rule.get("service_ports", [])
                prev_is_any_ports = "any" in prev_ports or ["any"] == prev_ports or len(prev_ports) == 0

                same_zones = (
                    prev_rule["source_zone"] in ["any", rule["source_zone"]]
                    and prev_rule["dest_zone"] in ["any", rule["dest_zone"]]
                )

                if same_zones:
                    src_covered = (prev_src == any_network) or (src_net.subnet_of(prev_src))
                    dst_covered = (prev_dst == any_network) or (dst_net.subnet_of(prev_dst))

                    # Port kapsama kontrolü
                    if prev_is_any_ports:
                        ports_covered = True
                    else:
                        prev_port_set = set(str(p) for p in prev_ports)
                        curr_port_set = set(str(p) for p in ports)
                        ports_covered = curr_port_set.issubset(prev_port_set) and not is_any_ports

                    if src_covered and dst_covered and ports_covered:
                        # Eğer önceki kural da aynı eyleme sahipse veya önceki kural DENY ediyorsa
                        if prev_action == action or prev_action == "DENY":
                            self._add_finding(
                                level="WARNING",
                                rule_id=rule["rule_id"],
                                rule_name=rule["name"],
                                category="Shadowing",
                                message=(
                                    f"GOLGELENMIS KURAL (SHADOWED): Bu kural, onceki '{prev_rule['name']}' "
                                    f"(Rule ID: {prev_rule['rule_id']}, Sira: {prev_idx}) tarafindan tamamen kapsanmaktadir."
                                ),
                            )
                            self.stats["shadowed_rules"] += 1
                            self.stats["warnings"] += 1
                            self.stats["score"] -= 5
                            break

            processed_rules.append((index, rule, src_net, dst_net))

    def audit_default_deny(self) -> None:
        """
        Güvenlik Analizi 3: Default-Deny Catch-All Kontrolü
        Kural setinin en son kuralının 0.0.0.0/0 -> 0.0.0.0/0 DENY olup olmadığını denetler.
        """
        if not self.rules:
            return

        last_rule = self.rules[-1]
        try:
            src_net = ipaddress.ip_network(last_rule.get("source_cidr", "255.255.255.255/32"), strict=False)
            dst_net = ipaddress.ip_network(last_rule.get("dest_cidr", "255.255.255.255/32"), strict=False)
            any_network = ipaddress.ip_network("0.0.0.0/0")
            action = str(last_rule.get("action", "")).upper()

            if src_net == any_network and dst_net == any_network and action == "DENY":
                self.stats["default_deny_present"] = True
            else:
                self._add_finding(
                    level="CRITICAL",
                    rule_id=last_rule.get("rule_id", "LAST"),
                    rule_name=last_rule.get("name", "Son_Kural"),
                    category="Default-Deny",
                    message="Kural setinin son kurali EXPLICIT DEFAULT-DENY (0.0.0.0/0 -> 0.0.0.0/0 DENY) degil!",
                )
                self.stats["critical_alerts"] += 1
                self.stats["score"] -= 30
        except Exception as exc:
            self._add_finding(
                level="ERROR",
                rule_id="LAST",
                rule_name="Son_Kural",
                category="Default-Deny",
                message=f"Default-deny analizi sirasinda hata: {exc}",
            )

    def _add_finding(
        self, level: str, rule_id: Any, rule_name: str, category: str, message: str
    ) -> None:
        """Bulguyu kaydeder."""
        self.findings.append(
            {
                "level": level,
                "rule_id": str(rule_id),
                "rule_name": rule_name,
                "category": category,
                "message": message,
            }
        )

    def print_report(self) -> None:
        """Denetim bulgularını ve skor kartını ekrana basar."""
        print(f"\n{TerminalColors.BOLD}--- DENETIM BULGULARI (AUDIT FINDINGS) ---{TerminalColors.RESET}")

        if not self.findings:
            print(f"{TerminalColors.GREEN}[BASARILI] Hicbir kural ihlali veya guvenlik acigi bulunamadi! Tum kontroller basarili.{TerminalColors.RESET}")
        else:
            for item in self.findings:
                level = item["level"]
                if level == "CRITICAL":
                    color = f"{TerminalColors.RED}{TerminalColors.BOLD}"
                    tag = "[CRITICAL ALERT]"
                elif level == "WARNING":
                    color = TerminalColors.YELLOW
                    tag = "[UYARI]"
                else:
                    color = TerminalColors.CYAN
                    tag = "[BILGI]"

                print(
                    f"{color}{tag} [{item['category']}] Kural ID: {item['rule_id']} ({item['rule_name']})\n"
                    f"  |-- {item['message']}{TerminalColors.RESET}"
                )

        # Skor kartı
        final_score = max(0, min(100, self.stats["score"]))
        score_color = TerminalColors.GREEN if final_score >= 85 else (
            TerminalColors.YELLOW if final_score >= 60 else TerminalColors.RED
        )

        default_deny_badge = (
            f"{TerminalColors.GREEN}MEVCUT (GECTI){TerminalColors.RESET}"
            if self.stats["default_deny_present"]
            else f"{TerminalColors.RED}EKSIK (KALDI){TerminalColors.RESET}"
        )

        print(f"\n{TerminalColors.CYAN}{TerminalColors.BOLD}================================================================================{TerminalColors.RESET}")
        print(f"{TerminalColors.BOLD}             GUVENLIK VE POLITIKA SKOR KARTI (SECURITY AUDIT SCORECARD)         {TerminalColors.RESET}")
        print(f"{TerminalColors.CYAN}================================================================================{TerminalColors.RESET}")
        print(f"  Toplam Denetlenen Kural Sayisi : {self.stats['total_rules']}")
        print(f"  Izin Veren Kurallar (PERMIT)   : {self.stats['permit_rules']}")
        print(f"  Engelleme Kurallari (DENY)     : {self.stats['deny_rules']}")
        print(f"  L7 Tehdit Teftisi Acik         : {self.stats['inspected_rules']} / {self.stats['total_rules']}")
        print(f"  Kritik Guvenlik Ihlalleri      : {self.stats['critical_alerts']}")
        print(f"  Golgede Kalan (Shadowed) Kural : {self.stats['shadowed_rules']}")
        print(f"  Default-Deny Catch-All Durumu  : {default_deny_badge}")
        print(f"{TerminalColors.CYAN}--------------------------------------------------------------------------------{TerminalColors.RESET}")
        print(f"  GUVENLIK UYUM SKORU            : {score_color}{TerminalColors.BOLD}{final_score} / 100{TerminalColors.RESET}")
        print(f"{TerminalColors.CYAN}================================================================================{TerminalColors.RESET}\n")


def inject_test_violation(rules_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test ve demonstrasyon amaciyla kural kumesine yapay bir mikro-segmentasyon ihlali ekler."""
    breach_rule = {
        "rule_id": "TEST-BREACH-99",
        "name": "TEST_STUDENT_TO_ADMIN_BREACH",
        "source_zone": "Zone_Campus_Student",
        "source_cidr": "10.100.12.0/24",
        "dest_zone": "Zone_Campus_Admin",
        "dest_cidr": "10.101.20.5/32",
        "service_ports": [445, 3389],
        "action": "PERMIT",
        "threat_inspection": False,
        "description": "Simulasyon amaciyla enjekte edilmis guvenlik ihlali kurali",
    }
    rules_copy = json.loads(json.dumps(rules_data))
    if "rules" in rules_copy:
        rules_copy["rules"].insert(5, breach_rule)
    return rules_copy


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Kurumsal Ağ Güvenlik Duvarı Kural Doğrulayıcı ve Mikro-Segmentasyon Denetçisi"
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=Path(__file__).parent / "sample_network_rules.json",
        help="Doğrulanacak kurallar JSON dosyasının yolu",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).parent / "rules_schema.json",
        help="JSON şema dosyasının yolu",
    )
    parser.add_argument(
        "--test-violation",
        action="store_true",
        help="Doğrulayıcının ihlali tespit etme yeteneğini test etmek için yapay mikro-segmentasyon ihlali enjekte eder",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Herhangi bir uyarı (warning) tespit edilirse sıfır olmayan çıkış kodu döndürür",
    )

    args = parser.parse_args()

    print_banner()

    validator = PolicyValidator(rules_path=args.rules, schema_path=args.schema)

    if not validator.load_data():
        return 2

    if args.test_violation:
        print(f"{TerminalColors.YELLOW}[TEST MODU] Yapay bir mikro-segmentasyon ihlali enjekte ediliyor...{TerminalColors.RESET}")
        validator.rules = inject_test_violation(validator.raw_data)["rules"]
        validator.stats["total_rules"] = len(validator.rules)

    # 1. Şema ve Alan Geçerlilik Analizi
    schema_ok = validator.validate_schema_structure()
    if not schema_ok:
        print(f"{TerminalColors.RED}[HATA] Kural sema yapisinda kritik hatalar tespit edildi.{TerminalColors.RESET}")

    # 2. Mikro-Segmentasyon Güvenlik Analizi
    validator.audit_microsegmentation()

    # 3. Any-to-Any ve Shadowing Analizi
    validator.audit_any_to_any_and_shadowing()

    # 4. Default-Deny Kontrolü
    validator.audit_default_deny()

    # Raporu yazdır
    validator.print_report()

    if validator.stats["critical_alerts"] > 0:
        return 1
    if args.strict and validator.stats["warnings"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

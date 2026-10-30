#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kurumsal Ağ ve Siber Güvenlik Mimarisi - Otomasyon ve Test Orkestratörü
(Enterprise Network Automation Test Suite & Verification Orchestrator)

Bu script, kurumsal ağ ve güvenlik mimarisi projesinde geliştirilen tüm Python
otomasyon araçlarını tek bir komutla sıralı olarak çalıştırır, doğrular ve
derlenen konfigürasyon/log çıktılarını 'build/' dizininde toplar.

İşlem Adımları:
  1. policy_validator.py ile kural doğrulama ve mikro-segmentasyon analizi
  2. policy_validator.py --test-violation ile ihlal tespit mekanizması doğrulaması
  3. vendor_exporter.py ile Fortinet FortiOS (.cfg) derlemesi
  4. vendor_exporter.py ile Palo Alto PAN-OS (.set) derlemesi
  5. bandwidth_engine.py ile 10.000 öğrencili kampüs kapasite ve LACP boyutlandırması
  6. syslog_generator.py ile 10 adet sentetik SOC telemetri logu üretimi

Standart Kütüphaneler: subprocess, sys, pathlib, time, typing
Harici bağımlılık gerektirmez.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"


def print_header() -> None:
    """Orkestratör ana başlığını basar."""
    header = f"""{TerminalColors.CYAN}{TerminalColors.BOLD}
================================================================================
   KURUMSAL AG VE SIBER GUVENLIK MIMARISI - TEST VE OTOMASYON MERKEZI
       Enterprise DevSecOps & Network Automation Test Suite Orchestrator
================================================================================{TerminalColors.RESET}"""
    print(header)


class AutomationOrchestrator:
    """Tüm test ve derleme adımlarını yöneten orkestratör sınıfı."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.tools_dir = base_dir / "tools"
        self.build_dir = self.tools_dir / "05-otomasyon-test-merkezi" / "build"
        self.results: List[Dict[str, Any]] = []

        # Araç yolları
        self.tool_validator = self.tools_dir / "01-kural-dogrulayici-ve-analiz" / "policy_validator.py"
        self.tool_exporter = self.tools_dir / "02-vendor-cli-donusturucu" / "vendor_exporter.py"
        self.tool_bandwidth = self.tools_dir / "03-kapasite-ve-qos-hesaplayici" / "bandwidth_engine.py"
        self.tool_syslog = self.tools_dir / "04-soc-telemetri-simulatoru" / "syslog_generator.py"

    def setup_build_dir(self) -> None:
        """Derleme çıktı dizinini hazırlar."""
        self.build_dir.mkdir(parents=True, exist_ok=True)
        print(f"{TerminalColors.CYAN}[HAZIRLIK] Derleme dizini hazirlandi: {self.build_dir}{TerminalColors.RESET}\n")

    def run_command(
        self,
        step_id: int,
        title: str,
        cmd: List[str],
        expected_exit_codes: Tuple[int, ...] = (0,),
    ) -> bool:
        """Belirtilen Python komutunu çalıştırır ve süre/durum takibi yapar."""
        print(f"{TerminalColors.BOLD}[ADIM {step_id}] {title}...{TerminalColors.RESET}")
        print(f"  {TerminalColors.WHITE}Komut: {' '.join(cmd)}{TerminalColors.RESET}")

        start_time = time.time()
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            elapsed = time.time() - start_time
            success = process.returncode in expected_exit_codes

            if success:
                print(f"  {TerminalColors.GREEN}[+] BASARILI ({elapsed:.2f} sn) - Cikis Kodu: {process.returncode}{TerminalColors.RESET}")
                # Özet çıktıdan ilk 2 satırı göster
                out_lines = [line.strip() for line in process.stdout.strip().split("\n") if line.strip()]
                for line in out_lines[-3:]:
                    print(f"      {TerminalColors.WHITE}| {line}{TerminalColors.RESET}")
            else:
                print(f"  {TerminalColors.RED}[-] BASARISIZ ({elapsed:.2f} sn) - Cikis Kodu: {process.returncode}{TerminalColors.RESET}")
                if process.stderr:
                    print(f"      {TerminalColors.RED}Hata: {process.stderr.strip()}{TerminalColors.RESET}")

            self.results.append(
                {
                    "step": step_id,
                    "title": title,
                    "duration": elapsed,
                    "success": success,
                    "returncode": process.returncode,
                }
            )
            print("")
            return success

        except Exception as exc:
            elapsed = time.time() - start_time
            print(f"  {TerminalColors.RED}[-] CALISTIRMA HATASI: {exc}{TerminalColors.RESET}\n")
            self.results.append(
                {
                    "step": step_id,
                    "title": title,
                    "duration": elapsed,
                    "success": False,
                    "returncode": -1,
                }
            )
            return False

    def execute_suite(self) -> bool:
        """Tüm doğrulama ve derleme adımlarını sırayla icra eder."""
        self.setup_build_dir()
        all_passed = True

        # ADIM 1: Policy Validator (Standart Temiz Kural Doğrulaması)
        step1 = self.run_command(
            step_id=1,
            title="Kural Seti Semasi, Mikro-Segmentasyon ve Default-Deny Analizi",
            cmd=[sys.executable, str(self.tool_validator)],
            expected_exit_codes=(0,),
        )
        all_passed = all_passed and step1

        # ADIM 2: Policy Validator (İhlal Tespit Mekanizması Testi)
        step2 = self.run_command(
            step_id=2,
            title="Mikro-Segmentasyon Ihlal Tespit Mekanizmasi Testi (--test-violation)",
            cmd=[sys.executable, str(self.tool_validator), "--test-violation"],
            expected_exit_codes=(1,),  # İhlal başarıyla yakalandığında çıkış kodu 1 döner
        )
        all_passed = all_passed and step2

        # ADIM 3: Vendor Exporter (Fortinet CLI Derlemesi)
        fortinet_out = self.build_dir / "fortinet_rules.cfg"
        step3 = self.run_command(
            step_id=3,
            title="Fortinet FortiOS Firewall Policy CLI Derlemesi",
            cmd=[
                sys.executable,
                str(self.tool_exporter),
                "--target",
                "fortinet",
                "--output",
                str(fortinet_out),
            ],
            expected_exit_codes=(0,),
        )
        all_passed = all_passed and step3

        # ADIM 4: Vendor Exporter (Palo Alto CLI Derlemesi)
        paloalto_out = self.build_dir / "paloalto_rules.set"
        step4 = self.run_command(
            step_id=4,
            title="Palo Alto Networks PAN-OS Security Rules CLI Derlemesi",
            cmd=[
                sys.executable,
                str(self.tool_exporter),
                "--target",
                "paloalto",
                "--output",
                str(paloalto_out),
            ],
            expected_exit_codes=(0,),
        )
        all_passed = all_passed and step4

        # ADIM 5: Bandwidth Engine (10.000 Öğrenci & 700 Personel Kapasite Boyutlandırma)
        step5 = self.run_command(
            step_id=5,
            title="10.000 Ogrencili Kampus Bant Genisligi ve 10G LACP Boyutlandirma Analizi",
            cmd=[
                sys.executable,
                str(self.tool_bandwidth),
                "--students",
                "10000",
                "--concurrency",
                "0.40",
                "--student-mbps",
                "8",
                "--staff",
                "700",
                "--staff-mbps",
                "15",
                "--overbooking",
                "4",
            ],
            expected_exit_codes=(0,),
        )
        all_passed = all_passed and step5

        # ADIM 6: SOC Telemetri Simülatörü (10 Sentetik Olay Log Dosyasına Kaydedilir)
        soc_log_out = self.build_dir / "soc_synthetic_events.log"
        # Eski test logu varsa temizleyelim
        if soc_log_out.exists():
            soc_log_out.unlink()

        step6 = self.run_command(
            step_id=6,
            title="SOC Sentetik Telemetri Log Uretimi (CEF ve RFC 5424 Formatinda 10 Olay)",
            cmd=[
                sys.executable,
                str(self.tool_syslog),
                "--scenario",
                "all",
                "--count",
                "10",
                "--format",
                "both",
                "--output",
                str(soc_log_out),
            ],
            expected_exit_codes=(0,),
        )
        all_passed = all_passed and step6

        # Oluşturulan dosyaları kontrol et
        self.verify_build_artifacts(fortinet_out, paloalto_out, soc_log_out)

        # Nihai Raporu Bas
        self.print_summary_report(all_passed)
        return all_passed

    def verify_build_artifacts(
        self, fn_file: Path, pa_file: Path, soc_file: Path
    ) -> None:
        """Derlenen dosyaların varlığını ve boyutlarını doğrular."""
        print(f"{TerminalColors.BOLD}--- DERLENEN CIKTI VE ARTIFACT KONTROLU ---{TerminalColors.RESET}")
        for path in [fn_file, pa_file, soc_file]:
            if path.exists():
                size = path.stat().st_size
                lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
                print(f"  {TerminalColors.GREEN}[OK]{TerminalColors.RESET} {path.name:<26} : {size:>6} byte ({lines} satir)")
            else:
                print(f"  {TerminalColors.RED}[HATA] {path.name:<26} : Dosya olusturulamadi!{TerminalColors.RESET}")
        print("")

    def print_summary_report(self, all_passed: bool) -> None:
        """Özet doğrulama raporunu ve bitiş skorunu basar."""
        total_time = sum(r["duration"] for r in self.results)

        print(f"{TerminalColors.CYAN}{TerminalColors.BOLD}================================================================================{TerminalColors.RESET}")
        print(f"{TerminalColors.BOLD}                    GENEL TEST VE DOGRULAMA RAPORU                             {TerminalColors.RESET}")
        print(f"{TerminalColors.CYAN}================================================================================{TerminalColors.RESET}")

        for res in self.results:
            status = (
                f"{TerminalColors.GREEN}[GECTI]{TerminalColors.RESET}"
                if res["success"]
                else f"{TerminalColors.RED}[KALDI]{TerminalColors.RESET}"
            )
            print(f"  Adim {res['step']}: {res['title'][:55]:<56} {status} ({res['duration']:.2f} sn)")

        print(f"{TerminalColors.CYAN}--------------------------------------------------------------------------------{TerminalColors.RESET}")
        print(f"  Toplam Calisma Suresi: {total_time:.2f} saniye")

        if all_passed:
            print(f"\n{TerminalColors.GREEN}{TerminalColors.BOLD}")
            print("  ****************************************************************************")
            print("  >>> BUTUN DOGRULAMALAR BASARIYLA TAMAMLANDI (ALL CHECKS PASSED) <<<")
            print("  ****************************************************************************")
            print(f"{TerminalColors.RESET}\n")
        else:
            print(f"\n{TerminalColors.RED}{TerminalColors.BOLD}")
            print("  [HATA] Bazi dogrulama adimlari basarisiz oldu. Lutfen loglari inceleyin.")
            print(f"{TerminalColors.RESET}\n")


def main() -> int:
    # Proje kök dizini (kurumsal-ag-guvenlik-mimarisi)
    script_path = Path(__file__).resolve()
    # tools/05-otomasyon-test-merkezi/run_all_checks.py -> 2 kademe üstü proje köküdür
    project_root = script_path.parent.parent.parent

    print_header()
    print(f"{TerminalColors.WHITE}Proje Kok Dizini: {project_root}{TerminalColors.RESET}\n")

    orchestrator = AutomationOrchestrator(base_dir=project_root)
    success = orchestrator.execute_suite()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

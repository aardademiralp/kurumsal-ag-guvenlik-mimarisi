#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kurumsal Ağ ve Siber Güvenlik Mimarisi - Bant Genişliği ve QoS Kapasite Hesaplayıcısı
(Enterprise Bandwidth Sizing & QoS Capacity Engineering Engine)

Bu script, üniversite kampüsü ve kurumsal holding için eşzamanlılık oranları,
kullanıcı başı hız limitleri, overbooking (aşırı tahsisat) çarpanları ve
kritik sistem rezervasyonlarını (VoIP DSCP EF, LMS AF21, buffer) hesaplayarak
gereken Metro Ethernet LACP hat kapasitesini ve donanım boyutlandırmasını raporlar.

Standart Kütüphaneler: argparse, sys, json, math, typing
Harici bağımlılık gerektirmez.
"""

import argparse
import json
import math
import sys
from typing import Any, Dict

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
    """Kapasite hesaplayıcı başlığını ekrana basar."""
    banner = f"""{TerminalColors.CYAN}{TerminalColors.BOLD}
================================================================================
   ENTERPRISE BANDWIDTH SIZING & QoS CAPACITY ENGINE (10K+ CAMPUS / HQ)
================================================================================{TerminalColors.RESET}"""
    print(banner)


class BandwidthCalculator:
    """Bant genişliği ve hat boyutlandırma matematiksel hesaplama sınıfı."""

    def __init__(
        self,
        students: int = 10000,
        student_concurrency: float = 0.40,
        student_mbps: float = 8.0,
        staff: int = 700,
        staff_concurrency: float = 0.90,
        staff_mbps: float = 15.0,
        overbooking: float = 4.0,
        voip_mbps: float = 500.0,
        lms_mbps: float = 1500.0,
        buffer_percent: float = 20.0,
    ) -> None:
        self.students = students
        self.student_concurrency = student_concurrency
        self.student_mbps = student_mbps
        self.staff = staff
        self.staff_concurrency = staff_concurrency
        self.staff_mbps = staff_mbps
        self.overbooking = overbooking
        self.voip_mbps = voip_mbps
        self.lms_mbps = lms_mbps
        self.buffer_percent = buffer_percent

    def calculate(self) -> Dict[str, Any]:
        """Tüm metrikleri matematiksel olarak hesaplar."""
        # 1. Öğrenci Trafiği Hesabı
        active_students = round(self.students * self.student_concurrency)
        raw_student_mbps = active_students * self.student_mbps
        student_egress_mbps = raw_student_mbps / self.overbooking

        # 2. Akademik ve İdari Personel Trafiği
        active_staff = round(self.staff * self.staff_concurrency)
        staff_egress_mbps = active_staff * self.staff_mbps

        # 3. Kritik Sistem Rezervasyonları
        reservations_mbps = self.voip_mbps + self.lms_mbps

        # 4. Alt Toplam ve Tampon Payı (Buffer)
        subtotal_mbps = student_egress_mbps + staff_egress_mbps + reservations_mbps
        buffer_mbps = subtotal_mbps * (self.buffer_percent / 100.0)
        total_required_mbps = subtotal_mbps + buffer_mbps
        total_required_gbps = total_required_mbps / 1000.0

        # 5. Hat ve Port Boyutlandırma
        # 10G Hat Sizing (10.000 Mbps port)
        active_10g_links = max(1, math.ceil(total_required_mbps / 10000.0))
        # N+1 Yedeklilik ile Toplam 10G Hat Sayısı
        total_10g_lacp_links = active_10g_links + 1

        # 1G Hat Karşılığı
        equivalent_1g_links = math.ceil(total_required_mbps / 1000.0)

        return {
            "inputs": {
                "total_students": self.students,
                "student_concurrency": self.student_concurrency,
                "student_rate_mbps": self.student_mbps,
                "total_staff": self.staff,
                "staff_concurrency": self.staff_concurrency,
                "staff_rate_mbps": self.staff_mbps,
                "overbooking_ratio": f"1:{int(self.overbooking)}",
                "voip_reserved_mbps": self.voip_mbps,
                "lms_reserved_mbps": self.lms_mbps,
                "buffer_percentage": self.buffer_percent,
            },
            "metrics": {
                "active_students": active_students,
                "raw_student_mbps": raw_student_mbps,
                "raw_student_gbps": round(raw_student_mbps / 1000.0, 2),
                "student_egress_mbps": round(student_egress_mbps, 2),
                "student_egress_gbps": round(student_egress_mbps / 1000.0, 2),
                "active_staff": active_staff,
                "staff_egress_mbps": round(staff_egress_mbps, 2),
                "staff_egress_gbps": round(staff_egress_mbps / 1000.0, 2),
                "voip_reservation_mbps": self.voip_mbps,
                "lms_reservation_mbps": self.lms_mbps,
                "total_reservations_mbps": round(reservations_mbps, 2),
                "subtotal_mbps": round(subtotal_mbps, 2),
                "buffer_mbps": round(buffer_mbps, 2),
                "total_required_mbps": round(total_required_mbps, 2),
                "total_required_gbps": round(total_required_gbps, 2),
            },
            "infrastructure": {
                "active_10g_links_needed": active_10g_links,
                "total_10g_lacp_links_n_plus_1": total_10g_lacp_links,
                "equivalent_1g_links": equivalent_1g_links,
                "recommended_carrier_plan": f"{total_10g_lacp_links}x 10G SFP+ LACP Metro Ethernet (Dual Carrier)",
            },
        }

    def print_formatted_report(self, results: Dict[str, Any]) -> None:
        """Kapasite ve QoS tablosunu terminale biçimlendirilmiş olarak basar."""
        m = results["metrics"]
        i = results["inputs"]
        infra = results["infrastructure"]

        print(f"\n{TerminalColors.BOLD}--- 1. GIRDI PARAMETRELERI VE TRAFIK PROFILI ---{TerminalColors.RESET}")
        print(f"  Toplam Kayitli Ogrenci        : {i['total_students']:,} kisi (Eszamanlilik: %{i['student_concurrency']*100:.0f})")
        print(f"  Ogrenci Basi Dinamik Limit    : {i['student_rate_mbps']} Mbps (Overbooking: {i['overbooking_ratio']})")
        print(f"  Toplam Akademik/Idari Personel: {i['total_staff']:,} kisi (Eszamanlilik: %{i['staff_concurrency']*100:.0f})")
        print(f"  Personel Basi Garanti Hiz     : {i['staff_rate_mbps']} Mbps (Overbooking yok, 1:1)")
        print(f"  Guvenlik ve Burst Tampon Payi : %{i['buffer_percentage']:.0f} ek kapasite")

        print(f"\n{TerminalColors.CYAN}{TerminalColors.BOLD}--------------------------------------------------------------------------------")
        print(f" METRIK TANIMI                       FORMUL / HESAP             DEGER (Mbps)     DEGER (Gbps)")
        print(f"--------------------------------------------------------------------------------{TerminalColors.RESET}")
        print(f" Pik Aktif Ogrenci Sayisi           N_aktif = 10.000 x 0.40    {m['active_students']:>7} kisi             -")
        print(f" Ham Tepe Ogrenci Trafigi           4.000 x 8 Mbps             {m['raw_student_mbps']:>10,.1f} Mbps     {m['raw_student_gbps']:>6.2f} Gbps")
        print(f" Overbooking Sonrasi Ogrenci Egress 32.000 / 4 (1:4)           {m['student_egress_mbps']:>10,.1f} Mbps     {m['student_egress_gbps']:>6.2f} Gbps")
        print(f" Pik Aktif Personel Sayisi          N_aktif = 700 x 0.90       {m['active_staff']:>7} kisi             -")
        print(f" Personel & Idari Sistem Trafigi    630 x 15 Mbps              {m['staff_egress_mbps']:>10,.1f} Mbps     {m['staff_egress_gbps']:>6.2f} Gbps")
        print(f" VoIP / Zoom Rezervasyonu (DSCP EF) Sabit Garanti              {m['voip_reservation_mbps']:>10,.1f} Mbps     {m['voip_reservation_mbps']/1000.0:>6.2f} Gbps")
        print(f" LMS / Canli Amfi (DSCP AF21)       Sabit Garanti              {m['lms_reservation_mbps']:>10,.1f} Mbps     {m['lms_reservation_mbps']/1000.0:>6.2f} Gbps")
        print(f"{TerminalColors.CYAN}--------------------------------------------------------------------------------{TerminalColors.RESET}")
        print(f" Alt Toplam Egress Gereksinimi      Ogrenci+Personel+QoS       {m['subtotal_mbps']:>10,.1f} Mbps     {m['subtotal_mbps']/1000.0:>6.2f} Gbps")
        print(f" Tepe Yuku Tamponu (+%20 Buffer)    Alt Toplam x 0.20          {m['buffer_mbps']:>10,.1f} Mbps     {m['buffer_mbps']/1000.0:>6.2f} Gbps")
        print(f"{TerminalColors.CYAN}================================================================================{TerminalColors.RESET}")
        print(f"{TerminalColors.BOLD}{TerminalColors.GREEN} TOPLAM GEREKEN BANT GENISLIGI     Net Egress + Buffer        {m['total_required_mbps']:>10,.1f} Mbps     {m['total_required_gbps']:>6.2f} Gbps{TerminalColors.RESET}")
        print(f"{TerminalColors.CYAN}================================================================================{TerminalColors.RESET}")

        print(f"\n{TerminalColors.BOLD}--- 2. TASIYICI VE DONANIM HAT BOYUTLANDIRMASI (CARRIER SIZING) ---{TerminalColors.RESET}")
        print(f"  * Aktif 10G SFP+ Hat Ihtiyaci : {TerminalColors.BOLD}{infra['active_10g_links_needed']} Adet 10G Port{TerminalColors.RESET} (Trafik yuku: {m['total_required_gbps']} Gbps)")
        print(f"  * N+1 Tam Yedekli LACP Paketi : {TerminalColors.GREEN}{TerminalColors.BOLD}{infra['total_10g_lacp_links_n_plus_1']} Adet 10G SFP+ Fiber Hat (LACP 802.3ad Bundle){TerminalColors.RESET}")
        print(f"  * 1G Metro Ethernet Esdegeri  : {infra['equivalent_1g_links']} Adet 1G baglanti (Darbagaz riski yuksek, 10G zorunlu)")
        print(f"  * Onerilen Tasiyici Mimarisi  : {TerminalColors.CYAN}{infra['recommended_carrier_plan']}{TerminalColors.RESET}")
        print(f"    - WAN-1: ULAKBIM 10G Ulusal Akademik Ag (Eduroam & LMS icin)")
        print(f"    - WAN-2: Turk Telekom 10G Kurumsal Metro Ethernet (Genel Internet icin)")
        print(f"    - WAN-3 / HA: Turkcell Superonline 10G Standby / LACP yedeklilik\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Kurumsal Kampüs ve Holding Bant Genişliği ve QoS Kapasite Motoru"
    )
    parser.add_argument(
        "--students",
        type=int,
        default=10000,
        help="Toplam kayıtlı öğrenci sayısı (varsayılan: 10000)",
    )
    parser.add_argument(
        "--concurrency",
        type=float,
        default=0.40,
        help="Öğrenci pik eşzamanlılık oranı (varsayılan: 0.40)",
    )
    parser.add_argument(
        "--student-mbps",
        type=float,
        default=8.0,
        help="Öğrenci başı dinamik hız limiti (Mbps) (varsayılan: 8.0)",
    )
    parser.add_argument(
        "--staff",
        type=int,
        default=700,
        help="Toplam akademik ve idari personel sayısı (varsayılan: 700)",
    )
    parser.add_argument(
        "--staff-concurrency",
        type=float,
        default=0.90,
        help="Personel eşzamanlılık oranı (varsayılan: 0.90)",
    )
    parser.add_argument(
        "--staff-mbps",
        type=float,
        default=15.0,
        help="Personel başı ayrılmış hız limiti (Mbps) (varsayılan: 15.0)",
    )
    parser.add_argument(
        "--overbooking",
        type=float,
        default=4.0,
        help="Öğrenci internet overbooking / aşırı tahsisat oranı (varsayılan: 4.0)",
    )
    parser.add_argument(
        "--voip-mbps",
        type=float,
        default=500.0,
        help="VoIP / Webex ses ve video garantili rezervasyon (Mbps) (varsayılan: 500.0)",
    )
    parser.add_argument(
        "--lms-mbps",
        type=float,
        default=1500.0,
        help="LMS Moodle / Canlı Amfi video rezervasyonu (Mbps) (varsayılan: 1500.0)",
    )
    parser.add_argument(
        "--buffer",
        type=float,
        default=20.0,
        help="Güvenlik ve tepe yükü tampon yüzdesi (varsayılan: 20.0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Çıktıyı JSON formatında basar",
    )

    args = parser.parse_args()

    calc = BandwidthCalculator(
        students=args.students,
        student_concurrency=args.concurrency,
        student_mbps=args.student_mbps,
        staff=args.staff,
        staff_concurrency=args.staff_concurrency,
        staff_mbps=args.staff_mbps,
        overbooking=args.overbooking,
        voip_mbps=args.voip_mbps,
        lms_mbps=args.lms_mbps,
        buffer_percent=args.buffer,
    )

    results = calc.calculate()

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_banner()
        calc.print_formatted_report(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())

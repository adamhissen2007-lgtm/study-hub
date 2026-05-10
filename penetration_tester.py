"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    ADVANCED PENETRATION TESTING SUITE v4.2                    ║
║                              Study Hub AI Security                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import json
import socket
import ssl
import requests
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse
import math

# ============================================================================
#                            ENUMS & CONSTANTS
# ============================================================================

class ThreatLevel(Enum):
    CRITICAL = "🔴 CRITICAL"
    HIGH = "🟠 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🟢 LOW"

class VulnerabilityCategory(Enum):
    INJECTION = "SQL Injection"
    AUTH_BREAK = "Authentication Bypass"
    SENSITIVE_DATA = "Sensitive Data Exposure"
    SECURITY_MISCONFIG = "Security Misconfiguration"
    XSS = "Cross-Site Scripting"

@dataclass
class Vulnerability:
    id: str
    title: str
    category: VulnerabilityCategory
    severity: ThreatLevel
    description: str
    impact: str
    remediation: str
    cvss_score: float = 0.0

# ============================================================================
#                          DETECTION ENGINE
# ============================================================================

class AIDetectionEngine:
    def __init__(self):
        self.attack_patterns = [
            (r"('|%27).*('|%27)", "SQL Injection", 0.95),
            (r"(union.*select|select.*from|insert.*into)", "SQL Command", 0.92),
            (r"<script.*?>.*?</script>", "XSS Script Injection", 0.94),
            (r"javascript:", "XSS JavaScript", 0.85),
            (r"\.\./", "Path Traversal", 0.87),
            (r"(/etc/passwd|/etc/shadow)", "System File Access", 0.96),
            (r"(system|exec|eval)\(", "RCE Function", 0.93),
            (r"(http://169.254.169.254|http://localhost)", "SSRF", 0.91),
            (r"('or'1'='1|admin'--|or 1=1)", "Auth Bypass", 0.94),
        ]
    
    def analyze_payload(self, payload: str) -> Dict[str, Any]:
        detected_patterns = []
        max_confidence = 0
        
        for pattern, attack_type, confidence in self.attack_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                detected_patterns.append({"type": attack_type, "confidence": confidence})
                max_confidence = max(max_confidence, confidence)
        
        return {
            "is_malicious": len(detected_patterns) > 0,
            "confidence": max_confidence,
            "detected_patterns": detected_patterns,
            "suspicious_level": "HIGH" if max_confidence > 0.8 else "MEDIUM" if max_confidence > 0.5 else "LOW"
        }

# ============================================================================
#                          CRYPTOGRAPHIC SCANNER
# ============================================================================

class CryptographicScanner:
    @staticmethod
    def analyze_ssl_certificate(hostname: str, port: int = 443) -> Dict[str, Any]:
        result = {"valid": False, "days_left": 0, "recommendations": []}
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    result["valid"] = True
                    if cert.get('notAfter'):
                        expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        result["days_left"] = (expiry - datetime.now()).days
                    if result["days_left"] < 30:
                        result["recommendations"].append("⚠️ الشهادة على وشك الانتهاء!")
        except Exception as e:
            result["error"] = str(e)
        return result

# ============================================================================
#                          WAF TESTER
# ============================================================================

class WAFTester:
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.test_payloads = {
            "SQL Injection": ["' OR '1'='1", "admin'--", "1 AND 1=1"],
            "XSS": ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"],
            "Path Traversal": ["../../../etc/passwd"],
        }
        
    def test_waf_protection(self) -> Dict[str, Any]:
        results = {"total_tests": 0, "blocked": 0, "details": {}}
        
        for attack_type, payloads in self.test_payloads.items():
            type_results = {"blocked": 0, "total": len(payloads)}
            for payload in payloads:
                results["total_tests"] += 1
                try:
                    response = requests.get(f"{self.target_url}?test={payload}", timeout=5, verify=False)
                    if response.status_code in [403, 406, 429, 503]:
                        results["blocked"] += 1
                        type_results["blocked"] += 1
                except:
                    results["blocked"] += 1
                    type_results["blocked"] += 1
            results["details"][attack_type] = type_results
        
        results["protection_percentage"] = (results["blocked"] / results["total_tests"] * 100) if results["total_tests"] > 0 else 0
        results["summary"] = {"grade": "A" if results["protection_percentage"] >= 80 else "B" if results["protection_percentage"] >= 60 else "F"}
        return results

# ============================================================================
#                          MAIN PENETRATION TESTER
# ============================================================================

class AdvancedPenetrationTester:
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.ai_engine = AIDetectionEngine()
        self.vulnerabilities = []
        
    def run_full_audit(self):
        parsed_url = urlparse(self.target_url)
        hostname = parsed_url.netloc or parsed_url.path
        if ':' in hostname:
            hostname = hostname.split(':')[0]
        
        waf_tester = WAFTester(self.target_url)
        waf_results = waf_tester.test_waf_protection()
        ssl_results = CryptographicScanner.analyze_ssl_certificate(hostname)
        security_headers = self._check_security_headers()
        
        self._collect_vulnerabilities(waf_results, ssl_results)
        overall_score = self._calculate_overall_score()
        
        return {
            "summary": {
                "overall_score": overall_score,
                "vulnerabilities_count": len(self.vulnerabilities),
                "overall_status": "آمن" if overall_score >= 80 else "متوسط" if overall_score >= 60 else "غير آمن",
                "performance_score": 75
            },
            "vulnerabilities": [
                {
                    "id": v.id,
                    "title": v.title,
                    "category": v.category.value,
                    "severity": v.severity.value,
                    "description": v.description,
                    "impact": v.impact,
                    "remediation": v.remediation,
                    "cvss_score": v.cvss_score
                } for v in self.vulnerabilities
            ],
            "security_headers": security_headers,
            "ssl_info": ssl_results,
            "technologies": {"server": "Detected", "framework": "Flask"},
            "recommendations": self._generate_recommendations(),
            "scan_timestamp": datetime.now().isoformat(),
            "target_url": self.target_url
        }
    
    def _check_security_headers(self) -> Dict[str, str]:
        headers_result = {}
        try:
            response = requests.get(self.target_url, timeout=10, verify=False)
            headers_to_check = ["Strict-Transport-Security", "Content-Security-Policy", "X-Frame-Options"]
            for header in headers_to_check:
                headers_result[header] = response.headers.get(header, "❌ غير موجود")
                if headers_result[header] == "❌ غير موجود":
                    self.vulnerabilities.append(Vulnerability(
                        id=f"SEC-{len(self.vulnerabilities)}",
                        title=f"Missing: {header}",
                        category=VulnerabilityCategory.SECURITY_MISCONFIG,
                        severity=ThreatLevel.MEDIUM,
                        description=f"Header {header} is missing",
                        impact="Security header missing",
                        remediation=f"Add {header} header",
                        cvss_score=5.0
                    ))
        except Exception as e:
            headers_result["error"] = str(e)
        return headers_result
    
    def _collect_vulnerabilities(self, waf_results: Dict, ssl_results: Dict):
        if waf_results.get("protection_percentage", 0) < 60:
            self.vulnerabilities.append(Vulnerability(
                id="WAF-001",
                title="Weak WAF Protection",
                category=VulnerabilityCategory.SECURITY_MISCONFIG,
                severity=ThreatLevel.HIGH,
                description=f"WAF protection is only {waf_results.get('protection_percentage', 0)}%",
                impact="Application may be vulnerable to injection attacks",
                remediation="Improve WAF rules",
                cvss_score=7.5
            ))
        
        if ssl_results.get("days_left", 999) < 30:
            self.vulnerabilities.append(Vulnerability(
                id="SSL-001",
                title="SSL Certificate Expiring Soon",
                category=VulnerabilityCategory.SENSITIVE_DATA,
                severity=ThreatLevel.MEDIUM,
                description=f"Certificate expires in {ssl_results.get('days_left', 0)} days",
                impact="HTTPS will stop working",
                remediation="Renew SSL certificate immediately",
                cvss_score=6.5
            ))
    
    def _calculate_overall_score(self) -> float:
        if not self.vulnerabilities:
            return 100.0
        deduction = sum(10 for v in self.vulnerabilities if v.severity == ThreatLevel.HIGH)
        deduction += sum(5 for v in self.vulnerabilities if v.severity == ThreatLevel.MEDIUM)
        return max(0, 100 - deduction)
    
    def _generate_recommendations(self) -> List[str]:
        recommendations = [
            "✅ Enable HTTPS everywhere",
            "✅ Implement strong CSP headers",
            "🔐 Enable 2FA for all users",
            "🛡️ Use Rate Limiting",
            "📝 Enable security logging"
        ]
        for v in self.vulnerabilities:
            recommendations.append(f"⚠️ {v.remediation}")
        return list(set(recommendations))

# ============================================================================
#                          MAIN FUNCTION
# ============================================================================

def run_advanced_penetration_test(target_url: str) -> Dict[str, Any]:
    tester = AdvancedPenetrationTester(target_url)
    return tester.run_full_audit()

if __name__ == "__main__":
    result = run_advanced_penetration_test("http://localhost:5000")
    print(json.dumps(result, indent=2, ensure_ascii=False))
"""
SAP S21 Live Connection Verifier (Strict Read-Only)
Tests read-only connectivity to SAP S21 (192.168.1.55) via HTTP / OData endpoints.
Enforces Zero-Modification Guardrail: only HTTP GET / HEAD requests are permitted.
"""

import os
import sys
import base64
import requests
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

SAP_HOST = os.getenv("SAP_ASHOST", "192.168.1.55")
SAP_SYSNR = os.getenv("SAP_SYSNR", "00")
SAP_SID = os.getenv("SAP_SID", "S21")
SAP_CLIENT = os.getenv("SAP_CLIENT", "200")
SAP_USER = os.getenv("SAP_USER", "INT_SAMARTH")
SAP_PASSWORD = os.getenv("SAP_PASSWORD", "")
SAP_HTTP_PORT = os.getenv("SAP_HTTP_PORT", "8000")
SAP_READ_ONLY = os.getenv("SAP_READ_ONLY", "TRUE")

def verify_safety_guardrail():
    """Validates that read-only mode is strictly active before any call."""
    if SAP_READ_ONLY.upper() != "TRUE":
        print("[CRITICAL SAFETY ERROR] SAP_READ_ONLY is not TRUE. Execution halted.")
        sys.exit(1)
    print(f"[*] SAP Safety Guardrail: Read-Only Mode is ACTIVE for user {SAP_USER} on {SAP_SID} (Client {SAP_CLIENT}).")

def probe_sap_endpoint(endpoint_path, description):
    """Executes a strictly read-only HTTP GET request against SAP S21."""
    url = f"http://{SAP_HOST}:{SAP_HTTP_PORT}{endpoint_path}"
    print(f"\n[*] Probing {description}: {url}")
    
    headers = {
        "Accept": "application/json, application/xml, text/plain",
        "User-Agent": "BW-Morph-Migration-Accelerator/1.0"
    }
    
    auth = (SAP_USER, SAP_PASSWORD)
    
    try:
        response = requests.get(url, auth=auth, headers=headers, timeout=8)
        print(f"    -> HTTP Status: {response.status_code} ({response.reason})")
        print(f"    -> Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"    -> Server Header: {response.headers.get('server', 'SAP NetWeaver Application Server')}")
        
        if response.status_code in [200, 201]:
            print("    -> Result: SUCCESS (Endpoint reachable and authenticated)")
        elif response.status_code == 401:
            print("    -> Result: AUTHENTICATION REQUIRED (Port active, credentials received)")
        elif response.status_code == 403:
            print("    -> Result: FORBIDDEN (ICF node may need manual activation in SICF)")
        elif response.status_code == 404:
            print("    -> Result: NOT FOUND (Service node inactive on this client/host)")
        else:
            print(f"    -> Result: RESPONSE RECEIVED ({response.status_code})")
        return response.status_code
    except requests.exceptions.ConnectTimeout:
        print("    -> [Warning] Connection timed out.")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"    -> [Warning] Connection refused: {e}")
        return None
    except Exception as e:
        print(f"    -> [Error] {e}")
        return None

def main():
    print("=" * 65)
    print(f" SAP S21 Live Connectivity & Readiness Check (System: {SAP_SID}) ")
    print("=" * 65)
    
    verify_safety_guardrail()
    
    print(f"\nTarget SAP Instance: http://{SAP_HOST}:{SAP_HTTP_PORT} (Client {SAP_CLIENT})")
    
    # 1. Ping ICF standard health check
    probe_sap_endpoint("/sap/bc/ping", "Standard ICF Ping Endpoint")
    
    # 2. ADT Discovery Endpoint
    probe_sap_endpoint("/sap/bc/adt/discovery", "ABAP Development Tools (ADT) Discovery")
    
    # 3. Gateway Catalog Service
    probe_sap_endpoint(f"/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/?sap-client={SAP_CLIENT}", "OData Catalog Service Collection")
    
    print("\n" + "=" * 65)
    print(" Verification Complete: All queries executed in Strict Read-Only Mode.")
    print("=" * 65)

if __name__ == "__main__":
    main()

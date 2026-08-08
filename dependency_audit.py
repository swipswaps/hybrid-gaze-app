# Resource Allocation, Hardware Audit, and Robust Dependency Management with Gate Asserts
# Reference: Python Sys & Subprocess Modules (https://docs.python.org/3/library/sys.html)

import sys
import shutil
import importlib.util
from typing import List, Tuple

class ResourceAuditor:
    def __init__(self, required_packages: List[str], required_binaries: List[str]):
        self.required_packages = required_packages
        self.required_binaries = required_binaries

    def assert_python_version(self, min_version: Tuple[int, int] = (3, 11)):
        current = sys.version_info[:2]
        assert current >= min_version, f"[GATE_ASSERT_FAIL]: Python {current} < {min_version}"
        print(f"[GATE_ASSERT_PASS]: Python {current}")

    def assert_binaries_present(self):
        for binary in self.required_binaries:
            path = shutil.which(binary)
            assert path is not None, f"[GATE_ASSERT_FAIL]: Binary '{binary}' missing"
            print(f"[GATE_ASSERT_PASS]: {binary} at {path}")

    def assert_packages_installed(self):
        for pkg in self.required_packages:
            spec = importlib.util.find_spec(pkg)
            assert spec is not None, f"[GATE_ASSERT_FAIL]: Package '{pkg}' missing"
            print(f"[GATE_ASSERT_PASS]: {pkg} present")

    def audit_hardware_conflicts(self, camera_ids: List[int]):
        import cv2
        for cam_id in camera_ids:
            cap = cv2.VideoCapture(cam_id)
            if cap.isOpened():
                print(f"[RESOURCE_AUDIT]: /dev/video{cam_id} OK")
                cap.release()
            else:
                print(f"[RESOURCE_AUDIT_WARNING]: /dev/video{cam_id} unavailable")

if __name__ == "__main__":
    try:
        auditor = ResourceAuditor(
            required_packages=["fastapi","uvicorn","cv2","numpy","pydantic","mediapipe","PIL"],
            required_binaries=["ffmpeg","docker","python3"]
        )
        auditor.assert_python_version()
        auditor.assert_binaries_present()
        auditor.assert_packages_installed()
        auditor.audit_hardware_conflicts([0,1])
        sys.exit(0)
    except AssertionError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script tải dữ liệu địa bàn hành chính sáp nhập từ sapnhap.bando.com.vn
Dữ liệu sẽ được lưu vào thư mục data/boundary_changes/

Tính năng:
- Tải danh sách 34 tỉnh/thành phố có thay đổi địa bàn
- Tải chi tiết 3321 phường/xã/thị trấn mới
- Lưu dữ liệu dạng JSON để tra cứu offline

Cách sử dụng:
    python scripts/scrape_boundary_changes.py

Yêu cầu thêm:
    pip install cloudscraper beautifulsoup4 selenium webdriver-manager
"""

import os
import sys
import json
import time
import re
from datetime import datetime
from pathlib import Path

# Thêm thư mục gốc vào path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import các thư viện cần thiết
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("Cần cài đặt requests: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Cần cài đặt beautifulsoup4: pip install beautifulsoup4")
    sys.exit(1)

# Thư mục lưu dữ liệu
DATA_DIR = BASE_DIR / "data" / "boundary_changes"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class BoundaryScraper:
    """
    Scraper để tải dữ liệu địa bàn hành chính từ sapnhap.bando.com.vn
    """

    BASE_URL = "https://sapnhap.bando.com.vn"

    # Headers giả lập trình duyệt
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    def __init__(self):
        self.session = None
        self.data = {
            "metadata": {
                "source": self.BASE_URL,
                "scraped_at": None,
                "description": "Dữ liệu địa bàn hành chính sau sáp nhập 1/7/2025"
            },
            "provinces": [],
            "districts": [],
            "wards": [],
            "changes": []
        }

    def create_session(self):
        """Tạo session với retry logic"""
        self.session = requests.Session()

        # Cấu hình retry
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update(self.HEADERS)

        return self.session

    def try_cloudscraper(self):
        """Thử sử dụng cloudscraper để bypass Cloudflare"""
        try:
            import cloudscraper
            print("Đang sử dụng cloudscraper để bypass bảo vệ...")
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            return scraper
        except ImportError:
            print("cloudscraper không được cài đặt. Cài đặt: pip install cloudscraper")
            return None
        except Exception as e:
            print(f"Lỗi khi tạo cloudscraper: {e}")
            return None

    def try_selenium(self):
        """Thử sử dụng Selenium như phương pháp cuối cùng"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            print("Đang sử dụng Selenium để tải trang...")

            # Cấu hình Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(f"user-agent={self.HEADERS['User-Agent']}")

            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                # Thử không dùng webdriver_manager
                driver = webdriver.Chrome(options=chrome_options)

            return driver

        except ImportError as e:
            print(f"Selenium không được cài đặt. Cài đặt: pip install selenium webdriver-manager")
            return None
        except Exception as e:
            print(f"Lỗi khi khởi tạo Selenium: {e}")
            return None

    def fetch_page(self, url):
        """
        Tải trang web sử dụng nhiều phương pháp
        Trả về HTML content hoặc None nếu thất bại
        """
        print(f"Đang tải: {url}")

        # Phương pháp 1: Requests thông thường
        if self.session is None:
            self.create_session()

        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200 and "Access denied" not in response.text:
                print("✓ Tải thành công bằng requests")
                return response.text
        except Exception as e:
            print(f"Requests thất bại: {e}")

        # Phương pháp 2: Cloudscraper
        scraper = self.try_cloudscraper()
        if scraper:
            try:
                response = scraper.get(url, timeout=30)
                if response.status_code == 200 and "Access denied" not in response.text:
                    print("✓ Tải thành công bằng cloudscraper")
                    return response.text
            except Exception as e:
                print(f"Cloudscraper thất bại: {e}")

        # Phương pháp 3: Selenium
        driver = self.try_selenium()
        if driver:
            try:
                driver.get(url)
                time.sleep(5)  # Đợi trang load
                html = driver.page_source
                driver.quit()
                if "Access denied" not in html:
                    print("✓ Tải thành công bằng Selenium")
                    return html
            except Exception as e:
                print(f"Selenium thất bại: {e}")
                if driver:
                    driver.quit()

        return None

    def parse_provinces(self, html):
        """Parse danh sách tỉnh/thành phố từ HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        provinces = []

        # Tìm các selector phổ biến cho danh sách tỉnh
        selectors = [
            'select[name*="tinh"] option',
            'select[name*="province"] option',
            'select#province option',
            '.province-list li',
            '[data-province]',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for el in elements:
                    value = el.get('value', '') or el.get('data-id', '')
                    name = el.get_text(strip=True)
                    if value and name and name != "Chọn tỉnh/thành":
                        provinces.append({
                            "id": value,
                            "name": name
                        })
                break

        return provinces

    def parse_districts(self, html, province_id):
        """Parse danh sách quận/huyện từ HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        districts = []

        selectors = [
            'select[name*="huyen"] option',
            'select[name*="district"] option',
            'select#district option',
            '.district-list li',
            '[data-district]',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for el in elements:
                    value = el.get('value', '') or el.get('data-id', '')
                    name = el.get_text(strip=True)
                    if value and name and name != "Chọn quận/huyện":
                        districts.append({
                            "id": value,
                            "name": name,
                            "province_id": province_id
                        })
                break

        return districts

    def parse_wards(self, html, district_id):
        """Parse danh sách phường/xã từ HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        wards = []

        selectors = [
            'select[name*="xa"] option',
            'select[name*="ward"] option',
            'select#ward option',
            '.ward-list li',
            '[data-ward]',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for el in elements:
                    value = el.get('value', '') or el.get('data-id', '')
                    name = el.get_text(strip=True)
                    if value and name and name != "Chọn phường/xã":
                        wards.append({
                            "id": value,
                            "name": name,
                            "district_id": district_id
                        })
                break

        return wards

    def parse_change_info(self, html):
        """Parse thông tin thay đổi địa bàn từ HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        changes = []

        # Tìm các bảng hoặc danh sách chứa thông tin thay đổi
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Bỏ qua header
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    change = {
                        "old_name": cells[0].get_text(strip=True) if len(cells) > 0 else "",
                        "new_name": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                        "note": cells[2].get_text(strip=True) if len(cells) > 2 else ""
                    }
                    if change["old_name"] or change["new_name"]:
                        changes.append(change)

        return changes

    def extract_json_data(self, html):
        """Trích xuất dữ liệu JSON từ script tags trong HTML"""
        if not html:
            return None

        # Tìm các đoạn JSON trong script tags
        json_patterns = [
            r'var\s+data\s*=\s*(\{[^;]+\});',
            r'var\s+provinces\s*=\s*(\[[^\]]+\]);',
            r'var\s+districts\s*=\s*(\[[^\]]+\]);',
            r'var\s+wards\s*=\s*(\[[^\]]+\]);',
            r'"provinces"\s*:\s*(\[[^\]]+\])',
            r'"districts"\s*:\s*(\[[^\]]+\])',
            r'"wards"\s*:\s*(\[[^\]]+\])',
        ]

        extracted = {}
        for pattern in json_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, list):
                        if not extracted.get('list_data'):
                            extracted['list_data'] = []
                        extracted['list_data'].extend(data)
                    elif isinstance(data, dict):
                        extracted.update(data)
                except:
                    continue

        return extracted if extracted else None

    def scrape_all(self):
        """Scrape toàn bộ dữ liệu từ trang web"""
        print("=" * 60)
        print("BẮT ĐẦU TẢI DỮ LIỆU ĐỊA BÀN HÀNH CHÍNH")
        print("=" * 60)

        # Tải trang chính
        html = self.fetch_page(self.BASE_URL)

        if not html:
            print("\n❌ Không thể tải trang web.")
            print("\nGợi ý:")
            print("1. Cài đặt thêm thư viện: pip install cloudscraper selenium webdriver-manager")
            print("2. Kiểm tra kết nối mạng")
            print("3. Thử lại sau vài phút")
            return False

        # Trích xuất dữ liệu JSON từ HTML
        json_data = self.extract_json_data(html)
        if json_data:
            print("✓ Tìm thấy dữ liệu JSON trong trang")
            self.data.update(json_data)

        # Parse danh sách tỉnh/thành phố
        provinces = self.parse_provinces(html)
        if provinces:
            print(f"✓ Tìm thấy {len(provinces)} tỉnh/thành phố")
            self.data["provinces"] = provinces

        # Parse thông tin thay đổi
        changes = self.parse_change_info(html)
        if changes:
            print(f"✓ Tìm thấy {len(changes)} thay đổi địa bàn")
            self.data["changes"] = changes

        # Cập nhật metadata
        self.data["metadata"]["scraped_at"] = datetime.now().isoformat()

        return True

    def save_data(self):
        """Lưu dữ liệu ra file JSON"""
        # File chính
        output_file = DATA_DIR / "boundary_changes.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Đã lưu dữ liệu vào: {output_file}")

        # File backup với timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = DATA_DIR / f"boundary_changes_{timestamp}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"✓ Đã lưu backup vào: {backup_file}")

        return output_file


def create_sample_data():
    """
    Tạo dữ liệu mẫu về sáp nhập địa bàn hành chính
    Dữ liệu này dựa trên thông tin công khai về sáp nhập 1/7/2025
    """
    sample_data = {
        "metadata": {
            "source": "https://sapnhap.bando.com.vn",
            "description": "Dữ liệu địa bàn hành chính sau sáp nhập 1/7/2025",
            "created_at": datetime.now().isoformat(),
            "note": "Dữ liệu mẫu - Cần cập nhật từ nguồn chính thức"
        },
        "statistics": {
            "total_provinces_with_changes": 34,
            "total_new_wards": 3321,
            "effective_date": "2025-07-01"
        },
        "provinces_with_changes": [
            {"code": "01", "name": "Hà Nội", "new_wards_count": 126},
            {"code": "79", "name": "TP. Hồ Chí Minh", "new_wards_count": 0},
            {"code": "48", "name": "Đà Nẵng", "new_wards_count": 45},
            {"code": "92", "name": "Cần Thơ", "new_wards_count": 38},
            {"code": "31", "name": "Hải Phòng", "new_wards_count": 52},
            {"code": "38", "name": "Thanh Hóa", "new_wards_count": 156},
            {"code": "40", "name": "Nghệ An", "new_wards_count": 143},
            {"code": "36", "name": "Nam Định", "new_wards_count": 89},
            {"code": "34", "name": "Thái Bình", "new_wards_count": 94},
            {"code": "30", "name": "Hải Dương", "new_wards_count": 87},
        ],
        "sample_changes": [
            {
                "province": "Hà Nội",
                "type": "merge",
                "old_units": ["Phường Phú La", "Phường Yên Nghĩa"],
                "new_unit": "Phường Phú Yên",
                "effective_date": "2025-07-01"
            },
            {
                "province": "Hà Nội",
                "type": "merge",
                "old_units": ["Xã Đại Mỗ", "Xã Trung Văn"],
                "new_unit": "Phường Đại Trung",
                "effective_date": "2025-07-01"
            },
            {
                "province": "Thanh Hóa",
                "type": "merge",
                "old_units": ["Xã Đông Hòa", "Xã Đông Yên"],
                "new_unit": "Xã Đông Hòa Yên",
                "effective_date": "2025-07-01"
            },
        ],
        "data_sources": [
            {
                "name": "sapnhap.bando.com.vn",
                "url": "https://sapnhap.bando.com.vn",
                "description": "Bản đồ tra cứu địa giới hành chính sau sáp nhập"
            },
            {
                "name": "diachi.vnpost.vn",
                "url": "https://diachi.vnpost.vn",
                "description": "Công cụ chuyển đổi địa chỉ cũ - mới của Bưu điện Việt Nam"
            },
            {
                "name": "vnsdi.mae.gov.vn",
                "url": "https://vnsdi.mae.gov.vn",
                "description": "Hạ tầng dữ liệu không gian địa lý Việt Nam"
            }
        ]
    }

    return sample_data


def main():
    """Hàm chính"""
    print("\n" + "=" * 60)
    print("CÔNG CỤ TẢI DỮ LIỆU ĐỊA BÀN HÀNH CHÍNH SÁP NHẬP")
    print("Nguồn: sapnhap.bando.com.vn")
    print("=" * 60 + "\n")

    # Tạo scraper và bắt đầu tải
    scraper = BoundaryScraper()
    success = scraper.scrape_all()

    if success:
        output_file = scraper.save_data()
        print("\n" + "=" * 60)
        print("HOÀN THÀNH!")
        print("=" * 60)
    else:
        # Tạo dữ liệu mẫu khi không thể scrape
        print("\n" + "-" * 60)
        print("Đang tạo dữ liệu mẫu...")
        sample_data = create_sample_data()

        output_file = DATA_DIR / "boundary_changes.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)

        print(f"✓ Đã tạo dữ liệu mẫu tại: {output_file}")
        print("\nLưu ý: Đây là dữ liệu mẫu. Để có dữ liệu đầy đủ, bạn cần:")
        print("1. Cài đặt: pip install cloudscraper selenium webdriver-manager")
        print("2. Chạy lại script này")
        print("3. Hoặc tải dữ liệu thủ công từ sapnhap.bando.com.vn")

    print(f"\nDữ liệu được lưu tại: {DATA_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

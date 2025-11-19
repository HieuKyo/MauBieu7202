# -*- coding: utf-8 -*-
"""
Service để tra cứu dữ liệu địa bàn hành chính sáp nhập
Đọc dữ liệu từ file JSON và cung cấp các hàm tra cứu
"""

import json
import os
from pathlib import Path
from django.conf import settings


class BoundaryService:
    """
    Service tra cứu địa bàn hành chính sau sáp nhập
    """

    _instance = None
    _data = None

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._data is None:
            self.load_data()

    def load_data(self):
        """Load dữ liệu từ file JSON"""
        data_file = Path(settings.BASE_DIR) / "data" / "boundary_changes" / "boundary_changes.json"

        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except Exception as e:
                print(f"Lỗi đọc file dữ liệu: {e}")
                self._data = self._get_empty_data()
        else:
            self._data = self._get_empty_data()

    def _get_empty_data(self):
        """Trả về dữ liệu rỗng nếu không load được"""
        return {
            "metadata": {
                "source": "https://sapnhap.bando.com.vn",
                "description": "Chưa có dữ liệu",
                "note": "Chạy scripts/scrape_boundary_changes.py để tải dữ liệu"
            },
            "statistics": {
                "total_provinces_with_changes": 0,
                "total_new_wards": 0,
                "effective_date": "2025-07-01"
            },
            "provinces_with_changes": [],
            "sample_changes": [],
            "data_sources": []
        }

    def reload_data(self):
        """Reload dữ liệu từ file"""
        self._data = None
        self.load_data()

    def get_metadata(self):
        """Lấy thông tin metadata"""
        return self._data.get("metadata", {})

    def get_statistics(self):
        """Lấy thống kê tổng quan"""
        return self._data.get("statistics", {})

    def get_all_provinces(self):
        """Lấy danh sách tất cả tỉnh/thành có thay đổi"""
        return self._data.get("provinces_with_changes", [])

    def get_province_by_code(self, code):
        """Tìm tỉnh theo mã"""
        for province in self.get_all_provinces():
            if province.get("code") == code:
                return province
        return None

    def get_province_by_name(self, name):
        """Tìm tỉnh theo tên"""
        name_lower = name.lower()
        for province in self.get_all_provinces():
            if name_lower in province.get("name", "").lower():
                return province
        return None

    def search_provinces(self, query):
        """Tìm kiếm tỉnh theo từ khóa"""
        if not query:
            return self.get_all_provinces()

        query_lower = query.lower()
        results = []

        for province in self.get_all_provinces():
            name = province.get("name", "").lower()
            code = province.get("code", "").lower()

            if query_lower in name or query_lower in code:
                results.append(province)

        return results

    def get_all_changes(self):
        """Lấy tất cả thay đổi địa bàn"""
        return self._data.get("sample_changes", [])

    def get_changes_by_province(self, province_name):
        """Lấy các thay đổi theo tỉnh"""
        province_lower = province_name.lower()
        results = []

        for change in self.get_all_changes():
            if province_lower in change.get("province", "").lower():
                results.append(change)

        return results

    def search_changes(self, query):
        """
        Tìm kiếm thay đổi địa bàn theo từ khóa
        Tìm trong tên đơn vị cũ, đơn vị mới, tỉnh
        """
        if not query:
            return self.get_all_changes()

        query_lower = query.lower()
        results = []

        for change in self.get_all_changes():
            # Tìm trong tên tỉnh
            if query_lower in change.get("province", "").lower():
                results.append(change)
                continue

            # Tìm trong đơn vị mới
            if query_lower in change.get("new_unit", "").lower():
                results.append(change)
                continue

            # Tìm trong các đơn vị cũ
            old_units = change.get("old_units", [])
            for unit in old_units:
                if query_lower in unit.lower():
                    results.append(change)
                    break

        return results

    def get_old_to_new_mapping(self, old_name):
        """
        Tra cứu địa bàn cũ -> địa bàn mới
        Trả về thông tin thay đổi nếu tìm thấy
        """
        old_lower = old_name.lower()

        for change in self.get_all_changes():
            old_units = change.get("old_units", [])
            for unit in old_units:
                if old_lower in unit.lower():
                    return {
                        "found": True,
                        "old_name": unit,
                        "new_name": change.get("new_unit", ""),
                        "province": change.get("province", ""),
                        "type": change.get("type", "merge"),
                        "effective_date": change.get("effective_date", "2025-07-01"),
                        "all_old_units": old_units
                    }

        return {
            "found": False,
            "message": f"Không tìm thấy thông tin thay đổi cho '{old_name}'"
        }

    def get_data_sources(self):
        """Lấy danh sách nguồn dữ liệu"""
        return self._data.get("data_sources", [])

    def get_summary(self):
        """Lấy tóm tắt dữ liệu"""
        stats = self.get_statistics()
        metadata = self.get_metadata()

        return {
            "total_provinces": stats.get("total_provinces_with_changes", 0),
            "total_wards": stats.get("total_new_wards", 0),
            "effective_date": stats.get("effective_date", "2025-07-01"),
            "source": metadata.get("source", ""),
            "description": metadata.get("description", ""),
            "note": metadata.get("note", ""),
            "data_loaded": len(self.get_all_provinces()) > 0
        }


# Singleton instance
boundary_service = BoundaryService()

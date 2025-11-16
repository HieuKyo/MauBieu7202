/**
 * Address Selector Component - Standalone
 *
 * Tích hợp hệ thống chọn địa chỉ cascade (Tỉnh → Huyện → Xã → Khóm)
 * cho dự án MauBieu7202 (Django)
 *
 * USAGE:
 * ------
 * 1. Include file này trong template Django
 * 2. Tạo container element: <div id="address-container"></div>
 * 3. Khởi tạo: new AddressSelector('#address-container', options)
 *
 * EXAMPLE:
 * --------
 * const selector = new AddressSelector('#address-container', {
 *     dataUrl: '/static/data/dia_danh.json',  // Đường dẫn đến file JSON
 *     showKhom: true,                          // Hiển thị cấp Khóm/Ấp
 *     autoFill: function(fullAddress, data) {
 *         // Tự động điền vào các input field
 *         document.querySelector('[name="address"]').value = fullAddress;
 *     }
 * });
 *
 * @author Converted from ChuyenDoiHanhChinh_Web
 * @version 1.0
 */

class AddressSelector {
    /**
     * Constructor
     * @param {string} containerId - CSS selector của container element
     * @param {object} options - Cấu hình
     */
    constructor(containerId, options = {}) {
        this.container = document.querySelector(containerId);

        if (!this.container) {
            console.error(`Container "${containerId}" not found`);
            return;
        }

        // Merge default options với user options
        this.options = {
            dataUrl: options.dataUrl || '/static/data/dia_danh.json',
            apiBaseUrl: options.apiBaseUrl || null, // Nếu muốn dùng API thay vì JSON
            onSelect: options.onSelect || null,
            onLoad: options.onLoad || null,
            autoFill: options.autoFill || null,
            showKhom: options.showKhom !== false,
            labels: {
                tinh: options.labels?.tinh || 'Tỉnh/Thành phố',
                huyen: options.labels?.huyen || 'Quận/Huyện',
                xa: options.labels?.xa || 'Phường/Xã',
                khom: options.labels?.khom || 'Ấp/Khóm'
            },
            placeholders: {
                tinh: '-- Chọn Tỉnh/Thành phố --',
                huyen: '-- Chọn Quận/Huyện --',
                xa: '-- Chọn Phường/Xã --',
                khom: '-- Chọn Ấp/Khóm --'
            },
            theme: options.theme || 'bootstrap', // 'bootstrap' hoặc 'custom'
            ...options
        };

        // State của component
        this.data = {
            tinh: '',
            huyen: '',
            xa: '',
            khom: ''
        };

        // Hierarchy data
        this.hierarchyData = null;

        // Initialize
        this.init();
    }

    /**
     * Initialize component
     */
    async init() {
        try {
            // Show loading
            this.showLoading();

            // Load data
            await this.loadHierarchyData();

            // Render UI
            this.render();

            // Bind events
            this.bindEvents();

            // Hide loading
            this.hideLoading();

            // Trigger onLoad callback
            if (this.options.onLoad) {
                this.options.onLoad(this);
            }
        } catch (error) {
            console.error('Error initializing AddressSelector:', error);
            this.showError('Không thể tải dữ liệu địa danh. Vui lòng thử lại.');
        }
    }

    /**
     * Load hierarchy data from JSON file
     */
    async loadHierarchyData() {
        try {
            const response = await fetch(this.options.dataUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.hierarchyData = await response.json();
        } catch (error) {
            console.error('Error loading hierarchy data:', error);
            throw error;
        }
    }

    /**
     * Render component UI
     */
    render() {
        const { labels, placeholders, showKhom } = this.options;

        this.container.innerHTML = `
            <div class="address-selector" data-theme="${this.options.theme}">
                <div class="address-row mb-3">
                    <label class="form-label">${labels.tinh}</label>
                    <select class="form-select" data-level="tinh">
                        <option value="">${placeholders.tinh}</option>
                        ${this.getTinhOptions()}
                    </select>
                </div>

                <div class="address-row mb-3">
                    <label class="form-label">${labels.huyen}</label>
                    <select class="form-select" data-level="huyen" disabled>
                        <option value="">${placeholders.huyen}</option>
                    </select>
                </div>

                <div class="address-row mb-3">
                    <label class="form-label">${labels.xa}</label>
                    <select class="form-select" data-level="xa" disabled>
                        <option value="">${placeholders.xa}</option>
                    </select>
                </div>

                ${showKhom ? `
                <div class="address-row mb-3">
                    <label class="form-label">${labels.khom}</label>
                    <select class="form-select" data-level="khom" disabled>
                        <option value="">${placeholders.khom}</option>
                    </select>
                </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Get Tinh options HTML
     */
    getTinhOptions() {
        if (!this.hierarchyData) return '';

        return Object.keys(this.hierarchyData)
            .map(tinh => `<option value="${this.escapeHtml(tinh)}">${this.escapeHtml(tinh)}</option>`)
            .join('');
    }

    /**
     * Bind events to select elements
     */
    bindEvents() {
        const selects = this.container.querySelectorAll('select');

        selects.forEach(select => {
            select.addEventListener('change', (e) => {
                const level = e.target.dataset.level;
                const value = e.target.value;
                this.handleChange(level, value);
            });
        });
    }

    /**
     * Handle select change event
     */
    handleChange(level, value) {
        this.data[level] = value;

        switch(level) {
            case 'tinh':
                this.populateHuyen(value);
                this.resetSelect('xa');
                this.resetSelect('khom');
                break;
            case 'huyen':
                this.populateXa(this.data.tinh, value);
                this.resetSelect('khom');
                break;
            case 'xa':
                if (this.options.showKhom) {
                    this.populateKhom(this.data.tinh, this.data.huyen, value);
                }
                break;
        }

        // Trigger callbacks
        this.triggerCallbacks();
    }

    /**
     * Populate Huyen select
     */
    populateHuyen(tinh) {
        const select = this.container.querySelector('[data-level="huyen"]');

        if (!tinh || !this.hierarchyData[tinh]) {
            this.disableSelect(select);
            return;
        }

        const huyens = Object.keys(this.hierarchyData[tinh]);
        this.populateSelect(select, huyens, this.options.placeholders.huyen);
    }

    /**
     * Populate Xa select
     */
    populateXa(tinh, huyen) {
        const select = this.container.querySelector('[data-level="xa"]');

        if (!tinh || !huyen || !this.hierarchyData[tinh]?.[huyen]) {
            this.disableSelect(select);
            return;
        }

        const xas = Object.keys(this.hierarchyData[tinh][huyen]);
        this.populateSelect(select, xas, this.options.placeholders.xa);
    }

    /**
     * Populate Khom select
     */
    populateKhom(tinh, huyen, xa) {
        if (!this.options.showKhom) return;

        const select = this.container.querySelector('[data-level="khom"]');

        if (!tinh || !huyen || !xa || !this.hierarchyData[tinh]?.[huyen]?.[xa]) {
            this.disableSelect(select);
            return;
        }

        const khoms = this.hierarchyData[tinh][huyen][xa];
        this.populateSelect(select, khoms, this.options.placeholders.khom);
    }

    /**
     * Populate select element with options
     */
    populateSelect(selectElement, items, placeholder) {
        const options = items
            .map(item => `<option value="${this.escapeHtml(item)}">${this.escapeHtml(item)}</option>`)
            .join('');

        selectElement.innerHTML = `<option value="">${placeholder}</option>${options}`;
        selectElement.disabled = false;
    }

    /**
     * Disable and reset select element
     */
    disableSelect(selectElement) {
        if (selectElement) {
            selectElement.innerHTML = `<option value="">${selectElement.querySelector('option').textContent}</option>`;
            selectElement.disabled = true;
        }
    }

    /**
     * Reset select element
     */
    resetSelect(level) {
        const select = this.container.querySelector(`[data-level="${level}"]`);
        if (select) {
            const placeholder = this.options.placeholders[level];
            select.innerHTML = `<option value="">${placeholder}</option>`;
            select.disabled = true;
            this.data[level] = '';
        }
    }

    /**
     * Get full address string
     */
    getFullAddress() {
        const { tinh, huyen, xa, khom } = this.data;
        let address = '';

        if (khom) {
            const prefix = xa.startsWith('Phường') ? 'Khóm' : 'Ấp';
            address = `${prefix} ${khom}, `;
        }
        if (xa) address += `${xa}, `;
        if (huyen) address += `${huyen}, `;
        if (tinh) address += tinh;

        return address.trim();
    }

    /**
     * Get address parts separately
     */
    getAddressParts() {
        const { tinh, huyen, xa, khom } = this.data;
        const prefix = xa && xa.startsWith('Phường') ? 'Khóm' : 'Ấp';

        return {
            province: tinh,
            district: huyen,
            ward: xa,
            hamlet: khom,
            hamletWithPrefix: khom ? `${prefix} ${khom}` : ''
        };
    }

    /**
     * Trigger callbacks
     */
    triggerCallbacks() {
        const fullAddress = this.getFullAddress();
        const parts = this.getAddressParts();

        // onSelect callback
        if (this.options.onSelect) {
            this.options.onSelect(fullAddress, parts, this.data);
        }

        // autoFill callback
        if (this.options.autoFill) {
            this.options.autoFill(fullAddress, parts);
        }
    }

    /**
     * Get current value
     */
    getValue() {
        return {
            raw: { ...this.data },
            parts: this.getAddressParts(),
            fullAddress: this.getFullAddress()
        };
    }

    /**
     * Set value programmatically
     */
    async setValue(data) {
        if (data.tinh) {
            const tinhSelect = this.container.querySelector('[data-level="tinh"]');
            tinhSelect.value = data.tinh;
            this.data.tinh = data.tinh;
            this.populateHuyen(data.tinh);

            await this.waitForNextTick();
        }

        if (data.huyen) {
            const huyenSelect = this.container.querySelector('[data-level="huyen"]');
            huyenSelect.value = data.huyen;
            this.data.huyen = data.huyen;
            this.populateXa(this.data.tinh, data.huyen);

            await this.waitForNextTick();
        }

        if (data.xa) {
            const xaSelect = this.container.querySelector('[data-level="xa"]');
            xaSelect.value = data.xa;
            this.data.xa = data.xa;

            if (this.options.showKhom) {
                this.populateKhom(this.data.tinh, this.data.huyen, data.xa);
                await this.waitForNextTick();
            }
        }

        if (data.khom && this.options.showKhom) {
            const khomSelect = this.container.querySelector('[data-level="khom"]');
            khomSelect.value = data.khom;
            this.data.khom = data.khom;
        }

        this.triggerCallbacks();
    }

    /**
     * Reset all selections
     */
    reset() {
        const tinhSelect = this.container.querySelector('[data-level="tinh"]');
        tinhSelect.value = '';
        this.data.tinh = '';

        this.resetSelect('huyen');
        this.resetSelect('xa');
        this.resetSelect('khom');

        this.triggerCallbacks();
    }

    /**
     * Validate if address is complete
     */
    isValid() {
        const { tinh, huyen, xa } = this.data;
        return !!(tinh && huyen && xa);
    }

    /**
     * Show loading state
     */
    showLoading() {
        this.container.innerHTML = '<div class="text-center p-3"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Đang tải...</span></div></div>';
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        // Loading is replaced by render()
    }

    /**
     * Show error message
     */
    showError(message) {
        this.container.innerHTML = `<div class="alert alert-danger" role="alert">${this.escapeHtml(message)}</div>`;
    }

    /**
     * Wait for next tick (for async operations)
     */
    waitForNextTick() {
        return new Promise(resolve => setTimeout(resolve, 0));
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Destroy component
     */
    destroy() {
        this.container.innerHTML = '';
        this.hierarchyData = null;
        this.data = null;
    }
}

// Export for use in modules or global scope
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AddressSelector;
} else {
    window.AddressSelector = AddressSelector;
}

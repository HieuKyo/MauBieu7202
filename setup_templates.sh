#!/bin/bash
# Script tự động setup template storage
# Giải quyết vấn đề template hết hạn sau 1 tuần

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/home/user/MauBieu7202"
OFFLINE_DIR="/home/user/maubieumoi"
MEDIA_DIR="$PROJECT_DIR/media/templates/docx"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}║   Template Storage Setup - Giải quyết vấn đề hết hạn      ║${NC}"
echo -e "${BLUE}║                                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function: Print step
print_step() {
    echo -e "\n${BLUE}▶ $1${NC}"
}

# Function: Print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function: Print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function: Print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. Some operations may have permission issues."
fi

# Menu
echo "Chọn giải pháp setup:"
echo ""
echo "1️⃣  Setup Hệ Thống Chuẩn (Lưu vào media folder)"
echo "   → Ổn định nhất, không phụ thuộc folder bên ngoài"
echo "   → Template không bao giờ hết hạn"
echo ""
echo "2️⃣  Link tới Folder Offline (maubieumoi)"
echo "   → Dùng chung templates với hệ thống khác"
echo "   → Cập nhật dễ dàng (chỉ cần thay file)"
echo ""
echo "3️⃣  Hybrid - Fallback Mechanism (Khuyên dùng!)"
echo "   → Kết hợp ưu điểm của cả 2"
echo "   → Auto-cache, có fallback"
echo ""
echo "4️⃣  Validate Templates (Kiểm tra file corrupt)"
echo "   → Scan và tìm templates bị lỗi"
echo ""
echo "0️⃣  Exit"
echo ""

read -p "Lựa chọn của bạn [1-4]: " choice

case $choice in
    1)
        # ========================================
        # GIẢI PHÁP 1: Setup Hệ Thống Chuẩn
        # ========================================
        print_step "GIẢI PHÁP 1: Setup Hệ Thống Chuẩn"

        # Create media directory
        print_step "Creating media directory..."
        mkdir -p "$MEDIA_DIR"
        print_success "Created: $MEDIA_DIR"

        # Set permissions
        print_step "Setting permissions..."
        chmod -R 755 "$PROJECT_DIR/media"
        print_success "Permissions set"

        # Migrate database
        print_step "Migrating database..."
        cd "$PROJECT_DIR"

        if python manage.py migrate; then
            print_success "Database migrated successfully"
        else
            print_error "Migration failed. Make sure Django environment is setup."
            exit 1
        fi

        # Check if templates exist to copy
        if [ -d "$OFFLINE_DIR" ] && [ "$(ls -A $OFFLINE_DIR/*.docx 2>/dev/null)" ]; then
            print_step "Found templates in $OFFLINE_DIR"
            read -p "Copy templates to media folder? [y/N]: " copy_choice

            if [ "$copy_choice" = "y" ] || [ "$copy_choice" = "Y" ]; then
                cp "$OFFLINE_DIR"/*.docx "$MEDIA_DIR/"
                print_success "Templates copied to $MEDIA_DIR"
            fi
        fi

        print_success "Setup complete!"
        echo ""
        echo "Next steps:"
        echo "1. Run: python manage.py runserver 0.0.0.0:8000"
        echo "2. Access admin: http://your-ip:8000/admin"
        echo "3. Upload templates via Django Admin"
        ;;

    2)
        # ========================================
        # GIẢI PHÁP 2: Link tới Folder Offline
        # ========================================
        print_step "GIẢI PHÁP 2: Link tới Folder Offline"

        # Ask for offline directory path
        read -p "Đường dẫn folder maubieumoi [$OFFLINE_DIR]: " user_offline_dir
        if [ -n "$user_offline_dir" ]; then
            OFFLINE_DIR="$user_offline_dir"
        fi

        # Create offline directory if not exists
        if [ ! -d "$OFFLINE_DIR" ]; then
            print_step "Creating offline directory..."
            mkdir -p "$OFFLINE_DIR"
            print_success "Created: $OFFLINE_DIR"

            print_warning "Please copy your .docx templates to: $OFFLINE_DIR"
        else
            print_success "Offline directory exists: $OFFLINE_DIR"

            # Count templates
            template_count=$(find "$OFFLINE_DIR" -name "*.docx" -type f | wc -l)
            print_success "Found $template_count template files"
        fi

        # Create media parent directory
        mkdir -p "$(dirname "$MEDIA_DIR")"

        # Remove existing symlink/folder if exists
        if [ -L "$MEDIA_DIR" ] || [ -d "$MEDIA_DIR" ]; then
            print_warning "Removing existing $MEDIA_DIR"
            rm -rf "$MEDIA_DIR"
        fi

        # Create symbolic link
        print_step "Creating symbolic link..."
        ln -sf "$OFFLINE_DIR" "$MEDIA_DIR"
        print_success "Linked: $MEDIA_DIR → $OFFLINE_DIR"

        # Verify link
        if [ -L "$MEDIA_DIR" ]; then
            print_success "Symbolic link created successfully"
            ls -la "$MEDIA_DIR"
        else
            print_error "Failed to create symbolic link"
            exit 1
        fi

        # Set permissions
        chmod -R 755 "$OFFLINE_DIR"

        print_success "Setup complete!"
        echo ""
        echo "⚠️  IMPORTANT:"
        echo "   - Nếu $OFFLINE_DIR bị xóa/mất kết nối → Hệ thống sẽ lỗi"
        echo "   - Nên dùng Giải pháp 3 (Hybrid) để có fallback"
        ;;

    3)
        # ========================================
        # GIẢI PHÁP 3: Hybrid - Fallback Mechanism
        # ========================================
        print_step "GIẢI PHÁP 3: Hybrid - Fallback Mechanism"

        # Ask for offline directory path
        read -p "Đường dẫn folder maubieumoi [$OFFLINE_DIR]: " user_offline_dir
        if [ -n "$user_offline_dir" ]; then
            OFFLINE_DIR="$user_offline_dir"
        fi

        # Create offline directory if not exists
        if [ ! -d "$OFFLINE_DIR" ]; then
            print_step "Creating offline directory..."
            mkdir -p "$OFFLINE_DIR"
            print_success "Created: $OFFLINE_DIR"

            print_warning "Please copy your .docx templates to: $OFFLINE_DIR"
        else
            print_success "Offline directory exists: $OFFLINE_DIR"
        fi

        # Create media directory
        mkdir -p "$MEDIA_DIR"
        print_success "Created media directory: $MEDIA_DIR"

        # Update settings.py
        print_step "Updating settings.py..."

        SETTINGS_FILE="$PROJECT_DIR/wordgen/settings.py"

        # Check if already configured
        if grep -q "OFFLINE_TEMPLATE_PATH" "$SETTINGS_FILE"; then
            print_warning "Settings already configured, skipping..."
        else
            # Add configuration
            cat >> "$SETTINGS_FILE" << EOF

# Template Storage Configuration (Auto-added by setup_templates.sh)
OFFLINE_TEMPLATE_PATH = '$OFFLINE_DIR'
TEMPLATE_AUTO_CACHE = True  # Auto-copy từ offline sang media để cache
EOF
            print_success "Settings.py updated"
        fi

        # Update models.py
        print_step "Updating models.py..."

        MODELS_FILE="$PROJECT_DIR/templates_app/models.py"

        # Check if already using HybridTemplateStorage
        if grep -q "HybridTemplateStorage" "$MODELS_FILE"; then
            print_warning "Models.py already configured, skipping..."
        else
            print_warning "Manual step required:"
            echo ""
            echo "Edit file: $MODELS_FILE"
            echo "Find line ~142: file = models.FileField(...)"
            echo ""
            echo "Replace with:"
            echo "──────────────────────────────────────────────────"
            echo "from .storage import HybridTemplateStorage"
            echo ""
            echo "file = models.FileField("
            echo "    upload_to='templates/docx/',"
            echo "    storage=HybridTemplateStorage(),"
            echo "    validators=[FileExtensionValidator(allowed_extensions=['docx'])],"
            echo "    verbose_name=\"File Word (.docx)\""
            echo ")"
            echo "──────────────────────────────────────────────────"
            echo ""
            read -p "Press Enter after you've made the changes..."
        fi

        # Migrate
        print_step "Migrating database..."
        cd "$PROJECT_DIR"

        if python manage.py makemigrations && python manage.py migrate; then
            print_success "Database migrated successfully"
        else
            print_warning "Migration may have failed, but continuing..."
        fi

        # Set permissions
        chmod -R 755 "$OFFLINE_DIR"
        chmod -R 755 "$PROJECT_DIR/media"

        print_success "Setup complete!"
        echo ""
        echo "How it works:"
        echo "  1. System reads from $OFFLINE_DIR first"
        echo "  2. If not found → reads from $MEDIA_DIR (cache)"
        echo "  3. Auto-cache from offline to media for performance"
        echo ""
        echo "Next: Restart Django server"
        ;;

    4)
        # ========================================
        # Validate Templates
        # ========================================
        print_step "Validating Templates"

        # Check which directory to scan
        if [ -d "$OFFLINE_DIR" ]; then
            SCAN_DIR="$OFFLINE_DIR"
        elif [ -d "$MEDIA_DIR" ]; then
            SCAN_DIR="$MEDIA_DIR"
        else
            print_error "No template directory found"
            exit 1
        fi

        print_step "Scanning: $SCAN_DIR"

        # Run validation script
        if [ -f "$PROJECT_DIR/validate_templates.py" ]; then
            python3 "$PROJECT_DIR/validate_templates.py" "$SCAN_DIR"
        else
            print_error "validate_templates.py not found"
            exit 1
        fi
        ;;

    0)
        echo "Exiting..."
        exit 0
        ;;

    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo ""
print_success "All done! 🎉"

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import User, Profile, APIToken

# Hide User and Profile models from admin - only show API tokens


@admin.register(APIToken)
class APITokenAdmin(admin.ModelAdmin):
    """Admin configuration for API Token model - simplified for admin use."""
    
    list_display = ('name', 'user', 'token_length', 'is_active', 'expires_at', 'last_used', 'created_at','short_token', 'copy_token_button')
    list_filter = ('is_active', 'expires_at', 'created_at')
    search_fields = ('user__username', 'user__email', 'name')
    readonly_fields = ('copy_token_button', 'created_at', 'updated_at', 'last_used')
    
    fieldsets = (
        (_('Token Configuration'), {
            'fields': ('user', 'name', 'token_length', 'is_active', 'expires_at'),
            'description': 'Configure API token settings. Token will be auto-generated.'
        }),
        (_('Generated Token'), {
            'fields': ('copy_token_button', 'last_used'),
            'classes': ('collapse',),
            'description': 'Auto-generated JWT token for API access.'
        }),
        (_('API Permissions'), {
            'fields': ('can_read_products', 'can_manage_cart', 'can_place_orders', 'can_manage_wishlist'),
            'classes': ('collapse',),
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def short_token(self, obj):
        """Show shortened token in list view."""
        return obj.token[:10] + "..." if obj.token else "-"
    short_token.short_description = "Token Preview"
    
    def copy_token_button(self, obj):
        """Custom readonly field with copy-to-clipboard button."""
        if not obj.token:
            return "-"
        return format_html(
        '''
        <div style="display:flex; align-items:center; gap:8px; max-width:100%;">
            <input 
                type="text" 
                id="token-{id}" 
                value="{token}" 
                readonly 
                style="flex:1; padding:6px 10px; border:1px solid #ccc; border-radius:6px; font-size:13px; background:#f9f9f9; color:#333;" 
            />
            <button 
                type="button" 
                onclick="copyToClipboard('token-{id}')" 
                style="padding:6px 12px; border:none; border-radius:6px; background:#0d6efd; color:white; font-size:13px; cursor:pointer; transition:background 0.3s;"
                onmouseover="this.style.background='#0b5ed7'" 
                onmouseout="this.style.background='#0d6efd'"
            >
                📋 Copy
            </button>
        </div>
        <script>
        function copyToClipboard(elementId) {{
            var copyText = document.getElementById(elementId);
            copyText.select();
            copyText.setSelectionRange(0, 99999); 
            document.execCommand("copy");
            
            // Show a toast message
            var msg = document.createElement("div");
            msg.innerText = "Token copied!";
            msg.style.position = "fixed";
            msg.style.bottom = "20px";
            msg.style.right = "20px";
            msg.style.background = "#198754";
            msg.style.color = "white";
            msg.style.padding = "8px 14px";
            msg.style.borderRadius = "6px";
            msg.style.boxShadow = "0 2px 6px rgba(0,0,0,0.2)";
            msg.style.zIndex = "9999";
            document.body.appendChild(msg);
            setTimeout(() => msg.remove(), 2000);
        }}
        </script>
        ''',
        id=obj.id,
        token=obj.token
    )
    copy_token_button.short_description = "Token"

    
    def save_model(self, request, obj, form, change):
        """Handle JWT token generation on save."""
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

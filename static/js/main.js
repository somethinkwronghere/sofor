// Görev Takip Sistemi - Main JavaScript

(function($) {
    'use strict';

    // Document Ready
    $(document).ready(function() {
        // Initialize tooltips
        initTooltips();
        
        // Initialize popovers
        initPopovers();
        
        // Auto-hide alerts
        autoHideAlerts();
        
        // Confirm delete actions
        confirmDelete();
        
        // Form validation
        formValidation();
        
        // Date/Time pickers
        initDateTimePickers();
        
        // Table search and filter
        initTableSearch();
        
        // Sidebar collapse state
        saveSidebarState();
        
        // Mesai calculation
        initMesaiCalculation();
        
        // Izin calculation
        initIzinCalculation();
        
        // Plaka validation
        initPlakaValidation();
        
        // Delete confirmation modals
        initDeleteModals();
    });

    // Initialize Bootstrap Tooltips
    function initTooltips() {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize Bootstrap Popovers
    function initPopovers() {
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    // Auto-hide success alerts after 5 seconds
    function autoHideAlerts() {
        $('.alert-success').delay(5000).fadeOut('slow', function() {
            $(this).remove();
        });
    }

    // Confirm delete actions
    function confirmDelete() {
        $('a[data-confirm], button[data-confirm]').on('click', function(e) {
            var message = $(this).data('confirm') || 'Bu işlemi gerçekleştirmek istediğinizden emin misiniz?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    }

    // Form validation
    function formValidation() {
        // Bootstrap form validation
        var forms = document.querySelectorAll('.needs-validation');
        Array.prototype.slice.call(forms).forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });

        // Custom date validation for all date/datetime inputs
        $('input[type="datetime-local"], input[type="date"]').on('change', function() {
            validateDateRange();
        });
        
        // Real-time validation for text inputs
        $('input[type="text"], input[type="email"]').on('blur', function() {
            var $input = $(this);
            var value = $input.val().trim();
            
            // Check required fields
            if ($input.prop('required') && !value) {
                $input.addClass('is-invalid');
                showFieldError($input, 'Bu alan zorunludur.');
            } else {
                $input.removeClass('is-invalid');
                removeFieldError($input);
            }
        });
        
        // Email validation
        $('input[type="email"]').on('blur', function() {
            var $input = $(this);
            var email = $input.val().trim();
            var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                $input.addClass('is-invalid');
                showFieldError($input, 'Geçerli bir e-posta adresi giriniz.');
            }
        });
        
        // Password match validation
        $('input[name="sifre_tekrar"], input[name="yeni_sifre_tekrar"]').on('keyup', function() {
            var password = $('input[name="sifre"], input[name="yeni_sifre"]').val();
            var confirmPassword = $(this).val();
            
            if (confirmPassword && password !== confirmPassword) {
                $(this).addClass('is-invalid');
                showFieldError($(this), 'Şifreler eşleşmiyor.');
            } else {
                $(this).removeClass('is-invalid');
                removeFieldError($(this));
            }
        });
    }
    
    // Validate date range
    function validateDateRange() {
        var startDate = $('input[name="bstarih"]').val();
        var endDate = $('input[name="bttarih"]').val();
        var $endInput = $('input[name="bttarih"]');
        
        if (startDate && endDate) {
            var start = new Date(startDate);
            var end = new Date(endDate);
            
            if (end <= start) {
                $endInput.addClass('is-invalid');
                showFieldError($endInput, 'Bitiş tarihi başlangıç tarihinden sonra olmalıdır.');
                return false;
            } else {
                $endInput.removeClass('is-invalid');
                removeFieldError($endInput);
                return true;
            }
        }
        return true;
    }
    
    // Show field error
    function showFieldError($input, message) {
        var $feedback = $input.siblings('.invalid-feedback');
        if ($feedback.length === 0) {
            $input.after('<div class="invalid-feedback">' + message + '</div>');
        } else {
            $feedback.text(message);
        }
    }
    
    // Remove field error
    function removeFieldError($input) {
        $input.siblings('.invalid-feedback').remove();
    }

    // Initialize Date/Time pickers
    function initDateTimePickers() {
        // Set min date to today for future date inputs
        $('input[type="date"], input[type="datetime-local"]').each(function() {
            if ($(this).hasClass('future-only')) {
                var today = new Date().toISOString().split('T')[0];
                $(this).attr('min', today);
            }
        });
    }

    // Table search functionality
    function initTableSearch() {
        $('#tableSearch').on('keyup', function() {
            var value = $(this).val().toLowerCase();
            $('#dataTable tbody tr').filter(function() {
                $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
            });
        });
    }

    // Save sidebar collapse state
    function saveSidebarState() {
        $('.sidebar .collapse').on('shown.bs.collapse', function() {
            var id = $(this).attr('id');
            localStorage.setItem('sidebar_' + id, 'open');
        });

        $('.sidebar .collapse').on('hidden.bs.collapse', function() {
            var id = $(this).attr('id');
            localStorage.setItem('sidebar_' + id, 'closed');
        });

        // Restore sidebar state
        $('.sidebar .collapse').each(function() {
            var id = $(this).attr('id');
            var state = localStorage.getItem('sidebar_' + id);
            if (state === 'open') {
                $(this).addClass('show');
            }
        });
    }

    // Loading spinner
    window.showLoading = function() {
        var spinner = '<div class="spinner-overlay"><div class="spinner-border text-light" role="status"><span class="visually-hidden">Yükleniyor...</span></div></div>';
        $('body').append(spinner);
    };

    window.hideLoading = function() {
        $('.spinner-overlay').remove();
    };

    // AJAX form submission helper
    window.submitFormAjax = function(formId, successCallback) {
        $(formId).on('submit', function(e) {
            e.preventDefault();
            
            var form = $(this);
            var url = form.attr('action');
            var method = form.attr('method') || 'POST';
            var formData = new FormData(this);
            
            showLoading();
            
            $.ajax({
                url: url,
                type: method,
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    hideLoading();
                    if (successCallback) {
                        successCallback(response);
                    }
                },
                error: function(xhr, status, error) {
                    hideLoading();
                    alert('Bir hata oluştu: ' + error);
                }
            });
        });
    };

    // Format date helper
    window.formatDate = function(dateString) {
        var date = new Date(dateString);
        var day = String(date.getDate()).padStart(2, '0');
        var month = String(date.getMonth() + 1).padStart(2, '0');
        var year = date.getFullYear();
        var hours = String(date.getHours()).padStart(2, '0');
        var minutes = String(date.getMinutes()).padStart(2, '0');
        
        return day + '.' + month + '.' + year + ' ' + hours + ':' + minutes;
    };

    // Print page helper
    window.printPage = function() {
        window.print();
    };

    // Export table to CSV
    window.exportTableToCSV = function(tableId, filename) {
        var csv = [];
        var rows = document.querySelectorAll(tableId + ' tr');
        
        for (var i = 0; i < rows.length; i++) {
            var row = [], cols = rows[i].querySelectorAll('td, th');
            
            for (var j = 0; j < cols.length; j++) {
                row.push(cols[j].innerText);
            }
            
            csv.push(row.join(','));
        }
        
        downloadCSV(csv.join('\n'), filename);
    };

    function downloadCSV(csv, filename) {
        var csvFile;
        var downloadLink;
        
        csvFile = new Blob([csv], {type: 'text/csv'});
        downloadLink = document.createElement('a');
        downloadLink.download = filename;
        downloadLink.href = window.URL.createObjectURL(csvFile);
        downloadLink.style.display = 'none';
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    }

    // Notification helper
    window.showNotification = function(message, type) {
        type = type || 'info';
        var alertClass = 'alert-' + type;
        var iconClass = '';
        
        switch(type) {
            case 'success':
                iconClass = 'bi-check-circle-fill';
                break;
            case 'error':
            case 'danger':
                iconClass = 'bi-exclamation-triangle-fill';
                break;
            case 'warning':
                iconClass = 'bi-exclamation-circle-fill';
                break;
            default:
                iconClass = 'bi-info-circle-fill';
        }
        
        var alert = '<div class="alert ' + alertClass + ' alert-dismissible fade show" role="alert">' +
                    '<i class="bi ' + iconClass + ' me-2"></i>' + message +
                    '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
                    '</div>';
        
        $('.messages-container').html(alert);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            $('.alert').fadeOut('slow', function() {
                $(this).remove();
            });
        }, 5000);
    };

    // Confirm modal helper
    window.confirmModal = function(title, message, confirmCallback) {
        var modalHtml = '<div class="modal fade" id="confirmModal" tabindex="-1">' +
                        '<div class="modal-dialog">' +
                        '<div class="modal-content">' +
                        '<div class="modal-header">' +
                        '<h5 class="modal-title">' + title + '</h5>' +
                        '<button type="button" class="btn-close" data-bs-dismiss="modal"></button>' +
                        '</div>' +
                        '<div class="modal-body">' + message + '</div>' +
                        '<div class="modal-footer">' +
                        '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">İptal</button>' +
                        '<button type="button" class="btn btn-primary" id="confirmBtn">Onayla</button>' +
                        '</div>' +
                        '</div>' +
                        '</div>' +
                        '</div>';
        
        $('body').append(modalHtml);
        var modal = new bootstrap.Modal(document.getElementById('confirmModal'));
        modal.show();
        
        $('#confirmBtn').on('click', function() {
            modal.hide();
            if (confirmCallback) {
                confirmCallback();
            }
            $('#confirmModal').remove();
        });
        
        $('#confirmModal').on('hidden.bs.collapse', function() {
            $(this).remove();
        });
    };
    
    // Mesai calculation
    function initMesaiCalculation() {
        var $bstarih = $('input[name="bstarih"]');
        var $bttarih = $('input[name="bttarih"]');
        var $mesai = $('input[name="mesai"]');
        
        // Only run on mesai forms
        if ($bstarih.length && $bttarih.length && $mesai.length) {
            $bstarih.add($bttarih).on('change', function() {
                calculateMesai();
            });
        }
    }
    
    function calculateMesai() {
        var startDate = $('input[name="bstarih"]').val();
        var endDate = $('input[name="bttarih"]').val();
        var $mesaiInput = $('input[name="mesai"]');
        var $pazargunuCheckbox = $('input[name="pazargunu"]');
        
        if (startDate && endDate) {
            var start = new Date(startDate);
            var end = new Date(endDate);
            
            if (end > start) {
                // Calculate hours
                var diff = end - start;
                var hours = diff / (1000 * 60 * 60);
                
                // Update mesai field
                $mesaiInput.val(hours.toFixed(2));
                
                // Check if it's Sunday (0 = Sunday)
                if (start.getDay() === 0 && $pazargunuCheckbox.length) {
                    $pazargunuCheckbox.prop('checked', true);
                }
                
                // Validate max 24 hours
                if (hours > 24) {
                    showFieldError($('input[name="bttarih"]'), 'Mesai süresi 24 saatten fazla olamaz.');
                }
            }
        }
    }
    
    // Izin calculation
    function initIzinCalculation() {
        var $bstarih = $('input[name="bstarih"]');
        var $bttarih = $('input[name="bttarih"]');
        var $gun = $('input[name="gun"]');
        
        // Only run on izin forms
        if ($bstarih.length && $bttarih.length && $gun.length) {
            $bstarih.add($bttarih).on('change', function() {
                calculateIzinDays();
            });
        }
    }
    
    function calculateIzinDays() {
        var startDate = $('input[name="bstarih"]').val();
        var endDate = $('input[name="bttarih"]').val();
        var $gunInput = $('input[name="gun"]');
        
        if (startDate && endDate) {
            var start = new Date(startDate);
            var end = new Date(endDate);
            
            if (end >= start) {
                // Calculate days (inclusive)
                var diff = end - start;
                var days = Math.floor(diff / (1000 * 60 * 60 * 24)) + 1;
                
                // Update gun field if empty
                if (!$gunInput.val() || $gunInput.val() == '0') {
                    $gunInput.val(days);
                }
            }
        }
    }
    
    // Plaka validation
    function initPlakaValidation() {
        $('input[name="plaka"]').on('blur', function() {
            var $input = $(this);
            var plaka = $input.val().trim().toUpperCase();
            
            if (plaka) {
                // Turkish plate format: 2 digits + 1-3 letters + 1-4 digits
                var plakaRegex = /^[0-9]{2}\s?[A-Z]{1,3}\s?[0-9]{1,4}$/;
                
                if (!plakaRegex.test(plaka)) {
                    $input.addClass('is-invalid');
                    showFieldError($input, 'Geçerli bir Türkiye plakası giriniz (örn: 34 ABC 123)');
                } else {
                    $input.removeClass('is-invalid');
                    removeFieldError($input);
                    // Format the plate
                    $input.val(plaka);
                }
            }
        });
    }
    
    // Delete confirmation modals
    function initDeleteModals() {
        // Handle delete buttons with modal
        $('button[data-delete-url], a[data-delete-url]').on('click', function(e) {
            e.preventDefault();
            
            var $btn = $(this);
            var deleteUrl = $btn.data('delete-url');
            var itemName = $btn.data('item-name') || 'bu kaydı';
            var itemType = $btn.data('item-type') || 'kayıt';
            
            showDeleteModal(itemName, itemType, function() {
                // Create a form and submit
                var form = $('<form>', {
                    'method': 'POST',
                    'action': deleteUrl
                });
                
                // Add CSRF token
                var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
                form.append($('<input>', {
                    'type': 'hidden',
                    'name': 'csrfmiddlewaretoken',
                    'value': csrfToken
                }));
                
                $('body').append(form);
                form.submit();
            });
        });
    }
    
    // Show delete confirmation modal
    function showDeleteModal(itemName, itemType, confirmCallback) {
        var modalHtml = '<div class="modal fade" id="deleteModal" tabindex="-1">' +
                        '<div class="modal-dialog">' +
                        '<div class="modal-content">' +
                        '<div class="modal-header bg-danger text-white">' +
                        '<h5 class="modal-title"><i class="bi bi-exclamation-triangle-fill me-2"></i>Silme Onayı</h5>' +
                        '<button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>' +
                        '</div>' +
                        '<div class="modal-body">' +
                        '<p class="mb-0"><strong>' + itemName + '</strong> ' + itemType + 'ini silmek istediğinizden emin misiniz?</p>' +
                        '<p class="text-muted mt-2 mb-0"><small>Bu işlem geri alınamaz.</small></p>' +
                        '</div>' +
                        '<div class="modal-footer">' +
                        '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">İptal</button>' +
                        '<button type="button" class="btn btn-danger" id="confirmDeleteBtn">' +
                        '<i class="bi bi-trash me-1"></i>Sil</button>' +
                        '</div>' +
                        '</div>' +
                        '</div>' +
                        '</div>';
        
        // Remove existing modal if any
        $('#deleteModal').remove();
        
        $('body').append(modalHtml);
        var modal = new bootstrap.Modal(document.getElementById('deleteModal'));
        modal.show();
        
        $('#confirmDeleteBtn').on('click', function() {
            modal.hide();
            if (confirmCallback) {
                confirmCallback();
            }
            setTimeout(function() {
                $('#deleteModal').remove();
            }, 500);
        });
        
        $('#deleteModal').on('hidden.bs.modal', function() {
            $(this).remove();
        });
    }
    
    // Table sorting
    window.initTableSorting = function(tableId) {
        $(tableId + ' th[data-sortable]').css('cursor', 'pointer').on('click', function() {
            var $th = $(this);
            var column = $th.index();
            var $table = $th.closest('table');
            var $tbody = $table.find('tbody');
            var rows = $tbody.find('tr').toArray();
            var isAsc = $th.hasClass('sort-asc');
            
            // Remove sort classes from all headers
            $table.find('th').removeClass('sort-asc sort-desc');
            
            // Sort rows
            rows.sort(function(a, b) {
                var aVal = $(a).find('td').eq(column).text();
                var bVal = $(b).find('td').eq(column).text();
                
                // Try to parse as number
                var aNum = parseFloat(aVal);
                var bNum = parseFloat(bVal);
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAsc ? bNum - aNum : aNum - bNum;
                } else {
                    return isAsc ? bVal.localeCompare(aVal, 'tr') : aVal.localeCompare(bVal, 'tr');
                }
            });
            
            // Update table
            $.each(rows, function(index, row) {
                $tbody.append(row);
            });
            
            // Update sort class
            $th.addClass(isAsc ? 'sort-desc' : 'sort-asc');
        });
    };
    
    // Pagination helper
    window.initPagination = function(itemsPerPage) {
        itemsPerPage = itemsPerPage || 25;
        var $table = $('#dataTable');
        var $rows = $table.find('tbody tr');
        var totalRows = $rows.length;
        var totalPages = Math.ceil(totalRows / itemsPerPage);
        var currentPage = 1;
        
        if (totalPages <= 1) return;
        
        // Create pagination controls
        var paginationHtml = '<nav aria-label="Sayfa navigasyonu"><ul class="pagination justify-content-center" id="pagination"></ul></nav>';
        $table.after(paginationHtml);
        
        function showPage(page) {
            currentPage = page;
            var start = (page - 1) * itemsPerPage;
            var end = start + itemsPerPage;
            
            $rows.hide().slice(start, end).show();
            updatePaginationControls();
        }
        
        function updatePaginationControls() {
            var $pagination = $('#pagination');
            $pagination.empty();
            
            // Previous button
            $pagination.append('<li class="page-item ' + (currentPage === 1 ? 'disabled' : '') + '">' +
                             '<a class="page-link" href="#" data-page="' + (currentPage - 1) + '">Önceki</a></li>');
            
            // Page numbers
            for (var i = 1; i <= totalPages; i++) {
                if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                    $pagination.append('<li class="page-item ' + (i === currentPage ? 'active' : '') + '">' +
                                     '<a class="page-link" href="#" data-page="' + i + '">' + i + '</a></li>');
                } else if (i === currentPage - 3 || i === currentPage + 3) {
                    $pagination.append('<li class="page-item disabled"><span class="page-link">...</span></li>');
                }
            }
            
            // Next button
            $pagination.append('<li class="page-item ' + (currentPage === totalPages ? 'disabled' : '') + '">' +
                             '<a class="page-link" href="#" data-page="' + (currentPage + 1) + '">Sonraki</a></li>');
            
            // Bind click events
            $pagination.find('a').on('click', function(e) {
                e.preventDefault();
                var page = parseInt($(this).data('page'));
                if (page >= 1 && page <= totalPages) {
                    showPage(page);
                }
            });
        }
        
        // Show first page
        showPage(1);
    };

})(jQuery);

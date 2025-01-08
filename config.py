VFS_URL = "https://visa.vfsglobal.com/tur/tr/pol/login"
CHECK_INTERVAL = 300  # 5 dakika (saniye cinsinden)

# Doldurulacak form alanları için seçiciler
SELECTORS = {
    'appointment_center': '#center',
    'appointment_category': '#category',
    'appointment_subcategory': '#subcategory',
    'date_picker': '#datepicker',
    'submit_button': '#submit-button'
}

# Form için varsayılan değerler
FORM_VALUES = {
    'center': 'ANKARA',
    'category': 'NATIONAL VISA',
    'subcategory': 'WORK'
}

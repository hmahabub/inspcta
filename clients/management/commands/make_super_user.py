from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='inspcta_erp_admin').exists():
    User.objects.create_superuser('inspcta_erp_admin', 'hm.sayem.14@gmail.com', 'adminpass23')

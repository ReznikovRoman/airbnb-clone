from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0007_auto_20210503_1716'),
    ]

    sql = """
    CREATE OR REPLACE VIEW realty_view AS
        SELECT
            r.id,
            r.name, r.description, r.is_available, r.realty_type, r.beds_count, r.max_guests_count, r.price_per_night,
            l.country, l.city, l.street,
            u.email, u.first_name, u.last_name
        FROM realty_realty AS r
        LEFT JOIN addresses_address AS l
            ON r.location_id = l.id
        LEFT JOIN hosts_realtyhost AS h
            ON r.host_id = h.id
        LEFT JOIN accounts_customuser AS u
            ON h.user_id = u.id
        ORDER BY r.id
    """

    operations = [
        migrations.RunSQL('DROP VIEW IF EXISTS realty_view;'),
        migrations.RunSQL(sql),
    ]

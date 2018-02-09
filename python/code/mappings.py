from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError

maxmind_country = Reader('../../home/app/data/GeoLite2-Country.mmdb')
maxmind_asn = Reader('../../home/app/data/GeoLite2-ASN.mmdb')


def get_country(ip):
    try:
        return maxmind_country.country(ip).country.iso_code
    except AddressNotFoundError:
        return None
    except ValueError:
        return None


def get_asn(ip):
    try:
        return maxmind_asn.asn(ip).autonomous_system_number
    except AddressNotFoundError:
        return None
    except ValueError:
        return None

from app.vpn_key.config import client_vpn

def gb_to_bytes(gb: float):
    bytes_in_gb = 1024 ** 3 # 1gb = 1024^3
    return int(gb * bytes_in_gb)

def get_keys():
    return client_vpn.get_keys()    

# vpn_keys = get_keys()
# for key_id in vpn_keys:
#     print(key_id)

# Получить конкертный ключ по его айди
def get_key_id(key_id: str):
    return client_vpn.get_key(key_id)

# Создать новый ключ
def create_new_key(key_id: str = None, name: str = None, data_limit_gb: float = None):
    return client_vpn.create_key(key_id=key_id, name=name, data_limit=gb_to_bytes(data_limit_gb))

# Переименовать ключ
def rename_key(key_id: str, new_name: str):
    return client_vpn.rename_key(key_id, new_name)

# Изменить лимит по трафику
def update_limit(key_id: str, data_limit_gb: float):
    return client_vpn.add_data_limit(key_id, gb_to_bytes(data_limit_gb))

# Удалить лимит по трафику
def delete_limit(key_id: str):
    return client_vpn.delete_data_limit(key_id)

# Удалить ключ
def delete_key(key_id: str):
    return client_vpn.delete_key(key_id)

#delete = delete_key('12')

#status_limit = delete_limit('12')

# key_info = get_key_id("1")
# print(f"key_id: {key_info.access_url}")

# new_key = create_new_key(name='test_delete_limit', data_limit_gb=1.5)
# status_rename = rename_key('12', 'update_name')
# status_update = update_limit('12', 6)
# new_key = get_key_id(20)
# print(new_key.key_id, new_key.access_url)
# delete_limit(new_key.key_id)
# key_16 = get_key_id(16)
# print(key_16.access_url)



from datetime import timedelta

from faker import Faker

fake = Faker('zh_CN')

def rdm_future_date_time(end_data):
    end_date = int(end_data)
    return str(fake.future_datetime(end_date=timedelta(end_date)))



if __name__ == '__main__':
    print(rdm_future_date_time(end_data=10),type(rdm_future_date_time(end_data=10)))